# quizzes/models.py
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
import hashlib
import re
class Category(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=150)
    level = models.SmallIntegerField(default=1)
    parent_subcat = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    is_leaf = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('category', 'name')
        ordering = ['category', 'level', 'name']

    def __str__(self):
        return f"{self.category.name} - {self.name}"

class QuizAttempt(models.Model):
    correct_answers = models.SmallIntegerField(default=0)
    attempted_questions = models.SmallIntegerField(default=0)
    time_taken_seconds = models.IntegerField(default=0)
    # Status choices
    STATUS_GENERATING = 0
    STATUS_IN_PROGRESS = 1
    STATUS_COMPLETED = 2
    STATUS_ABANDONED = 3
    
    STATUS_CHOICES = [
        (STATUS_GENERATING, 'Generating Questions'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_ABANDONED, 'Abandoned'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_attempts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True)
    difficulty = models.CharField(max_length=10, choices=[
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard')
    ],
    default='medium')
    time_limit_seconds = models.IntegerField(default=600)  # 10 minutes default
    
    # JSON structure for questions:
    # [
    #   {
    #     "id": 1,
    #     "question": "What is...",
    #     "option_a": "...",
    #     "option_b": "...",
    #     "option_c": "...",
    #     "option_d": "...",
    #     "correct_answer": "A",
    #     "explanation": "...",
    #     "user_answer": null,  # filled when user answers
    #     "is_correct": null    # calculated when user answers
    #   }
    # ]
    questions = models.JSONField(null=True, blank=True)
    
    # AI metadata (model used, tokens, generation time, etc.)
    ai_meta = models.JSONField(null=True, blank=True)
    
    status = models.SmallIntegerField(default=STATUS_GENERATING, choices=STATUS_CHOICES)
    total_questions = models.SmallIntegerField(default=10)
    current_question_index = models.SmallIntegerField(default=0)  # Track progress
    score = models.FloatField(default=0.0)
    
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'started_at']),
            models.Index(fields=['category', 'subcategory']),
            models.Index(fields=['status']),
        ]
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.user.username} - {self.subcategory.name if self.subcategory else 'N/A'} ({self.difficulty})"
    
    def calculate_score(self):
        """Calculate score based on correct answers"""
        if not self.questions:
            return 0
        
        correct_count = sum(1 for q in self.questions if q.get('is_correct') == True)
        self.score = (correct_count / len(self.questions)) * 100
        return self.score
    
    def get_current_question(self):
        """Get the current question based on index"""
        if self.questions and 0 <= self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]
        return None
    
    def is_quiz_complete(self):
        """Check if all questions are answered"""
        if not self.questions:
            return False
        return all(q.get('user_answer') is not None for q in self.questions)
    
class Question(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    difficulty = models.CharField(max_length=10)

    question_text = models.TextField()
    option_a = models.TextField()
    option_b = models.TextField()
    option_c = models.TextField()
    option_d = models.TextField()
    correct_answer = models.CharField(max_length=1)
    explanation = models.TextField()

    normalized_hash = models.CharField(max_length=64, db_index=True, unique=True)

    source = models.CharField(
        max_length=10,
        choices=[('ai', 'AI'), ('manual', 'Manual')],
        default='ai'
    )

    usage_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def normalize(text):
        text = text.lower()
        text = re.sub(r'[^a-z0-9 ]+', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    @classmethod
    def make_hash(cls, text):
        return hashlib.sha256(cls.normalize(text).encode()).hexdigest()

    def __str__(self):
        return self.question_text[:60]

class Concept(models.Model):
    subcategory = models.ForeignKey(
        SubCategory,
        on_delete=models.CASCADE,
        related_name="concepts"
    )
    difficulty = models.CharField(
        max_length=10,
        choices=[
            ('easy', 'Easy'),
            ('medium', 'Medium'),
            ('hard', 'Hard')
        ]
    )
    name = models.CharField(max_length=150)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('subcategory', 'difficulty', 'name')
        ordering = ['name']

    def __str__(self):
        return f"{self.subcategory.name} - {self.name} ({self.difficulty})"
