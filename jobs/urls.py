from django.urls import path
from . import views


app_name = "jobs"


urlpatterns = [

    # ==================================================
    # PUBLIC JOBS
    # ==================================================

    path(
        "",
        views.job_list,
        name="job_list"
    ),

    path(
        "<int:job_id>/",
        views.job_detail,
        name="job_detail"
    ),


    # ==================================================
    # STUDENT
    # ==================================================

    path(
        "<int:job_id>/apply/",
        views.apply_job,
        name="apply_job"
    ),


    # ==================================================
    # COMPANY
    # ==================================================

    # Post new job
    path(
        "post/",
        views.post_job,
        name="post_job"
    ),

    # Company's posted jobs
    path(
        "company/jobs/",
        views.company_jobs,
        name="company_jobs"
    ),

    # Edit job
    path(
        "company/jobs/<int:job_id>/edit/",
        views.edit_job,
        name="edit_job"
    ),

    # Delete job
    path(
        "company/jobs/<int:job_id>/delete/",
        views.delete_job,
        name="delete_job"
    ),

    # Activate / deactivate job
    path(
        "company/jobs/<int:job_id>/toggle/",
        views.toggle_job_status,
        name="toggle_job_status"
    ),

    # View applications
    path(
        "company/jobs/<int:job_id>/applications/",
        views.job_applications,
        name="job_applications"
    ),

    # Update application status
    path(
        "company/applications/<int:application_id>/status/",
        views.update_application_status,
        name="update_application_status"
    ),
]