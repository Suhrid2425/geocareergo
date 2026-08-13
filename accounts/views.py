from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import StudentProfile


# ==========================================================
# LOGIN
# ==========================================================

def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            # Make sure profile exists
            StudentProfile.objects.get_or_create(
                user=user
            )

            # Send incomplete profiles to profile page
            profile = user.student_profile

            if not profile.profile_completed:

                return redirect(
                    "accounts:complete_profile"
                )

            return redirect("core:home")

        return render(
            request,
            "accounts/login.html",
            {
                "error": "Invalid username or password."
            }
        )

    return render(
        request,
        "accounts/login.html"
    )


# ==========================================================
# LOGOUT
# ==========================================================

def logout_view(request):

    logout(request)

    return redirect("core:home")


# ==========================================================
# REGISTER
# ==========================================================

def register_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Username check

        if User.objects.filter(
            username=username
        ).exists():

            return render(
                request,
                "accounts/register.html",
                {
                    "error": "Username already exists."
                }
            )

        # Email check

        if email and User.objects.filter(
            email=email
        ).exists():

            return render(
                request,
                "accounts/register.html",
                {
                    "error": "An account with this email already exists."
                }
            )

        # Create user

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Create student profile

        StudentProfile.objects.create(
            user=user
        )

        # Login immediately

        login(request, user)

        # Complete profile

        return redirect(
            "accounts:complete_profile"
        )

    return render(
        request,
        "accounts/register.html"
    )


# ==========================================================
# COMPLETE PROFILE
# ==========================================================

def complete_profile(request):

    if not request.user.is_authenticated:

        return redirect(
            "accounts:login"
        )

    profile, created = StudentProfile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":

        profile.full_name = request.POST.get(
     "full_name",
        ""
       ) 

        profile.degree = request.POST.get(
            "degree",
            ""
        )

        profile.branch = request.POST.get(
            "branch",
            ""
        )

        profile.college = request.POST.get(
            "college",
            ""
        )

        profile.year = request.POST.get(
            "year",
            ""
        )

        profile.semester = request.POST.get(
            "semester",
            ""
        )

        graduation_year = request.POST.get(
            "graduation_year",
            ""
        )

        if graduation_year:

            profile.graduation_year = graduation_year

        else:

            profile.graduation_year = None

        profile.career_interest = request.POST.get(
            "career_interest",
            ""
        )

        profile.exam_interest = request.POST.get(
            "exam_interest",
            ""
        )

        profile.profile_completed = True

        profile.save()

        return redirect(
            "core:home"
        )

    return render(
    request,
    "accounts/complete_profile.html",
    {
        "profile": profile,
        "degree_choices": StudentProfile.DEGREE_CHOICES,
        "year_choices": StudentProfile.YEAR_CHOICES,
        "semester_choices": StudentProfile.SEMESTER_CHOICES,
    }
)
@login_required
def profile_view(request):

    profile, created = StudentProfile.objects.get_or_create(
        user=request.user
    )

    return render(
        request,
        "accounts/profile.html",
        {
            "profile": profile,
        }
    )