import datetime as dt

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.core.cache import caches
from dmr.exceptions import NotAuthenticatedError
from dmr.security.jwt import HeaderJWTSyncAuth, JWToken

cache = caches["blacklist"]


def blacklist_token(jti: str, exp: dt.datetime | None = None) -> None:
    """Добавить JTI токена в черный список в Redis."""
    timeout = int(settings.JWT_REFRESH_TOKEN_LIFETIME.total_seconds())
    if exp is not None:
        remaining = int((exp - dt.datetime.now(dt.UTC)).total_seconds())
        if remaining > 0:
            timeout = remaining
    cache.set(f"jwt:blacklist:{jti}", True, timeout=timeout)


def is_token_blacklisted(jti: str) -> bool:
    """Проверить, находится ли JTI токена в черном списке в Redis."""
    return bool(cache.get(f"jwt:blacklist:{jti}"))


class JWTAuth(HeaderJWTSyncAuth):
    """Синхронная аутентификация по JWT с проверкой чёрного списка в Redis."""

    def __init__(self, **kwargs) -> None:
        kwargs.setdefault("algorithm", settings.JWT_ALGORITHM)
        super().__init__(**kwargs)

    def check_auth(self, user: AbstractBaseUser, token: JWToken) -> None:
        super().check_auth(user, token)
        if token.jti and is_token_blacklisted(token.jti):
            raise NotAuthenticatedError


jwt_auth = JWTAuth()
