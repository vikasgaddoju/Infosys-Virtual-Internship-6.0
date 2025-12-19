from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Max, Min, Sum, Count
from django.db.models.functions import Coalesce
from .models import Category, SubCategory, QuizAttempt
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from .models import QuizAttempt
from django.views.decorators.http import require_POST
import json

# ============================================================
# USER DASHBOARD
# ============================================================
@login_required
def dashboard(request):
    user = request.user

    # Base queryset: only completed quizzes
    completed_qs = QuizAttempt.objects.filter(
        user=user,
        status=QuizAttempt.STATUS_COMPLETED
    )

    total_attempted = QuizAttempt.objects.filter(user=user).count()
    total_completed = completed_qs.count()

    completion_rate = (
        (total_completed / total_attempted) * 100
        if total_attempted > 0 else 0
    )

    score_stats = completed_qs.aggregate(
        avg_score=Coalesce(Avg('score'), 0.0),
        best_score=Coalesce(Max('score'), 0.0),
        worst_score=Coalesce(Min('score'), 0.0),
    )

    difficulty_stats = completed_qs.values('difficulty').annotate(
        quizzes=Count('id'),
        avg_score=Avg('score')
    ).order_by('difficulty')

    category_stats = completed_qs.values(
        'category__name'
    ).annotate(
        quizzes=Count('id'),
        avg_score=Avg('score')
    ).order_by('-avg_score')

    recent_quizzes = completed_qs.select_related(
        'category', 'subcategory'
    ).order_by('-completed_at')[:10]

    last_7_days = completed_qs.filter(
        completed_at__gte=timezone.now() - timedelta(days=7)
    ).count()

    context = {
        "total_attempted": total_attempted,
        "total_completed": total_completed,
        "completion_rate": round(completion_rate, 2),

        "avg_score": round(score_stats["avg_score"], 2),
        "best_score": score_stats["best_score"],
        "worst_score": score_stats["worst_score"],

        "difficulty_stats": difficulty_stats,
        "category_stats": category_stats,
        "recent_quizzes": recent_quizzes,

        "last_7_days": last_7_days,
    }
    return render(request, "quizzes/dashboard.html", context)


# ============================================================
# STEP 1 — SHOW ALL MAIN CATEGORIES (e.g. Academic, GK, Ent)
# ============================================================
def category_list(request):
    """
    Show top-level Category rows (Academic, Entertainment, General Knowledge).
    From here user selects a main category — then we show its level=1 subcategories.
    """
    categories = Category.objects.all()
    return render(request, "quizzes/category_list.html", {
        "categories": categories,
        "debug_count": categories.count(),
    })


# ============================================================
# STEP 2 — SHOW LEVEL-1 SUBCATEGORIES FOR A GIVEN CATEGORY
# ============================================================
def choose_subcategory(request, category_id):
    """
    Given a Category (e.g. Academic), show only its level=1 subcategories:
    i.e. SubCategory.objects.filter(category=category, parent_subcat__isnull=True)
    """
    category = get_object_or_404(Category, id=category_id)

    level1_subs = SubCategory.objects.filter(category=category, parent_subcat__isnull=True).order_by('name')

    return render(request, "quizzes/step_subcategories.html", {
        "category": category,
        "subcategories": level1_subs,
        "debug_count": level1_subs.count(),
    })


# ============================================================
# STEP 2b — SHOW CHILD SUBCATEGORIES FOR A SELECTED SUBCATEGORY
# ============================================================
def subcategory_children(request, sub_id):
    """
    When user clicks a SubCategory (e.g. Engineering), this view lists its children (CS, Civil...).
    If no children exist (i.e. it's a leaf), redirect to difficulty selection.
    """
    parent = get_object_or_404(SubCategory, id=sub_id)
    children = SubCategory.objects.filter(parent_subcat=parent).order_by('name')

    # If no children -> this is a leaf (or final node). Go to difficulty selection.
    if not children.exists():
        return redirect('quizzes:choose_difficulty', subcategory_id=parent.id)

    return render(request, "quizzes/child_subcategories.html", {
        "parent": parent,
        "children": children,
        "debug_count": children.count(),
    })


