from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from accounts.models import CompanyProfile
from django.http import HttpResponse, HttpResponseRedirect
from .forms import JobApplicationForm, JobForm
from .models import Job, JobApplication


# ============================================================
# PUBLIC — JOB LIST
# ============================================================

def job_list(request):

    jobs = (
        Job.objects
        .filter(is_active=True)
        .select_related("company")
        .order_by("-created_at")
    )

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    search = request.GET.get("q", "").strip()

    if search:
        jobs = jobs.filter(
            Q(title__icontains=search)
            | Q(company_name__icontains=search)
            | Q(company__company_name__icontains=search)
            | Q(location__icontains=search)
        )

    # --------------------------------------------------------
    # JOB TYPE
    # --------------------------------------------------------

    job_type = request.GET.get("type", "").strip()

    if job_type:
        jobs = jobs.filter(
            job_type=job_type
        )

    # --------------------------------------------------------
    # DEGREE
    # --------------------------------------------------------

    degree = request.GET.get("degree", "").strip()

    if degree:
        jobs = jobs.filter(
            Q(degree=degree)
            | Q(degree="any")
        )

    # --------------------------------------------------------
    # EXPERIENCE
    # --------------------------------------------------------

    min_experience = request.GET.get(
        "min_experience",
        ""
    ).strip()

    max_experience = request.GET.get(
        "max_experience",
        ""
    ).strip()

    if min_experience.isdigit():

        min_exp = int(min_experience)

        jobs = jobs.filter(
            Q(max_experience__isnull=True)
            | Q(max_experience__gte=min_exp)
        )

    if max_experience.isdigit():

        max_exp = int(max_experience)

        jobs = jobs.filter(
            Q(min_experience__isnull=True)
            | Q(min_experience__lte=max_exp)
        )

    return render(
        request,
        "jobs/job_list.html",
        {
            "jobs": jobs,
            "search": search,
            "selected_type": job_type,
            "selected_degree": degree,
            "selected_min_experience": min_experience,
            "selected_max_experience": max_experience,
        }
    )


# ============================================================
# PUBLIC — JOB DETAIL
# ============================================================

def job_detail(request, job_id):

    job = get_object_or_404(
        Job.objects.select_related("company"),
        id=job_id,
        is_active=True
    )

    return render(
        request,
        "jobs/job_detail.html",
        {
            "job": job
        }
    )


# ============================================================
# STUDENT — APPLY FOR JOB
# ============================================================

@login_required
def apply_job(request, job_id):

    job = get_object_or_404(
        Job.objects.select_related("company"),
        id=job_id,
        is_active=True
    )

    # --------------------------------------------------------
    # CHECK DEADLINE
    # --------------------------------------------------------

    if job.last_date:

        today = timezone.localdate()

        if today > job.last_date:

            messages.error(
                request,
                "Applications for this job are closed."
            )

            return redirect(
                "jobs:job_detail",
                job_id=job.id
            )

    # --------------------------------------------------------
    # EXTERNAL APPLICATION
    #
    # User must be logged into GeoCareerGo first.
    # Once logged in, continue to the company's
    # external application website.
    # --------------------------------------------------------

    if job.application_type == "external":

        if not job.application_url:

            messages.error(
                request,
                "Application link is not available for this job."
            )

            return redirect(
                "jobs:job_detail",
                job_id=job.id
            )

        return redirect(
            job.application_url
        )
        # --------------------------------------------------------
    # EMAIL APPLICATION
    # --------------------------------------------------------

    if job.application_type == "email":

        if not job.application_email:
            messages.error(
                request,
                "Application email is not available for this job."
            )

            return redirect(
                "jobs:job_detail",
                job_id=job.id
            )

        return HttpResponseRedirect(
            f"mailto:{job.application_email}"
        )

    # --------------------------------------------------------
    # INTERNAL APPLICATION
    # --------------------------------------------------------

    # --------------------------------------------------------
    # CHECK STUDENT PROFILE
    # --------------------------------------------------------

    try:

        profile = request.user.student_profile

    except Exception:

        messages.warning(
            request,
            "Please complete your profile before applying."
        )

        return redirect(
            "accounts:complete_profile"
        )

    if not profile.profile_completed:

        messages.warning(
            request,
            "Please complete your profile before applying."
        )

        return redirect(
            "accounts:complete_profile"
        )

    # --------------------------------------------------------
    # PREVENT DUPLICATE APPLICATION
    # --------------------------------------------------------

    already_applied = JobApplication.objects.filter(
        job=job,
        applicant=request.user
    ).exists()

    if already_applied:

        messages.info(
            request,
            "You have already applied for this job."
        )

        return redirect(
            "jobs:job_detail",
            job_id=job.id
        )

    # --------------------------------------------------------
    # APPLICATION FORM
    # --------------------------------------------------------

    if request.method == "POST":

        form = JobApplicationForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            application = form.save(
                commit=False
            )

            application.job = job
            application.applicant = request.user

            application.save()

            messages.success(
                request,
                "Your application has been submitted successfully."
            )

            return redirect(
                "jobs:job_detail",
                job_id=job.id
            )

    else:

        form = JobApplicationForm()

    return render(
        request,
        "jobs/apply_job.html",
        {
            "job": job,
            "profile": profile,
            "form": form,
        }
    )


