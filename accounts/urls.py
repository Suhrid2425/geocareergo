from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
    path("complete-profile/", views.complete_profile, name="complete_profile"),
    path("profile/", views.profile_view, name="profile"),

    # Company
    path("company-register/", views.company_register, name="company_register"),
    path("company-login/", views.company_login, name="company_login"),
    path("company-dashboard/", views.company_dashboard, name="company_dashboard"),
    path(
        "company-edit-profile/",
        views.company_verification,
        name="company_edit_profile",
    ),

    # Google Sign-In
    path("google-login/", views.google_login, name="google_login"),
]