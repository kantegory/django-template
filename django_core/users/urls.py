from django.urls import include, path

from users.views import (
    BlacklistTokenView,
    TokenRefreshViewWithBlacklist,
)

app_name = "users"

urlpatterns = [
    path("jwt/blacklist/", BlacklistTokenView.as_view()),
    path("jwt/refresh/", TokenRefreshViewWithBlacklist.as_view()),
    path("", include("djoser.urls.jwt")),
    path("", include("djoser.urls")),
]
