from django.urls import path
from . import views

app_name = "jobs"

urlpatterns = [

    # Job list
    path(
        "",
        views.job_list,
        name="job_list"
    ),

    # Job detail
    path(
        "<int:job_id>/",
        views.job_detail,
        name="job_detail"
    ),

    # Apply on GeoCareerGo
    path(
        "<int:job_id>/apply/",
        views.apply_job,
        name="apply_job"
    ),
]