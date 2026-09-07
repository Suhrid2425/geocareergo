from django.urls import path
from django.views.generic import TemplateView

from . import views


app_name = "core"


urlpatterns = [
    path("", views.home, name="home"),

    path(
        "mentorship/",
        views.mentorship,
        name="mentorship"
    ),

    path(
        "robots.txt",
        TemplateView.as_view(
            template_name="robots.txt",
            content_type="text/plain"
        ),
        name="robots"
    ),

    path(
        "about/",
        TemplateView.as_view(
            template_name="about.html"
        ),
        name="about"
    ),

    path(
        "contact/",
        TemplateView.as_view(
            template_name="contact.html"
        ),
        name="contact"
    ),

    path(
        "privacy-policy/",
        TemplateView.as_view(
            template_name="privacy_policy.html"
        ),
        name="privacy_policy"
    ),

    path(
        "terms/",
        TemplateView.as_view(
            template_name="terms.html"
        ),
        name="terms"
    ),
]