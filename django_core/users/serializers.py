from django.core.cache import caches
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

cache = caches["blacklist"]


class TokenBlacklistSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):

        refresh = RefreshToken(attrs["refresh"])
        data = {"refresh": str(refresh)}

        return data


class TokenRefreshSerializerWithBlacklist(TokenRefreshSerializer):
    def validate(self, attrs):

        refresh = RefreshToken(attrs["refresh"])

        token_in_cache = cache.get(refresh)

        if token_in_cache:
            raise ValidationError("Token is blacklisted")

        data = {"access": str(refresh.access_token)}

        return data
