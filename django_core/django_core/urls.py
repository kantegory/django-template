from django.contrib import admin
from django.conf import settings
from django.urls import path, include

api_urlpatterns = [
    path("auth/", include("users.urls")),
]

internal_urlpatterns = [
    path("admin/", admin.site.urls),
    path("tinymce/", include("tinymce.urls")),

    path(settings.API_PREFIX, include(api_urlpatterns)),
]

urlpatterns = [
    path(
        settings.BASE_URL,
        include(internal_urlpatterns)
    ),
]
