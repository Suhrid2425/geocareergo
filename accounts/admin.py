from django.contrib import admin

from .models import StudentProfile, CompanyProfile


# ==========================================================
# STUDENT PROFILE
# ==========================================================

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "full_name",
        "degree",
        "college",
        "year",
        "profile_completed",
    )

    list_filter = (
        "degree",
        "year",
        "profile_completed",
    )

    search_fields = (
        "user__username",
        "user__email",
        "full_name",
        "college",
        "branch",
    )


# ==========================================================
# COMPANY PROFILE
# ==========================================================

@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):

    list_display = (
        "company_name",
        "company_email",
        "verification_status",
        "created_at",
    )

    list_filter = (
        "verification_status",
    )

    search_fields = (
        "company_name",
        "company_email",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Company Information",
            {
                "fields": (
                    "user",
                    "company_name",
                    "logo",
                    "website",
                    "linkedin_url",
                    "company_email",
                    "executive_linkedin_url",
                )
            }
        ),

        (
            "Verification",
            {
                "fields": (
                    "registration_document",
                    "verification_status",
                )
            }
        ),

        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            }
        ),
    )