from django.contrib import admin
from django.conf import settings
from django.urls import include
from dmr.openapi import build_schema
from dmr.openapi.views import OpenAPIJsonView, SwaggerView
from dmr.plugins.pydantic import PydanticFastSerializer
from dmr.routing import Router, build_404_handler, build_500_handler, include as dmr_include, path

api_router = Router(
    prefix=settings.API_PREFIX,
    urls=[
        path("auth/", dmr_include("users.urls")),
    ],
)

api_schema = build_schema(api_router)

internal_urlpatterns = [
    path("admin/", admin.site.urls),
    path("tinymce/", include("tinymce.urls")),
    api_router.to_urlpatterns(namespace="api"),
    path(f"{settings.API_PREFIX}docs/schema.json", OpenAPIJsonView.as_view(schema=api_schema), name="openapi-json"),
    path(f"{settings.API_PREFIX}docs/swagger/", SwaggerView.as_view(schema=api_schema), name="swagger-ui"),
]

if settings.BASE_URL:
    urlpatterns = [path(settings.BASE_URL, include(internal_urlpatterns))]
else:
    urlpatterns = internal_urlpatterns

handler404 = build_404_handler(api_router.prefix, serializer=PydanticFastSerializer)
handler500 = build_500_handler(api_router.prefix, serializer=PydanticFastSerializer)
