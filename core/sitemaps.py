from django.contrib import sitemaps
from django.urls import reverse

from jobs.models import Job


class StaticViewSitemap(sitemaps.Sitemap):

    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return [
            "homepage",
            "jobs",
        ]

    def location(self, item):

        locations = {
            "homepage": "/",
            "jobs": "/jobs/",
        }

        return locations[item]


class JobSitemap(sitemaps.Sitemap):

    priority = 0.9
    changefreq = "daily"

    def items(self):

        return (
            Job.objects
            .filter(is_active=True)
            .select_related("company")
            .order_by("-updated_at")
        )

    def location(self, obj):

        return reverse(
            "jobs:job_detail",
            kwargs={
                "job_id": obj.id
            }
        )

    def lastmod(self, obj):

        return obj.updated_at


sitemaps = {
    "static": StaticViewSitemap,
    "jobs": JobSitemap,
}