# ============================================================
# COMPANY — POST JOB
# ============================================================

@login_required
def post_job(request):

    # --------------------------------------------------------
    # GET LOGGED-IN COMPANY
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # COMPANY VERIFICATION
    # --------------------------------------------------------

    if company.verification_status != "verified":

        messages.warning(
            request,
            "Your company must be verified before posting jobs."
        )

        return redirect(
            "accounts:company_dashboard"
        )

    # --------------------------------------------------------
    # POST JOB
    # --------------------------------------------------------

    if request.method == "POST":

        form = JobForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            job = form.save(
                commit=False
            )

            # Company ownership comes ONLY from
            # the logged-in company account.

            job.company = company

            # ------------------------------------------------
            # COMPANY NAME
            # ------------------------------------------------

            if not job.company_name:
                job.company_name = company.company_name

            # ------------------------------------------------
            # SECURITY / DEFAULTS
            # ------------------------------------------------

            job.is_active = True

            # Company cannot control trending.
            # Admin can mark jobs as trending.

            job.is_trending = False

            job.save()

            messages.success(
                request,
                f"Job '{job.title}' has been posted successfully."
            )

            return redirect(
                "accounts:company_dashboard"
            )

    else:

        form = JobForm(
            initial={
                "company_name": company.company_name,
            }
        )

    return render(
        request,
        "jobs/company_post_job.html",
        {
            "form": form,
            "company": company,
        }
    )


# ============================================================
# COMPANY — MY JOBS
# ============================================================

@login_required
def company_jobs(request):

    # --------------------------------------------------------
    # GET LOGGED-IN COMPANY
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # ONLY THIS COMPANY'S JOBS
    # --------------------------------------------------------

    jobs = (
        Job.objects
        .filter(company=company)
        .select_related("company")
        .order_by("-created_at")
    )

    return render(
        request,
        "jobs/company_jobs.html",
        {
            "company": company,
            "jobs": jobs,
        }
    )


# ============================================================
# COMPANY — EDIT JOB
# ============================================================

@login_required
def edit_job(request, job_id):

    # --------------------------------------------------------
    # GET LOGGED-IN COMPANY
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # ONLY ALLOW THIS COMPANY'S JOB
    # --------------------------------------------------------

    job = get_object_or_404(
        Job,
        id=job_id,
        company=company
    )

    # --------------------------------------------------------
    # EDIT FORM
    # --------------------------------------------------------

    if request.method == "POST":

        form = JobForm(
            request.POST,
            request.FILES,
            instance=job
        )

        if form.is_valid():

            updated_job = form.save(
                commit=False
            )

            # NEVER allow company ownership
            # to be changed through the form.

            updated_job.company = company

            if not updated_job.company_name:
                updated_job.company_name = company.company_name

            # Company cannot make a job trending.

            updated_job.is_trending = job.is_trending

            updated_job.save()

            messages.success(
                request,
                "Job updated successfully."
            )

            return redirect(
                "jobs:company_jobs"
            )

    else:

        form = JobForm(
            instance=job
        )

    return render(
        request,
        "jobs/edit_job.html",
        {
            "form": form,
            "job": job,
            "company": company,
        }
    )


# ============================================================
# COMPANY — DELETE JOB
# ============================================================

@login_required
def delete_job(request, job_id):

    # --------------------------------------------------------
    # GET LOGGED-IN COMPANY
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # ONLY THIS COMPANY CAN DELETE ITS JOB
    # --------------------------------------------------------

    job = get_object_or_404(
        Job,
        id=job_id,
        company=company
    )

    # --------------------------------------------------------
    # DELETE
    # --------------------------------------------------------

    if request.method == "POST":

        title = job.title

        job.delete()

        messages.success(
            request,
            f"Job '{title}' has been deleted."
        )

        return redirect(
            "jobs:company_jobs"
        )

    return render(
        request,
        "jobs/delete_job.html",
        {
            "job": job,
            "company": company,
        }
    )


