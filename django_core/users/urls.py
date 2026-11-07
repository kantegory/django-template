from django.conf import settings
from dmr.plugins.pydantic import PydanticFastSerializer
from dmr.routing import path
from dmr.security.jwt import concrete_views

from users.views import (
    MeController,
    RegisterController,
    TokenBlacklistController,
    TokenRefreshController,
)

urlpatterns = [
    path("register/", RegisterController.as_view(), name="register"),
    path(
        "login/",
        concrete_views.ObtainTokensSyncController.as_view(
            serializer=PydanticFastSerializer,
            jwt_expiration=settings.JWT_ACCESS_TOKEN_LIFETIME,
            jwt_refresh_expiration=settings.JWT_REFRESH_TOKEN_LIFETIME,
            jwt_algorithm=settings.JWT_ALGORITHM,
        ),
        name="login",
    ),
    path(
        "jwt/refresh/",
        TokenRefreshController.as_view(),
        name="jwt_refresh",
    ),
    path(
        "jwt/verify/",
        concrete_views.VerifyTokenSyncController.as_view(
            serializer=PydanticFastSerializer,
            jwt_algorithm=settings.JWT_ALGORITHM,
        ),
        name="jwt_verify",
    ),
    path(
        "jwt/blacklist/",
        TokenBlacklistController.as_view(),
        name="jwt_blacklist",
    ),
    path("me/", MeController.as_view(), name="me"),
]
