from django.urls import path

from . import views


app_name = "accounts"


urlpatterns = [

    # Login
    path(
        "login/",
        views.login_view,
        name="login"
    ),

    # Logout
    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),

    # Register
    path(
        "register/",
        views.register_view,
        name="register"
    ),

    # Complete Student Profile
    path(
        "complete-profile/",
        views.complete_profile,
        name="complete_profile"
    ),
    path(
    "profile/",
    views.profile_view,
    name="profile"
),

]