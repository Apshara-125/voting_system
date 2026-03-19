from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("vote/<str:reg_no>/", views.vote, name="vote"),
    path("results/", views.results, name="results"),
    path("already-voted/", views.already_voted, name="already_voted"),
    path("confirmation/", views.confirmation_view, name="confirmation"),
    path("admin-welcome/", views.admin_welcome, name="admin_welcome"),
    path("analysis/", views.analysis_view, name="analysis"),  # Added missing route
]