from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from jobs.models import Job, JobApplication

from .models import StudentProfile, CompanyProfile


# ==========================================================
# STUDENT LOGIN
# ==========================================================

def login_view(request):

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            # --------------------------------------------------
            # COMPANY ACCOUNT
            # --------------------------------------------------

            if hasattr(user, "company_profile"):

                login(
                    request,
                    user
                )

                return redirect(
                    "accounts:company_dashboard"
                )

            # --------------------------------------------------
            # STUDENT ACCOUNT
            # --------------------------------------------------

            login(
                request,
                user
            )

            profile, created = StudentProfile.objects.get_or_create(
                user=user
            )

            if not profile.profile_completed:

                return redirect(
                    "accounts:complete_profile"
                )

            return redirect(
                "core:home"
            )

        return render(
            request,
            "accounts/login.html",
            {
                "error": "Invalid username or password.",
                "google_client_id": settings.GOOGLE_CLIENT_ID,
            }
        )

    return render(
        request,
        "accounts/login.html",
        {
            "google_client_id": settings.GOOGLE_CLIENT_ID,
        }
    )


# ==========================================================
# GOOGLE SIGN-IN
# ==========================================================

@csrf_protect
def google_login(request):

    # ------------------------------------------------------
    # ONLY POST ALLOWED
    # ------------------------------------------------------

    if request.method != "POST":

        return JsonResponse(
            {
                "success": False,
                "message": "Invalid request method.",
            },
            status=405,
        )

    # ------------------------------------------------------
    # GET GOOGLE CREDENTIAL
    # ------------------------------------------------------

    credential = request.POST.get(
        "credential"
    )

    if not credential:

        return JsonResponse(
            {
                "success": False,
                "message": "Google credential missing.",
            },
            status=400,
        )

    # ------------------------------------------------------
    # CHECK GOOGLE CONFIGURATION
    # ------------------------------------------------------

    if not settings.GOOGLE_CLIENT_ID:

        return JsonResponse(
            {
                "success": False,
                "message": "Google Sign-In is not configured.",
            },
            status=500,
        )

    try:

        # --------------------------------------------------
        # VERIFY GOOGLE ID TOKEN
        # --------------------------------------------------

        google_user = id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )

        # --------------------------------------------------
        # GOOGLE ACCOUNT INFORMATION
        # --------------------------------------------------

        google_id = google_user.get(
            "sub"
        )

        email = google_user.get(
            "email"
        )

        email_verified = google_user.get(
            "email_verified",
            False
        )

        first_name = google_user.get(
            "given_name",
            ""
        )

        last_name = google_user.get(
            "family_name",
            ""
        )

        # --------------------------------------------------
        # BASIC VALIDATION
        # --------------------------------------------------

        if not google_id or not email:

            return JsonResponse(
                {
                    "success": False,
                    "message": "Invalid Google account information.",
                },
                status=400,
            )

        # --------------------------------------------------
        # EMAIL VERIFICATION
        # --------------------------------------------------

        if not email_verified:

            return JsonResponse(
                {
                    "success": False,
                    "message": "Google email is not verified.",
                },
                status=400,
            )

        email = email.strip().lower()

        # --------------------------------------------------
        # FIND EXISTING USER
        # --------------------------------------------------

        user = User.objects.filter(
            email__iexact=email
        ).first()

        # --------------------------------------------------
        # COMPANY ACCOUNT CHECK
        # --------------------------------------------------

        if user:

            try:

                user.company_profile

                return JsonResponse(
                    {
                        "success": False,
                        "message": (
                            "This email belongs to a company account. "
                            "Please use Company Login."
                        ),
                    },
                    status=403,
                )

            except CompanyProfile.DoesNotExist:

                pass

        # --------------------------------------------------
        # CREATE STUDENT USER IF NEEDED
        # --------------------------------------------------

        if not user:

            username_base = email.split("@")[0]

            username = username_base

            counter = 1

            while User.objects.filter(
                username=username
            ).exists():

                username = (
                    f"{username_base}{counter}"
                )

                counter += 1

            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
            )

            # Google handles authentication
            user.set_unusable_password()

            user.save()

        else:

            # --------------------------------------------------
            # UPDATE MISSING GOOGLE PROFILE INFORMATION
            # --------------------------------------------------

            changed = False

            if first_name and not user.first_name:

                user.first_name = first_name

                changed = True

            if last_name and not user.last_name:

                user.last_name = last_name

                changed = True

            if changed:

                user.save()

        # --------------------------------------------------
        # ENSURE STUDENT PROFILE EXISTS
        # --------------------------------------------------

        StudentProfile.objects.get_or_create(
            user=user
        )

        # --------------------------------------------------
        # LOGIN
        # --------------------------------------------------

        login(
            request,
            user,
            backend="django.contrib.auth.backends.ModelBackend",
        )

        # --------------------------------------------------
        # REDIRECT
        # --------------------------------------------------

        return JsonResponse(
            {
                "success": True,
                "redirect": "/accounts/profile/",
            }
        )

    except ValueError:

        return JsonResponse(
            {
                "success": False,
                "message": "Invalid or expired Google credential.",
            },
            status=400,
        )

    except Exception:

        return JsonResponse(
            {
                "success": False,
                "message": "Google Sign-In failed. Please try again.",
            },
            status=500,
        )


