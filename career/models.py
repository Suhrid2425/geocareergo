from django.db import models
from django.utils.text import slugify


class Article(models.Model):
    CATEGORY_CHOICES = [
        ("career", "Career Guide"),
        ("jobs", "Jobs"),
        ("internship", "Internships"),
        ("skills", "Skills"),
        ("interview", "Interview Preparation"),
        ("education", "Education"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=220)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="career",
    )
    excerpt = models.TextField(max_length=300)
    content = models.TextField()

    featured_image = models.ImageField(
        upload_to="career/",
        blank=True,
        null=True,
    )

    author = models.CharField(max_length=100, default="GeoCareerGo")
    is_published = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title