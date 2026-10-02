from django.contrib import admin

from .models import Job, JobApplication


# ==========================================================
# JOB
# ==========================================================

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "company_name",
        "company",
        "job_type",
        "degree",
        "min_experience",
        "max_experience",
        "application_type",
        "location",
        "last_date",
        "is_active",
        "is_trending",
    )

    list_filter = (
        "job_type",
        "degree",
        "application_type",
        "is_active",
        "is_trending",
    )

    search_fields = (
        "title",
        "company_name",
        "company__company_name",
        "location",
        "qualification",
        "description",
    )

    fieldsets = (

        (
            "Job Information",
            {
                "fields": (
                    "title",
                    "company_name",
                    "company_logo",
                    "company",
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
            },
        ),

        (
            "Job Details",
            {
                "fields": (
                    "salary",
                    "description",
                )
            },
        ),

        (
            "Application",
            {
                "fields": (
                    "application_type",
                    "application_url",
                )
            },
        ),

        (
            "Deadline & Status",
            {
                "fields": (
                    "last_date",
                    "is_active",
                    "is_trending",
                )
            },
        ),
    )

    ordering = (
        "-created_at",
    )


# ==========================================================
# JOB APPLICATION
# ==========================================================

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
        "job__company_name",
        "job__company__company_name",
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