# ============================================================
# COMPANY — TOGGLE JOB ACTIVE STATUS
# ============================================================

@login_required
def toggle_job_status(request, job_id):

    # --------------------------------------------------------
    # GET LOGGED-IN COMPANY
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # ONLY THIS COMPANY'S JOB
    # --------------------------------------------------------

    job = get_object_or_404(
        Job,
        id=job_id,
        company=company
    )

    if request.method == "POST":

        job.is_active = not job.is_active

        job.save(
            update_fields=[
                "is_active",
                "updated_at"
            ]
        )

        if job.is_active:

            messages.success(
                request,
                "Job has been published."
            )

        else:

            messages.success(
                request,
                "Job has been unpublished."
            )

    return redirect(
        "jobs:company_jobs"
    )


# ============================================================
# COMPANY — VIEW APPLICATIONS FOR A JOB
# ============================================================

@login_required
def job_applications(request, job_id):

    # --------------------------------------------------------
    # GET LOGGED-IN COMPANY
    # --------------------------------------------------------

    try:

        company = request.user.company_profile

    except CompanyProfile.DoesNotExist:

        return redirect(
            "accounts:company_login"
        )

    # --------------------------------------------------------
    # SECURITY:
    # JOB MUST BELONG TO THIS COMPANY
    # --------------------------------------------------------

    job = get_object_or_404(
        Job,
        id=job_id,
        company=company
    )

    # --------------------------------------------------------
    # GET APPLICATIONS
    # --------------------------------------------------------

    applications = (
        JobApplication.objects
        .filter(job=job)
        .select_related("applicant")
        .order_by("-applied_at")
    )

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    search = request.GET.get(
        "search",
        ""
    ).strip()

    if search:

        applications = applications.filter(
            Q(applicant__first_name__icontains=search)
            | Q(applicant__last_name__icontains=search)
            | Q(applicant__username__icontains=search)
            | Q(applicant__email__icontains=search)
        )

    # --------------------------------------------------------
    # STATUS FILTER
    # --------------------------------------------------------

    status = request.GET.get(
        "status",
        ""
    ).strip()

    if status:

        applications = applications.filter(
            status=status
        )

    # --------------------------------------------------------
    # COUNTS
    # --------------------------------------------------------

    total_count = JobApplication.objects.filter(
        job=job
    ).count()

    submitted_count = JobApplication.objects.filter(
        job=job,
        status="submitted"
    ).count()

    reviewing_count = JobApplication.objects.filter(
        job=job,
        status="reviewing"
    ).count()

    shortlisted_count = JobApplication.objects.filter(
        job=job,
        status="shortlisted"
    ).count()

    selected_count = JobApplication.objects.filter(
        job=job,
        status="selected"
    ).count()

    rejected_count = JobApplication.objects.filter(
        job=job,
        status="rejected"
    ).count()

    return render(
        request,
        "jobs/job_applications.html",
        {
            "job": job,
            "applications": applications,
            "status_choices": JobApplication.STATUS_CHOICES,

            "search": search,
            "selected_status": status,

            "total_count": total_count,
            "submitted_count": submitted_count,
            "reviewing_count": reviewing_count,
            "shortlisted_count": shortlisted_count,
            "selected_count": selected_count,
            "rejected_count": rejected_count,
        }
    )


# ============================================================
# COMPANY — UPDATE APPLICATION STATUS
# ============================================================

@login_required
def update_application_status(
    request,
    application_id
):

    # --------------------------------------------------------
    # GET LOGGED-IN COMPANY
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # SECURITY:
    # APPLICATION MUST BELONG TO
    # COMPANY'S OWN JOB
    # --------------------------------------------------------

    application = get_object_or_404(
        JobApplication.objects.select_related(
            "job",
            "applicant"
        ),
        id=application_id,
        job__company=company
    )

    # --------------------------------------------------------
    # UPDATE STATUS
    # --------------------------------------------------------

    if request.method == "POST":

        new_status = request.POST.get(
            "status",
            ""
        ).strip()

        valid_statuses = {
            choice[0]
            for choice in JobApplication.STATUS_CHOICES
        }

        if new_status not in valid_statuses:

            messages.error(
                request,
                "Invalid application status."
            )

        else:

            application.status = new_status

            application.save(
                update_fields=[
                    "status",
                    "updated_at"
                ]
            )

            messages.success(
                request,
                "Application status updated successfully."
            )

    return redirect(
        "jobs:job_applications",
        job_id=application.job.id
    )