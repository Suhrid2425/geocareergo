from django.contrib import admin

from .models import (
    Test,
    Question,
    TestAttempt,
    TestAnswer,
    TestPurchase,
    Doubt,
)


# ==========================================
# QUESTION INLINE
# ==========================================

class QuestionInline(admin.TabularInline):

    model = Question

    extra = 1

    fields = (
        "order",
        "question_text",
        "option_a",
        "option_b",
        "option_c",
        "option_d",
        "correct_answer",
        "marks",
        "negative_marks",
    )

    ordering = (
        "order",
    )


# ==========================================
# TEST
# ==========================================

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "category",
        "test_type",
        "is_free",
        "price",
        "duration_minutes",
        "total_marks",
        "is_active",
        "created_at",
    )

    list_filter = (
        "category",
        "test_type",
        "is_free",
        "is_active",
    )

    search_fields = (
        "title",
        "description",
    )

    ordering = (
        "-created_at",
    )

    inlines = [
        QuestionInline,
    ]

    fieldsets = (

        (
            "Basic Information",
            {
                "fields": (
                    "title",
                    "category",
                    "test_type",
                    "description",
                )
            }
        ),

        (
            "Test Settings",
            {
                "fields": (
                    "duration_minutes",
                    "total_marks",
                )
            }
        ),

        (
            "Access & Pricing",
            {
                "fields": (
                    "is_free",
                    "price",
                )
            }
        ),

        (
            "Status",
            {
                "fields": (
                    "is_active",
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

    readonly_fields = (
        "created_at",
        "updated_at",
    )


# ==========================================
# QUESTION
# ==========================================

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):

    list_display = (
        "test",
        "order",
        "short_question",
        "correct_answer",
        "marks",
        "negative_marks",
    )

    list_filter = (
        "test",
        "correct_answer",
    )

    search_fields = (
        "question_text",
        "test__title",
    )

    ordering = (
        "test",
        "order",
    )

    def short_question(self, obj):

        if len(obj.question_text) > 70:
            return obj.question_text[:70] + "..."

        return obj.question_text

    short_question.short_description = "Question"


# ==========================================
# TEST ATTEMPT
# ==========================================

@admin.register(TestAttempt)
class TestAttemptAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "test",
        "score",
        "percentage",
        "is_completed",
        "started_at",
        "submitted_at",
    )

    list_filter = (
        "is_completed",
        "test",
    )

    search_fields = (
        "user__username",
        "test__title",
    )

    readonly_fields = (
        "started_at",
    )

    ordering = (
        "-started_at",
    )


# ==========================================
# TEST ANSWER
# ==========================================

@admin.register(TestAnswer)
class TestAnswerAdmin(admin.ModelAdmin):

    list_display = (
        "attempt",
        "question",
        "selected_answer",
        "is_correct",
        "marks_obtained",
    )

    list_filter = (
        "is_correct",
        "selected_answer",
    )

    search_fields = (
        "attempt__user__username",
        "question__question_text",
    )


# ==========================================
# TEST PURCHASE
# ==========================================

@admin.register(TestPurchase)
class TestPurchaseAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "test",
        "is_active",
        "purchased_at",
    )

    list_filter = (
        "is_active",
        "test",
    )

    search_fields = (
        "user__username",
        "test__title",
    )

    ordering = (
        "-purchased_at",
    )


# ==========================================
# DOUBT
# ==========================================

@admin.register(Doubt)
class DoubtAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "test",
        "status",
        "created_at",
        "answered_at",
    )

    list_filter = (
        "status",
        "test",
    )

    search_fields = (
        "user__username",
        "test__title",
        "doubt_text",
        "faculty_answer",
    )

    readonly_fields = (
        "created_at",
    )

    fieldsets = (

        (
            "Student",
            {
                "fields": (
                    "user",
                    "test",
                    "question",
                )
            }
        ),

        (
            "Doubt",
            {
                "fields": (
                    "doubt_text",
                    "image",
                )
            }
        ),

        (
            "Faculty Response",
            {
                "fields": (
                    "faculty_answer",
                    "status",
                    "answered_at",
                )
            }
        ),

        (
            "Timestamp",
            {
                "fields": (
                    "created_at",
                )
            }
        ),

    )