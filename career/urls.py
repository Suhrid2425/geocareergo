from django.urls import path

from . import views


app_name = "career"

urlpatterns = [
    path("", views.career_home, name="home"),
    path(
        "article/<slug:slug>/",
        views.article_detail,
        name="article_detail",
    ),
]