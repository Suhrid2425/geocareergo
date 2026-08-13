from django.db import models
from django.contrib.auth.models import User


class Job(models.Model):

    JOB_TYPES = [
        ("private", "Private"),
        ("government", "Government"),
        ("psu", "PSU"),
        ("internship", "Internship"),
    ]

    DEGREE_CHOICES = [
        ("any", "Any Degree"),
        ("bsc", "B.Sc"),
        ("msc", "M.Sc"),
        ("btech", "B.Tech"),
        ("mtech", "M.Tech"),
        ("ba", "B.A"),
        ("ma", "M.A"),
        ("phd", "Ph.D"),
        ("other", "Other"),
    ]

    APPLICATION_TYPES = [
        ("external", "External Website"),
        ("internal", "Apply on GeoCareerGo"),
    ]

    # ==================================================
    # BASIC JOB INFORMATION
    # ==================================================

    title = models.CharField(
        max_length=200
    )

    organization = models.CharField(
        max_length=200
    )

    location = models.CharField(
        max_length=200
    )

    job_type = models.CharField(
        max_length=20,
        choices=JOB_TYPES
    )

    # ==================================================
    # EDUCATION
    # ==================================================

    degree = models.CharField(
        max_length=20,
        choices=DEGREE_CHOICES,
        default="any"
    )

    qualification = models.TextField()

    # ==================================================
    # EXPERIENCE
    # ==================================================

    min_experience = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Minimum experience required in years."
    )

    max_experience = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum experience required in years."
    )

    # ==================================================
    # SALARY
    # ==================================================

    salary = models.CharField(
        max_length=100,
        blank=True
    )

    # ==================================================
    # DESCRIPTION
    # ==================================================

    description = models.TextField()

    # ==================================================
    # APPLICATION
    # ==================================================

    application_type = models.CharField(
        max_length=20,
        choices=APPLICATION_TYPES,
        default="external"
    )

    application_url = models.URLField(
        blank=True
    )

    # ==================================================
    # DEADLINE
    # ==================================================

    last_date = models.DateField(
        null=True,
        blank=True
    )

    # ==================================================
    # STATUS
    # ==================================================

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.title


# ==================================================
# JOB APPLICATION
# ==================================================

class JobApplication(models.Model):

    STATUS_CHOICES = [
        ("submitted", "Submitted"),
        ("reviewing", "Under Review"),
        ("shortlisted", "Shortlisted"),
        ("rejected", "Rejected"),
        ("selected", "Selected"),
    ]

    # ==================================================
    # JOB + APPLICANT
    # ==================================================

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="applications"
    )

    applicant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="job_applications"
    )

    # ==================================================
    # APPLICANT INFORMATION
    # ==================================================

    phone = models.CharField(
        max_length=20
    )

    # Resume uploaded by applicant
    resume = models.FileField(
        upload_to="resumes/"
    )

    cover_message = models.TextField(
        blank=True
    )

    # ==================================================
    # APPLICATION STATUS
    # ==================================================

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="submitted"
    )

    # ==================================================
    # DATES
    # ==================================================

    applied_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    # ==================================================
    # META
    # ==================================================

    class Meta:

        ordering = [
            "-applied_at"
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "job",
                    "applicant"
                ],
                name="unique_job_application"
            )
        ]

    # ==================================================
    # STRING
    # ==================================================

    def __str__(self):

        return (
            f"{self.applicant.username} - "
            f"{self.job.title}"
        )