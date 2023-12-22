from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

api_urlpatterns = [
    path("auth/", include("users.urls")),

    # api docs
    path("docs/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "docs/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
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