# ==========================================================
# LOGOUT
# ==========================================================

def logout_view(request):

    logout(
        request
    )

    return redirect(
        "core:home"
    )


# ==========================================================
# STUDENT REGISTER
# ==========================================================

@csrf_protect
def register_view(request):

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip().lower()

        password = request.POST.get(
            "password",
            ""
        )

        confirm_password = request.POST.get(
            "confirm_password",
            ""
        )

        # --------------------------------------------------
        # REQUIRED FIELDS
        # --------------------------------------------------

        if not username or not email or not password:

            return render(
                request,
                "accounts/register.html",
                {
                    "error": "All fields are required.",
                    "username": username,
                    "email": email,
                }
            )

        # --------------------------------------------------
        # PASSWORD
        # --------------------------------------------------

        if password != confirm_password:

            return render(
                request,
                "accounts/register.html",
                {
                    "error": "Passwords do not match.",
                    "username": username,
                    "email": email,
                }
            )

        # --------------------------------------------------
        # USERNAME
        # --------------------------------------------------

        if User.objects.filter(
            username=username
        ).exists():

            return render(
                request,
                "accounts/register.html",
                {
                    "error": "Username already exists.",
                    "username": username,
                    "email": email,
                }
            )

        # --------------------------------------------------
        # EMAIL
        # --------------------------------------------------

        if User.objects.filter(
            email=email
        ).exists():

            return render(
                request,
                "accounts/register.html",
                {
                    "error": (
                        "An account with this email "
                        "already exists."
                    ),
                    "username": username,
                    "email": email,
                }
            )

        # --------------------------------------------------
        # CREATE USER
        # --------------------------------------------------

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # --------------------------------------------------
        # CREATE STUDENT PROFILE
        # --------------------------------------------------

        StudentProfile.objects.create(
            user=user
        )

        # --------------------------------------------------
        # LOGIN
        # --------------------------------------------------

        login(
            request,
            user
        )

        return redirect(
            "accounts:complete_profile"
        )

    return render(
        request,
        "accounts/register.html"
    )


# ==========================================================
# STUDENT COMPLETE PROFILE
# ==========================================================

@login_required
def complete_profile(request):

    profile, created = StudentProfile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":

        profile.full_name = request.POST.get(
            "full_name",
            ""
        ).strip()

        profile.degree = request.POST.get(
            "degree",
            ""
        )

        profile.branch = request.POST.get(
            "branch",
            ""
        ).strip()

        profile.college = request.POST.get(
            "college",
            ""
        ).strip()

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
        ).strip()

        if graduation_year:

            profile.graduation_year = (
                graduation_year
            )

        else:

            profile.graduation_year = None

        profile.career_interest = request.POST.get(
            "career_interest",
            ""
        ).strip()

        profile.exam_interest = request.POST.get(
            "exam_interest",
            ""
        ).strip()

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


# ==========================================================
# STUDENT PROFILE
# ==========================================================

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


# ==========================================================
# COMPANY REGISTER
# ==========================================================

@csrf_protect
def company_register(request):

    # ------------------------------------------------------
    # GET
    # ------------------------------------------------------

    if request.method == "GET":

        return render(
            request,
            "accounts/company_register.html"
        )

    # ------------------------------------------------------
    # POST DATA
    # ------------------------------------------------------

    company_name = request.POST.get(
        "company_name",
        ""
    ).strip()

    company_email = request.POST.get(
        "company_email",
        ""
    ).strip().lower()

    website = request.POST.get(
        "website",
        ""
    ).strip()

    linkedin_url = request.POST.get(
        "linkedin_url",
        ""
    ).strip()

    executive_linkedin_url = request.POST.get(
        "executive_linkedin_url",
        ""
    ).strip()

    password = request.POST.get(
        "password",
        ""
    )

    confirm_password = request.POST.get(
        "confirm_password",
        ""
    )

    logo = request.FILES.get(
        "logo"
    )

    registration_document = request.FILES.get(
        "registration_document"
    )

    # ------------------------------------------------------
    # REQUIRED FIELDS
    # ------------------------------------------------------

    if not company_name:

        return render(
            request,
            "accounts/company_register.html",
            {
                "error": "Company name is required.",
                "company_name": company_name,
                "company_email": company_email,
            }
        )

    if not company_email:

        return render(
            request,
            "accounts/company_register.html",
            {
                "error": "Company email is required.",
                "company_name": company_name,
                "company_email": company_email,
            }
        )

    if not password:

        return render(
            request,
            "accounts/company_register.html",
            {
                "error": "Password is required.",
                "company_name": company_name,
                "company_email": company_email,
            }
        )

    # ------------------------------------------------------
    # PASSWORD CHECK
    # ------------------------------------------------------

    if password != confirm_password:

        return render(
            request,
            "accounts/company_register.html",
            {
                "error": "Passwords do not match.",
                "company_name": company_name,
                "company_email": company_email,
            }
        )

    # ------------------------------------------------------
    # EMAIL CHECK
    # ------------------------------------------------------

    if User.objects.filter(
        email=company_email
    ).exists():

        return render(
            request,
            "accounts/company_register.html",
            {
                "error": (
                    "An account with this company email "
                    "already exists."
                ),
                "company_name": company_name,
                "company_email": company_email,
            }
        )

    # ------------------------------------------------------
    # USERNAME CHECK
    #
    # Company username = company email
    # ------------------------------------------------------

    if User.objects.filter(
        username=company_email
    ).exists():

        return render(
            request,
            "accounts/company_register.html",
            {
                "error": (
                    "An account with this company email "
                    "already exists."
                ),
                "company_name": company_name,
                "company_email": company_email,
            }
        )

    # ------------------------------------------------------
    # CREATE DJANGO USER
    # ------------------------------------------------------

    user = User.objects.create_user(
        username=company_email,
        email=company_email,
        password=password
    )

    # ------------------------------------------------------
    # CREATE COMPANY PROFILE
    # ------------------------------------------------------

    CompanyProfile.objects.create(
        user=user,
        company_name=company_name,
        company_email=company_email,
        website=website,
        linkedin_url=linkedin_url,
        executive_linkedin_url=executive_linkedin_url,
        logo=logo,
        registration_document=registration_document,
        verification_status="pending"
    )

    # ------------------------------------------------------
    # LOGIN COMPANY
    # ------------------------------------------------------

    login(
        request,
        user
    )

    messages.success(
        request,
        (
            "Company account created successfully. "
            "Your company is now pending verification."
        )
    )

    # ------------------------------------------------------
    # DASHBOARD
    # ------------------------------------------------------

    return redirect(
        "accounts:company_dashboard"
    )


# ==========================================================
# COMPANY LOGIN
# ==========================================================

