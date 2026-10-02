from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from core.sitemaps import sitemaps


urlpatterns = [

    # ==================================================
    # Django Admin
    # ==================================================

    path(
        "admin/",
        admin.site.urls
    ),

    # ==================================================
    # Sitemap
    # ==================================================

    path(
        "sitemap.xml",
        sitemap,
        {
            "sitemaps": sitemaps
        },
        name="sitemap"
    ),

       # ==================================================
    # PWA
    # ==================================================

    path(
        "manifest.json",
        TemplateView.as_view(
            template_name="manifest.json",
            content_type="application/manifest+json",
        ),
        name="manifest",
    ),

    path(
        "service-worker.js",
        TemplateView.as_view(
            template_name="service-worker.js",
            content_type="application/javascript",
        ),
        name="service_worker",
    ),

        # ==================================================
    # PWA
    # ==================================================

    path(
        "manifest.json",
        TemplateView.as_view(
            template_name="manifest.json",
            content_type="application/manifest+json",
        ),
        name="manifest",
    ),

    path(
        "service-worker.js",
        TemplateView.as_view(
            template_name="service-worker.js",
            content_type="application/javascript",
        ),
        name="service_worker",
    ),

    # ==================================================
    # Home / Core
    # ==================================================

    path(
        "",
        include("core.urls")
    ),

    # ==================================================
    # Jobs
    # ==================================================

    path(
        "jobs/",
        include("jobs.urls")
    ),

    # ==================================================
    # Notes
    # ==================================================

    path(
        "notes/",
        include("notes.urls")
    ),

    # ==================================================
    # Accounts
    # ==================================================

    path(
        "accounts/",
        include("accounts.urls")
    ),

    # ==================================================
    # Tests
    # ==================================================

    path(
        "tests/",
        include("exam_tests.urls")
    ),
    path("career/", include("career.urls")),

]


# ==================================================
# Media files during development
# ==================================================

if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )