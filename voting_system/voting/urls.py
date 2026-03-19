from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),                        # Homepage
    path("vote/<str:reg_no>/", views.vote, name="vote"),      # Voting page
    path("results/", views.results, name="results"),          # Results page
    path("already-voted/", views.already_voted, name="already_voted"),  # Already voted page
    path("login/", views.login_view, name="login"),           # Login page
    path("signup/", views.signup, name="signup"),  # Signup page

]
