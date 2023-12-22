from django.conf import settings
from django.core.cache import caches
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.views import TokenViewBase

from users.serializers import (
    TokenBlacklistSerializer,
    TokenRefreshSerializerWithBlacklist,
)

cache = caches["blacklist"]


class BlacklistTokenView(TokenViewBase):
    """
    Выход из системы, добавление refresh JWT в чёрный список.
    """

    serializer_class = TokenBlacklistSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        token = serializer.validated_data["refresh"]
        token_in_cache = cache.get(token)

        if token_in_cache:
            return Response(
                {"error": "token already blacklisted"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            cache.set(
                token,
                True,
                settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds(),
            )

            return Response(serializer.validated_data, status=status.HTTP_200_OK)


class TokenRefreshViewWithBlacklist(TokenViewBase):
    """
    Takes a refresh type JSON web token and returns an access type JSON web
    token if the refresh token is valid.
    """

    serializer_class = TokenRefreshSerializerWithBlacklist
