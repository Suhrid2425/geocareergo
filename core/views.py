from django.shortcuts import render

from jobs.models import Job


def home(request):

    trending_jobs = Job.objects.filter(
        is_active=True,
        is_trending=True
    ).order_by("-created_at")[:6]

    return render(
        request,
        "core/home.html",
        {
            "trending_jobs": trending_jobs,
        }
    )


def mentorship(request):

    return render(
        request,
        "core/mentorship.html"
    )