from django.db import models
from django.contrib.auth.models import User


class StudentProfile(models.Model):

    DEGREE_CHOICES = [
        ("btech", "B.Tech"),
        ("be", "B.E."),
        ("bsc", "B.Sc."),
        ("msc", "M.Sc."),
        ("mtech", "M.Tech"),
        ("ma", "M.A."),
        ("phd", "Ph.D."),
        ("other", "Other"),
    ]

    YEAR_CHOICES = [
        ("1", "1st Year"),
        ("2", "2nd Year"),
        ("3", "3rd Year"),
        ("4", "4th Year"),
        ("graduated", "Graduated"),
    ]

    SEMESTER_CHOICES = [
        ("1", "1st Semester"),
        ("2", "2nd Semester"),
        ("3", "3rd Semester"),
        ("4", "4th Semester"),
        ("5", "5th Semester"),
        ("6", "6th Semester"),
        ("7", "7th Semester"),
        ("8", "8th Semester"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="student_profile"
    )

    full_name = models.CharField(
        max_length=150,
        blank=True
    )

    degree = models.CharField(
        max_length=20,
        choices=DEGREE_CHOICES,
        blank=True
    )

    branch = models.CharField(
        max_length=100,
        blank=True
    )

    college = models.CharField(
        max_length=200,
        blank=True
    )

    year = models.CharField(
        max_length=20,
        choices=YEAR_CHOICES,
        blank=True
    )

    semester = models.CharField(
        max_length=20,
        choices=SEMESTER_CHOICES,
        blank=True
    )

    graduation_year = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    career_interest = models.CharField(
        max_length=100,
        blank=True
    )

    exam_interest = models.CharField(
        max_length=100,
        blank=True
    )

    profile_completed = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.user.username