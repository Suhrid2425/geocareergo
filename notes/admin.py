from django.contrib import admin
from .models import Note, Subject, Purchase


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "description",
    )

    ordering = (
        "name",
    )


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "category",
        "subject_obj",
        "subject",
        "access_type",
        "price",
        "is_active",
        "created_at",
    )

    list_filter = (
        "category",
        "access_type",
        "is_active",
        "subject_obj",
    )

    search_fields = (
        "title",
        "subject",
        "subject_obj__name",
        "description",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "note",
        "purchased_at",
        "is_active",
    )

    list_filter = (
        "is_active",
        "purchased_at",
    )

    search_fields = (
        "user__username",
        "note__title",
    )

    ordering = (
        "-purchased_at",
    )