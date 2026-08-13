from django.urls import path
from . import views


app_name = "notes"


urlpatterns = [

    path(
        "",
        views.note_list,
        name="note_list"
    ),

    path(
        "<int:note_id>/",
        views.note_detail,
        name="note_detail"
    ),

    path(
        "<int:note_id>/download/",
        views.download_note,
        name="download_note"
    ),

]