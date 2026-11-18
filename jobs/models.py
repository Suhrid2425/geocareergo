
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
        ("email", "Email Application"),
        ("internal", "Apply on GeoCareerGo"),
    ]

    # ==================================================
    # BASIC JOB INFORMATION
    # ==================================================

    title = models.CharField(max_length=200)

    company_name = models.CharField(
        max_length=200,
        blank=True,
        default=""
    )

    company_logo = models.ImageField(
        upload_to="job_company_logos/",
        blank=True,
        null=True
    )

    company = models.ForeignKey(
        "accounts.CompanyProfile",
        on_delete=models.SET_NULL,
        related_name="jobs",
        null=True,
        blank=True,
    )

    location = models.CharField(max_length=200)

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
    # SEO & ORIGINAL SOURCE
    # ==================================================

    seo_title = models.CharField(
        max_length=70,
        blank=True,
        help_text="Optional custom SEO title."
    )

    meta_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="Optional custom meta description."
    )

    source_url = models.URLField(
        blank=True,
        help_text="Original employer job posting URL."
    )

    # ==================================================
    # APPLICATION
    # ==================================================

    application_type = models.CharField(
        max_length=20,
        choices=APPLICATION_TYPES,
        default="external"
    )

    application_url = models.URLField(blank=True)

    application_email = models.EmailField(
        blank=True,
        help_text="Email address where applicants should send their CV."
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

    is_active = models.BooleanField(default=True)

    is_trending = models.BooleanField(
        default=False,
        help_text="Show this job in the Trending Jobs section on the homepage."
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    # ==================================================
    # SEO PROPERTIES
    # ==================================================

    @property
    def get_seo_title(self):
        if self.seo_title:
            return self.seo_title

        employer = self.company_name or "Employer"

        return f"{self.title} at {employer} | GeoCareerGo"

    @property
    def get_meta_description(self):
        if self.meta_description:
            return self.meta_description

        experience = (
            self.experience_display
            if self.min_experience is not None
            else "Check experience requirements"
        )

        employer = self.company_name or "the employer"

        description = (
            f"Explore {self.title} at {employer} in {self.location}. "
            f"{experience}. Check qualifications and application details."
        )

        return description[:160]

    # ==================================================
    # EXPERIENCE DISPLAY
    # ==================================================

    @property
    def experience_display(self):

        minimum = self.min_experience
        maximum = self.max_experience

        if minimum is None and maximum is None:
            return "Not specified"

        if minimum is not None and maximum is None:
            return f"{minimum}+ years"

        if minimum is None and maximum is not None:
            return f"Up to {maximum} years"

        if minimum == maximum:
            return f"{minimum} years"

        return f"{minimum}-{maximum} years"

    # ==================================================
    # JOB STATUS
    # ==================================================

    @property
    def is_expired(self):
        from django.utils import timezone

        if self.last_date is None:
            return False

        return self.last_date < timezone.localdate()

    # ==================================================
    # STRING REPRESENTATION
    # ==================================================

    def __str__(self):
        return self.title

    # ==================================================
    # META
    # ==================================================

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Job"
        verbose_name_plural = "Jobs"


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

    phone = models.CharField(max_length=20)

    resume = models.FileField(upload_to="resumes/")

    cover_message = models.TextField(blank=True)

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

    applied_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    # ==================================================
    # META
    # ==================================================

    class Meta:

        ordering = ["-applied_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["job", "applicant"],
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
