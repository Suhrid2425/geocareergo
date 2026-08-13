from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, render

from .models import Note, Subject, Purchase


def note_list(request):

    notes = Note.objects.filter(
        is_active=True
    ).select_related(
        "subject_obj"
    ).order_by("-created_at")


    # Search
    search = request.GET.get("q", "").strip()

    if search:
        notes = (
            notes.filter(title__icontains=search)
            | notes.filter(subject__icontains=search)
            | notes.filter(subject_obj__name__icontains=search)
            | notes.filter(description__icontains=search)
        )


    # Category
    category = request.GET.get("category", "").strip()

    if category:
        notes = notes.filter(
            category=category
        )


    # Free / Premium
    access_type = request.GET.get("access", "").strip()

    if access_type:
        notes = notes.filter(
            access_type=access_type
        )


    # Subject
    subject_id = request.GET.get("subject", "").strip()

    if subject_id:
        notes = notes.filter(
            subject_obj_id=subject_id
        )


    notes = notes.distinct()


    # Pagination
    paginator = Paginator(
        notes,
        9
    )

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(
        page_number
    )


    # Subjects for dropdown
    subjects = Subject.objects.filter(
        is_active=True
    ).order_by("name")


    return render(
        request,
        "notes/note_list.html",
        {
            "notes": page_obj,
            "page_obj": page_obj,
            "subjects": subjects,

            "search": search,
            "selected_category": category,
            "selected_access": access_type,
            "selected_subject": subject_id,
        }
    )


def note_detail(request, note_id):

    note = get_object_or_404(
        Note.objects.select_related(
            "subject_obj"
        ),
        id=note_id,
        is_active=True
    )

    return render(
        request,
        "notes/note_detail.html",
        {
            "note": note
        }
    )




@login_required
def download_note(request, note_id):

    note = get_object_or_404(
        Note,
        id=note_id,
        is_active=True
    )

    # FREE NOTE
    if note.access_type == "free":

        if not note.pdf_file:
            raise Http404("PDF not available.")

        return FileResponse(
            note.pdf_file.open("rb"),
            as_attachment=False,
            filename=note.pdf_file.name.split("/")[-1]
        )


    # PREMIUM NOTE
    has_purchased = Purchase.objects.filter(
        user=request.user,
        note=note,
        is_active=True
    ).exists()


    if not has_purchased:

        return render(
            request,
            "notes/premium_required.html",
            {
                "note": note
            }
        )


    # PURCHASED
    if not note.pdf_file:
        raise Http404("PDF not available.")

    return FileResponse(
        note.pdf_file.open("rb"),
        as_attachment=False,
        filename=note.pdf_file.name.split("/")[-1]
    )