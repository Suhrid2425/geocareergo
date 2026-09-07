from django.conf import settings


def site_settings(request):

    return {
        "google_client_id": settings.GOOGLE_CLIENT_ID,
        "adsense_client_id": settings.ADSENSE_CLIENT_ID,
        "adsense_enabled": settings.ADSENSE_ENABLED,
    }