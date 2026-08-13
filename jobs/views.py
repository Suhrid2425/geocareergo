from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.utils import timezone

from .models import Job, JobApplication
from .forms import JobApplicationForm


def job_list(request):

    jobs = Job.objects.filter(
        is_active=True
    ).order_by("-created_at")

    # ==================================================
    # SEARCH
    # ==================================================

    search = request.GET.get(
        "q",
        ""
    ).strip()

    if search:

        from django.db.models import Q

        jobs = jobs.filter(
            Q(title__icontains=search)
            | Q(organization__icontains=search)
            | Q(location__icontains=search)
        )


    # ==================================================
    # JOB TYPE
    # ==================================================

    job_type = request.GET.get(
        "type",
        ""
    ).strip()

    if job_type:

        jobs = jobs.filter(
            job_type=job_type
        )


    # ==================================================
    # DEGREE
    # ==================================================

    degree = request.GET.get(
        "degree",
        ""
    ).strip()

    if degree:

        from django.db.models import Q

        jobs = jobs.filter(
            Q(degree=degree)
            | Q(degree="any")
        )


    # ==================================================
    # EXPERIENCE
    # ==================================================

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

        from django.db.models import Q

        jobs = jobs.filter(
            Q(max_experience__isnull=True)
            | Q(max_experience__gte=min_exp)
        )


    if max_experience.isdigit():

        max_exp = int(max_experience)

        from django.db.models import Q

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


def job_detail(request, job_id):

    job = get_object_or_404(
        Job,
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


# ==================================================
# APPLY ON GEOCAREERGO
# ==================================================

@login_required
def apply_job(request, job_id):

    job = get_object_or_404(
        Job,
        id=job_id,
        is_active=True
    )


    # ==================================================
    # ONLY INTERNAL JOBS
    # ==================================================

    if job.application_type != "internal":

        return redirect(
            "jobs:job_detail",
            job_id=job.id
        )


    # ==================================================
    # CHECK APPLICATION DEADLINE
    # ==================================================

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


    # ==================================================
    # CHECK STUDENT PROFILE
    # ==================================================

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


    # ==================================================
    # PREVENT DUPLICATE APPLICATION
    # ==================================================

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


    # ==================================================
    # APPLICATION FORM
    # ==================================================

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