@csrf_protect
def company_login(request):

    if request.method == "POST":

        email = request.POST.get(
            "email",
            ""
        ).strip().lower()

        password = request.POST.get(
            "password",
            ""
        )

        # --------------------------------------------------
        # REQUIRED
        # --------------------------------------------------

        if not email or not password:

            return render(
                request,
                "accounts/company_login.html",
                {
                    "error": (
                        "Company email and password "
                        "are required."
                    ),
                    "email": email,
                }
            )

        # --------------------------------------------------
        # FIND USER
        # --------------------------------------------------

        try:

            user_account = User.objects.get(
                email=email
            )

        except User.DoesNotExist:

            return render(
                request,
                "accounts/company_login.html",
                {
                    "error": (
                        "Invalid company email or password."
                    ),
                    "email": email,
                }
            )

        # --------------------------------------------------
        # COMPANY PROFILE
        # --------------------------------------------------

        try:

            user_account.company_profile

        except CompanyProfile.DoesNotExist:

            return render(
                request,
                "accounts/company_login.html",
                {
                    "error": (
                        "This account is not registered "
                        "as a company."
                    ),
                    "email": email,
                }
            )

        # --------------------------------------------------
        # AUTHENTICATE
        # --------------------------------------------------

        user = authenticate(
            request,
            username=user_account.username,
            password=password
        )

        if user is None:

            return render(
                request,
                "accounts/company_login.html",
                {
                    "error": (
                        "Invalid company email or password."
                    ),
                    "email": email,
                }
            )

        # --------------------------------------------------
        # LOGIN
        # --------------------------------------------------

        login(
            request,
            user
        )

        return redirect(
            "accounts:company_dashboard"
        )

    return render(
        request,
        "accounts/company_login.html"
    )


# ==========================================================
# COMPANY DASHBOARD
# ==========================================================

@login_required
def company_dashboard(request):

    try:

        company = request.user.company_profile

    except CompanyProfile.DoesNotExist:

        messages.error(
            request,
            "Company profile not found."
        )

        return redirect(
            "accounts:company_login"
        )

    # ========================================================
    # COMPANY JOBS
    # ========================================================

    company_jobs = Job.objects.filter(
        company=company
    )

    total_jobs = company_jobs.count()

    active_jobs = company_jobs.filter(
        is_active=True
    ).count()

    inactive_jobs = company_jobs.filter(
        is_active=False
    ).count()

    # ========================================================
    # APPLICATIONS
    # ========================================================

    company_applications = JobApplication.objects.filter(
        job__company=company
    )

    total_applications = company_applications.count()

    shortlisted_applications = company_applications.filter(
        status="shortlisted"
    ).count()

    selected_applications = company_applications.filter(
        status="selected"
    ).count()

    reviewing_applications = company_applications.filter(
        status="reviewing"
    ).count()

    # ========================================================
    # RECENT APPLICATIONS
    # ========================================================

    recent_applications = (
        company_applications
        .select_related(
            "job",
            "applicant"
        )
        .order_by("-applied_at")[:5]
    )

    # ========================================================
    # RENDER
    # ========================================================

    return render(
        request,
        "accounts/company_dashboard.html",
        {
            "profile": company,

            "total_jobs": total_jobs,
            "active_jobs": active_jobs,
            "inactive_jobs": inactive_jobs,

            "total_applications": total_applications,
            "shortlisted_applications": shortlisted_applications,
            "selected_applications": selected_applications,
            "reviewing_applications": reviewing_applications,

            "recent_applications": recent_applications,
        }
    )


# ==========================================================
# COMPANY EDIT PROFILE / VERIFICATION
# ==========================================================

