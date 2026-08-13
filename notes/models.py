from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


class Subject(models.Model):

    name = models.CharField(
        max_length=150,
        unique=True
    )

    description = models.TextField(
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name


class Note(models.Model):

    CATEGORY_CHOICES = [
        ("gate", "GATE"),
        ("jam", "JAM"),
        ("psu", "PSU Preparation"),
        ("subject", "Subject Notes"),
    ]

    ACCESS_CHOICES = [
        ("free", "Free"),
        ("paid", "Premium"),
    ]

    title = models.CharField(max_length=200)

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )

    # Old subject text field.
    # We keep this temporarily so existing notes remain safe.
    subject = models.CharField(
        max_length=150,
        blank=True
    )

    # New proper subject relationship.
    subject_obj = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notes"
    )

    description = models.TextField(
        blank=True
    )

    pdf_file = models.FileField(
        upload_to="notes/"
    )

    access_type = models.CharField(
        max_length=10,
        choices=ACCESS_CHOICES,
        default="free"
    )

    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )

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

    def get_absolute_url(self):
        return reverse(
            "notes:note_detail",
            args=[self.id]
        )

    @property
    def subject_name(self):
        if self.subject_obj:
            return self.subject_obj.name

        return self.subject


class Purchase(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="note_purchases"
    )

    note = models.ForeignKey(
        Note,
        on_delete=models.CASCADE,
        related_name="purchases"
    )

    purchased_at = models.DateTimeField(
        auto_now_add=True
    )

    is_active = models.BooleanField(
        default=True
    )

    class Meta:
        unique_together = (
            "user",
            "note",
        )

    def __str__(self):
        return f"{self.user.username} - {self.note.title}"