# ============================================================
# STEP 3 — CHOOSE DIFFICULTY (only for a chosen subcategory)
# ============================================================
def choose_difficulty(request, subcategory_id):
    """
    Show difficulty options for a chosen subcategory.
    (This view is reached either from a leaf-level subcategory, or from the children view.)
    """
    subcategory = get_object_or_404(SubCategory, id=subcategory_id)

    # If subcategory is not a leaf and has children, it's better UX to redirect
    # user to its children page so they pick the precise leaf.
    if not subcategory.is_leaf:
        # If it has children, redirect to children listing
        children = SubCategory.objects.filter(parent_subcat=subcategory)
        if children.exists():
            return redirect('quizzes:subcategory_children', sub_id=subcategory.id)

    return render(request, "quizzes/step_difficulty.html", {
        "subcategory": subcategory
    })


# ============================================================
# STEP 4 — INSTRUCTIONS BEFORE START
# ============================================================
def instructions(request, subcategory_id, difficulty):
    """
    Show user instructions, selected difficulty & start button.
    """
    subcategory = get_object_or_404(SubCategory, id=subcategory_id)

    # If the selected subcategory is not leaf, redirect user to children list to pick a leaf.
    if not subcategory.is_leaf:
        children = SubCategory.objects.filter(parent_subcat=subcategory)
        if children.exists():
            return redirect('quizzes:subcategory_children', sub_id=subcategory.id)

    return render(request, "quizzes/step_instructions.html", {
        "subcategory": subcategory,
        "difficulty": difficulty
    })


# ============================================================
# START QUIZ — only allowed for leaf nodes and logged-in users
# ============================================================
@login_required
def start_quiz(request, subcategory_id, difficulty):
    """
    Create quiz attempt and show loading page
    """
    subcategory = get_object_or_404(SubCategory, id=subcategory_id)
    
    # Safety: only leaf nodes should start a quiz
    if not subcategory.is_leaf:
        return redirect('quizzes:subcategory_children', sub_id=subcategory.id)
    
    # Create quiz attempt
    quiz_attempt = QuizAttempt.objects.create(
        user=request.user,
        category=subcategory.category,
        subcategory=subcategory,
        difficulty=difficulty,
        total_questions=10,
        status=QuizAttempt.STATUS_GENERATING
    )
    
    # Show loading page that will trigger AJAX to generate questions
    return render(request, "quizzes/generating_quiz.html", {
        "quiz_attempt": quiz_attempt,
        "subcategory": subcategory,
        "difficulty": difficulty,
    })


@login_required
@require_POST
def generate_questions(request, attempt_id):
    """
    AJAX endpoint to generate questions using AI
    """
    quiz_attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
    
    # Check if questions already generated
    if quiz_attempt.questions:
        return JsonResponse({
            'success': True,
            'redirect_url': f'/quiz/attempt/{quiz_attempt.id}/question/'
        })
    
    try:
        # Import here to avoid circular imports
        from .ai_service import generate_quiz_questions
        
        # Generate questions via AI
        questions_data = generate_quiz_questions(
            topic=quiz_attempt.subcategory.name,
            category=quiz_attempt.category.name,
            difficulty=quiz_attempt.difficulty,
            count=quiz_attempt.total_questions
        )
        
        # Format questions with IDs and empty user_answer fields
        formatted_questions = []
        for idx, q in enumerate(questions_data, start=1):
            formatted_questions.append({
                'id': idx,
                'question': q['question'],
                'option_a': q['option_a'],
                'option_b': q['option_b'],
                'option_c': q['option_c'],
                'option_d': q['option_d'],
                'correct_answer': q['correct_answer'],
                'explanation': q.get('explanation', ''),
                'user_answer': None,
                'is_correct': None
            })
        
        # Save questions to quiz attempt
        quiz_attempt.questions = formatted_questions
        quiz_attempt.status = QuizAttempt.STATUS_IN_PROGRESS
        quiz_attempt.ai_meta = {
            'model': 'gpt-3.5-turbo',
            'generated_at': timezone.now().isoformat(),
        }
        quiz_attempt.save()
        
        return JsonResponse({
            'success': True,
            'redirect_url': f'/quiz/attempt/{quiz_attempt.id}/question/'
        })
        
    except Exception as e:
        quiz_attempt.status = QuizAttempt.STATUS_ABANDONED
        quiz_attempt.save()
        
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def show_question(request, attempt_id):
    """
    Show current question in the quiz
    """
    quiz_attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
    
    # Check if quiz is completed
    if quiz_attempt.status == QuizAttempt.STATUS_COMPLETED:
        return redirect('quizzes:quiz_results', attempt_id=quiz_attempt.id)
    
    # Get current question
    current_question = quiz_attempt.get_current_question()
    
    if not current_question:
        return redirect('quizzes:quiz_results', attempt_id=quiz_attempt.id)
    
    # Calculate progress
    answered_count = sum(1 for q in quiz_attempt.questions if q.get('user_answer') is not None)
    
    return render(request, "quizzes/quiz_question.html", {
        "quiz_attempt": quiz_attempt,
        "question": current_question,
        "question_number": quiz_attempt.current_question_index + 1,
        "total_questions": quiz_attempt.total_questions,
        "answered_count": answered_count,
    })