@csrf_protect
@login_required
def company_verification(request):

    # ------------------------------------------------------
    # GET COMPANY PROFILE
    # ------------------------------------------------------

    try:

        profile = request.user.company_profile

    except CompanyProfile.DoesNotExist:

        messages.error(
            request,
            "Company profile not found."
        )

        return redirect(
            "accounts:company_register"
        )

    # ------------------------------------------------------
    # GET
    # ------------------------------------------------------

    if request.method == "GET":

        return render(
            request,
            "accounts/company_verification.html",
            {
                "profile": profile,
            }
        )

    # ------------------------------------------------------
    # POST DATA
    # ------------------------------------------------------

    company_name = request.POST.get(
        "company_name",
        ""
    ).strip()

    company_email = request.POST.get(
        "company_email",
        ""
    ).strip().lower()

    website = request.POST.get(
        "website",
        ""
    ).strip()

    linkedin_url = request.POST.get(
        "linkedin_url",
        ""
    ).strip()

    executive_linkedin_url = request.POST.get(
        "executive_linkedin_url",
        ""
    ).strip()

    logo = request.FILES.get(
        "logo"
    )

    registration_document = request.FILES.get(
        "registration_document"
    )

    # ------------------------------------------------------
    # REQUIRED
    # ------------------------------------------------------

    if not company_name or not company_email:

        return render(
            request,
            "accounts/company_verification.html",
            {
                "profile": profile,
                "error": (
                    "Company name and company email "
                    "are required."
                )
            }
        )

    # ------------------------------------------------------
    # EMAIL CHECK
    # ------------------------------------------------------

    existing_user = (
        User.objects
        .filter(email=company_email)
        .exclude(id=request.user.id)
        .first()
    )

    if existing_user:

        return render(
            request,
            "accounts/company_verification.html",
            {
                "profile": profile,
                "error": (
                    "This email is already being used "
                    "by another account."
                )
            }
        )

    # ------------------------------------------------------
    # USERNAME CHECK
    # ------------------------------------------------------

    existing_username = (
        User.objects
        .filter(username=company_email)
        .exclude(id=request.user.id)
        .first()
    )

    if existing_username:

        return render(
            request,
            "accounts/company_verification.html",
            {
                "profile": profile,
                "error": (
                    "This email is already being used "
                    "by another account."
                )
            }
        )

    # ------------------------------------------------------
    # UPDATE PROFILE
    # ------------------------------------------------------

    profile.company_name = company_name

    profile.company_email = company_email

    profile.website = website

    profile.linkedin_url = linkedin_url

    profile.executive_linkedin_url = (
        executive_linkedin_url
    )

    # ------------------------------------------------------
    # LOGO
    # ------------------------------------------------------

    if logo:

        profile.logo = logo

    # ------------------------------------------------------
    # REGISTRATION DOCUMENT
    # ------------------------------------------------------

    if registration_document:

        profile.registration_document = (
            registration_document
        )

    # ------------------------------------------------------
    # PENDING VERIFICATION
    # ------------------------------------------------------

    profile.verification_status = "pending"

    profile.save()

    # ------------------------------------------------------
    # UPDATE DJANGO USER
    # ------------------------------------------------------

    request.user.email = company_email

    request.user.username = company_email

    request.user.save()

    # ------------------------------------------------------
    # SUCCESS
    # ------------------------------------------------------

    messages.success(
        request,
        (
            "Company profile updated and submitted "
            "for verification."
        )
    )

    return redirect(
        "accounts:company_dashboard"
    )


# ==========================================================
# COMPANY EDIT PROFILE
# ==========================================================

@login_required
def company_edit_profile(request):

    try:

        company = request.user.company_profile

    except CompanyProfile.DoesNotExist:

        messages.error(
            request,
            "Company profile not found."
        )

        return redirect(
            "accounts:company_login"
        )

    if request.method == "POST":

        company.company_name = request.POST.get(
            "company_name",
            ""
        ).strip()

        company.company_email = request.POST.get(
            "company_email",
            ""
        ).strip()

        company.website = request.POST.get(
            "website",
            ""
        ).strip()

        company.linkedin_url = request.POST.get(
            "linkedin_url",
            ""
        ).strip()

        company.executive_linkedin_url = (
            request.POST.get(
                "executive_linkedin_url",
                ""
            ).strip()
        )

        if request.FILES.get("logo"):

            company.logo = request.FILES["logo"]

        if request.FILES.get(
            "registration_document"
        ):

            company.registration_document = (
                request.FILES[
                    "registration_document"
                ]
            )

        company.verification_status = "pending"

        company.save()

        messages.success(
            request,
            (
                "Company profile updated successfully. "
                "It is now pending verification."
            )
        )

        return redirect(
            "accounts:company_dashboard"
        )

    return render(
        request,
        "accounts/company_edit_profile.html",
        {
            "profile": company,
        }
    )