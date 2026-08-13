from django.contrib import admin

from .models import Job, JobApplication


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):

    # ==================================================
    # JOB LIST
    # ==================================================

    list_display = (
        "title",
        "organization",
        "job_type",
        "degree",
        "min_experience",
        "max_experience",
        "application_type",
        "location",
        "last_date",
        "is_active",
    )

    # ==================================================
    # FILTERS
    # ==================================================

    list_filter = (
        "job_type",
        "degree",
        "application_type",
        "is_active",
    )

    # ==================================================
    # SEARCH
    # ==================================================

    search_fields = (
        "title",
        "organization",
        "location",
        "qualification",
        "description",
    )

    # ==================================================
    # FORM ORGANIZATION
    # ==================================================

    fieldsets = (

        (
            "Job Information",
            {
                "fields": (
                    "title",
                    "organization",
                    "location",
                    "job_type",
                )
            }
        ),

        (
            "Education",
            {
                "fields": (
                    "degree",
                    "qualification",
                )
            }
        ),

        (
            "Experience",
            {
                "fields": (
                    "min_experience",
                    "max_experience",
                )
            }
        ),

        (
            "Job Details",
            {
                "fields": (
                    "salary",
                    "description",
                )
            }
        ),

        (
            "Application",
            {
                "fields": (
                    "application_type",
                    "application_url",
                )
            }
        ),

        (
            "Deadline & Status",
            {
                "fields": (
                    "last_date",
                    "is_active",
                )
            }
        ),

    )

    ordering = (
        "-created_at",
    )


# ==================================================
# JOB APPLICATION
# ==================================================

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):

    list_display = (
        "job",
        "applicant",
        "status",
        "applied_at",
    )

    list_filter = (
        "status",
        "applied_at",
    )

    search_fields = (
        "job__title",
        "job__organization",
        "applicant__username",
        "applicant__email",
    )

    readonly_fields = (
        "job",
        "applicant",
        "phone",
        "resume",
        "cover_message",
        "applied_at",
        "updated_at",
    )

    ordering = (
        "-applied_at",
    )