@login_required
@require_POST
def submit_answer(request, attempt_id):
    """
    Submit answer for current question
    """
    quiz_attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
    
    # Get user's answer
    user_answer = request.POST.get('answer', '').upper()
    
    if user_answer not in ['A', 'B', 'C', 'D']:
        return JsonResponse({'error': 'Invalid answer'}, status=400)
    
    # Get current question
    current_idx = quiz_attempt.current_question_index
    
    if current_idx >= len(quiz_attempt.questions):
        return JsonResponse({'error': 'No more questions'}, status=400)
    
    # Update question with user's answer
    quiz_attempt.questions[current_idx]['user_answer'] = user_answer
    quiz_attempt.questions[current_idx]['is_correct'] = (
        user_answer == quiz_attempt.questions[current_idx]['correct_answer']
    )
    
    # Move to next question
    quiz_attempt.current_question_index += 1
    quiz_attempt.save()
    
    # Check if quiz is complete
    if quiz_attempt.is_quiz_complete():
        finalize_quiz_attempt(quiz_attempt)

        return JsonResponse({
            'success': True,
            'completed': True,
            'redirect_url': f'/quiz/attempt/{quiz_attempt.id}/results/'
        })

    
    return JsonResponse({
        'success': True,
        'completed': False,
        'redirect_url': f'/quiz/attempt/{quiz_attempt.id}/question/'
    })

@login_required
def quiz_results(request, attempt_id):
    """
    Show quiz results with score and review
    """
    quiz_attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
    
    # Calculate results
    total = len(quiz_attempt.questions) if quiz_attempt.questions else 0
    correct = sum(1 for q in quiz_attempt.questions if q.get('is_correct')) if quiz_attempt.questions else 0
    incorrect = total - correct
    percentage = quiz_attempt.score
    
    # Determine grade
    if percentage >= 90:
        grade = 'A+'
    elif percentage >= 80:
        grade = 'A'
    elif percentage >= 70:
        grade = 'B'
    elif percentage >= 60:
        grade = 'C'
    else:
        grade = 'F'
    
    return render(request, "quizzes/quiz_results.html", {
        "quiz_attempt": quiz_attempt,
        "total": total,
        "correct": correct,
        "incorrect": incorrect,
        "percentage": percentage,
        "grade": grade,
    })

def finalize_quiz_attempt(quiz_attempt):
    """
    Finalize quiz attempt:
    - calculate correct / attempted
    - calculate score
    - calculate time taken
    - mark completed
    """
    questions = quiz_attempt.questions or []

    attempted = 0
    correct = 0

    for q in questions:
        if q.get("user_answer") is not None:
            attempted += 1
            if q.get("is_correct") is True:
                correct += 1

    quiz_attempt.attempted_questions = attempted
    quiz_attempt.correct_answers = correct

    quiz_attempt.score = (
        (correct / quiz_attempt.total_questions) * 100
        if quiz_attempt.total_questions > 0 else 0
    )

    quiz_attempt.completed_at = timezone.now()
    quiz_attempt.status = QuizAttempt.STATUS_COMPLETED

    quiz_attempt.time_taken_seconds = int(
        (quiz_attempt.completed_at - quiz_attempt.started_at).total_seconds()
    )

    quiz_attempt.save()
