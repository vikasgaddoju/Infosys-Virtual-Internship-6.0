from django.urls import path
from . import views
from . import views_spa

app_name = "quizzes"

urlpatterns = [
    # ============================================================
    # SPA Quiz Selector (Primary entry point for quiz selection)
    # ============================================================
    path("select/", views_spa.quiz_selector_view, name="quiz_selector"),
    path("api/children/", views_spa.get_children_ajax, name="get_children"),
    
    # ============================================================
    # Dashboard
    # ============================================================
    path("dashboard/", views.dashboard, name="dashboard"),
    
    # ============================================================
    # Quiz Flow (Instructions -> Start -> Questions -> Results)
    # ============================================================
    path("subcategory/<int:subcategory_id>/instructions/<str:difficulty>/",
         views.instructions,
         name="instructions"),
    path("start/<int:subcategory_id>/<str:difficulty>/",
         views.start_quiz,
         name="start_quiz"),
    path("attempt/<uuid:attempt_id>/generate/", views.generate_questions, name="generate_questions"),
    path("attempt/<uuid:attempt_id>/question/", views.show_question, name="show_question"),
    path("attempt/<uuid:attempt_id>/submit/", views.submit_answer, name="submit_answer"),
    path("attempt/<uuid:attempt_id>/auto-submit/", views.auto_submit_quiz, name="auto_submit_quiz"),
    path("attempt/<uuid:attempt_id>/results/", views.quiz_results, name="quiz_results"),

    # ============================================================
    # Performance & Analytics
    # ============================================================
    path("performance/", views.performance_dashboard, name="performance_dashboard"),       
    path("performance/download/", views.download_performance_pdf, name="download_performance_pdf"),

    # ============================================================
    # History & Leaderboard
    # ============================================================
    path('recent/', views.recent_quizzes_view, name='recent_quizzes'),
    path('attempts/', views.attempts_summary_view, name='attempts_summary'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),

    # ============================================================
    # Resume Quiz
    # ============================================================
    path('quiz/resume/<uuid:attempt_id>/', views.resume_quiz_prompt, name='resume_quiz_prompt'),
    path('quiz/resume/<uuid:attempt_id>/continue/', views.resume_quiz, name='resume_quiz'),
    path('quiz/resume/<uuid:attempt_id>/quit/', views.quit_quiz, name='quit_quiz'),
     # resume quiz
     path('quiz/resume/<uuid:attempt_id>/',views.resume_quiz_prompt,name='resume_quiz_prompt'),
     path('quiz/resume/<uuid:attempt_id>/continue/', views.resume_quiz, name='resume_quiz'),
     path('quiz/resume/<uuid:attempt_id>/quit/', views.quit_quiz, name='quit_quiz'),

     # back to previous question 
     path("attempt/<uuid:attempt_id>/previous/",views.previous_question,name="previous_question"),

     path('attempt/<uuid:attempt_id>/save-timer/', views.save_timer, name='save_timer'),

]