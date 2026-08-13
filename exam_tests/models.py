from django.contrib.auth.models import User
from django.db import models


class Test(models.Model):

    TEST_TYPE_CHOICES = [
        ("pyq", "Previous Year Paper"),
        ("practice", "Practice Quiz"),
        ("series", "Test Series"),
    ]

    CATEGORY_CHOICES = [
        ("gate", "GATE"),
        ("jam", "JAM"),
        ("psu", "PSU"),
        ("net", "NET"),
        ("govt", "Government Exams"),
        ("reasoning", "Reasoning"),
        ("aptitude", "Aptitude"),
        ("verbal", "Verbal"),
        ("other", "Other PYQs"),
    ]

    title = models.CharField(
        max_length=200
    )

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )

    test_type = models.CharField(
        max_length=20,
        choices=TEST_TYPE_CHOICES
    )

    description = models.TextField(
        blank=True
    )

    duration_minutes = models.PositiveIntegerField(
        default=30
    )

    total_marks = models.PositiveIntegerField(
        default=0
    )

    is_free = models.BooleanField(
        default=True
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

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Question(models.Model):

    ANSWER_CHOICES = [
        ("A", "Option A"),
        ("B", "Option B"),
        ("C", "Option C"),
        ("D", "Option D"),
    ]

    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name="questions"
    )

    question_text = models.TextField()

    option_a = models.CharField(
        max_length=500
    )

    option_b = models.CharField(
        max_length=500
    )

    option_c = models.CharField(
        max_length=500
    )

    option_d = models.CharField(
        max_length=500
    )

    correct_answer = models.CharField(
        max_length=1,
        choices=ANSWER_CHOICES
    )

    explanation = models.TextField(
        blank=True
    )

    marks = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1
    )

    negative_marks = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    order = models.PositiveIntegerField(
        default=1
    )

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.test.title} - Q{self.order}"


class TestAttempt(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="test_attempts"
    )

    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name="attempts"
    )

    started_at = models.DateTimeField(
        auto_now_add=True
    )

    submitted_at = models.DateTimeField(
        null=True,
        blank=True
    )

    score = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )

    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    is_completed = models.BooleanField(
        default=False
    )

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.user.username} - {self.test.title}"


class TestAnswer(models.Model):

    attempt = models.ForeignKey(
        TestAttempt,
        on_delete=models.CASCADE,
        related_name="answers"
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="attempt_answers"
    )

    selected_answer = models.CharField(
        max_length=1,
        choices=Question.ANSWER_CHOICES,
        blank=True
    )

    is_correct = models.BooleanField(
        default=False
    )

    marks_obtained = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    class Meta:
        unique_together = (
            "attempt",
            "question",
        )

    def __str__(self):
        return f"{self.attempt} - Q{self.question.order}"


class TestPurchase(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="test_purchases"
    )

    test = models.ForeignKey(
        Test,
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
            "test",
        )

    def __str__(self):
        return f"{self.user.username} - {self.test.title}"


class Doubt(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("answered", "Answered"),
        ("closed", "Closed"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="test_doubts"
    )

    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name="doubts"
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="doubts"
    )

    doubt_text = models.TextField()

    image = models.ImageField(
        upload_to="doubts/",
        blank=True,
        null=True
    )

    faculty_answer = models.TextField(
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    answered_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.test.title}"