from django.urls import path
from . import views

app_name = "quizzes"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("categories/", views.category_list, name="categories"),
    path("category/<int:category_id>/", views.choose_subcategory, name="subcategories"),
    path("subcategory/<int:sub_id>/children/", views.subcategory_children, name="subcategory_children"),  
    path("subcategory/<int:subcategory_id>/difficulty/", 
         views.choose_difficulty, 
         name="choose_difficulty"),
    path("subcategory/<int:subcategory_id>/instructions/<str:difficulty>/",
         views.instructions,
         name="instructions"),
    path("start/<int:subcategory_id>/<str:difficulty>/",
         views.start_quiz,
         name="start_quiz"),

     # Quiz flow URLs
    path("start/<int:subcategory_id>/<str:difficulty>/", views.start_quiz, name="start_quiz"),
    path("attempt/<uuid:attempt_id>/generate/", views.generate_questions, name="generate_questions"),
    path("attempt/<uuid:attempt_id>/question/", views.show_question, name="show_question"),
    path("attempt/<uuid:attempt_id>/submit/", views.submit_answer, name="submit_answer"),
    path("attempt/<uuid:attempt_id>/results/", views.quiz_results, name="quiz_results"),
]