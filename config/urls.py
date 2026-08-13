from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [

    # Django Admin
    path(
        "admin/",
        admin.site.urls
    ),

    # Home / Core
    path(
        "",
        include("core.urls")
    ),

    # Jobs
    path(
        "jobs/",
        include("jobs.urls")
    ),

    # Notes
    path(
        "notes/",
        include("notes.urls")
    ),

    # Accounts
    path(
        "accounts/",
        include("accounts.urls")
    ),

    # Tests
    path(
        "tests/",
        include("exam_tests.urls")
    ),

]


# Media files during development

if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )