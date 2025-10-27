from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),

    path("courses/", views.courses_list, name="courses_list"),
    path("courses/<slug:slug>/", views.course_enroll, name="course_enroll"),
    path("enroll/<slug:slug>/", views.enroll, name="enroll"),

    path("register/", views.register, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("settings/", views.settings_view, name="settings"),
    path("contact/", views.contact_submit, name="contact_submit"),

    # Keep only ONE course detail route
    path("course/<slug:slug>/", views.course_detail, name="course_detail"),

    # Static quizzes 1..8
    path("quiz/<int:num>/", views.quiz_static, name="quiz"),

    # JSON APIs
    path("api/profile/", views.api_profile, name="api_profile"),
    path("api/preferences/", views.api_preferences, name="api_preferences"),
    path("api/account/delete/", views.api_delete_account, name="api_delete_account"),
    path("api/lesson/toggle/", views.api_toggle_lesson_completion, name="api_toggle_lesson"),
    path("api/quiz/<int:quiz_id>/attempt/", views.api_submit_quiz_attempt, name="api_quiz_attempt"),

    # Staff helpers
    path("enroll/<int:user_id>/<slug:slug>/", views.enroll_user, name="enroll_user"),
    path("unenroll/<int:user_id>/<slug:slug>/", views.unenroll_user, name="unenroll_user"),
]
