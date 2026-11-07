import datetime as dt
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from dmr import APIError, Body, Controller, ResponseSpec, modify
from dmr.plugins.pydantic import PydanticFastSerializer
from dmr.security import AuthenticatedHttpRequest
from dmr.security.jwt import views
from dmr.security.jwt.token import JWToken
from typing_extensions import override

from users.constants import AuthErrorCode
from users.schemas import MessageResponse, RegisterRequest, UserResponse
from users.tokens import blacklist_token, is_token_blacklisted, jwt_auth

User = get_user_model()


class RegisterController(Controller[PydanticFastSerializer]):
    """Регистрация нового пользователя в системе."""

    tags = ["Auth"]
    summary = "Регистрация нового пользователя"

    @modify(
        extra_responses=[
            ResponseSpec(
                return_type=Controller.error_model,
                status_code=HTTPStatus.BAD_REQUEST,
            ),
        ],
    )
    def post(self, parsed_body: Body[RegisterRequest]) -> UserResponse:
        """Создать новую учетную запись пользователя с уникальными username и email."""
        if User.objects.filter(username=parsed_body.username).exists():
            raise APIError(
                self.format_error(
                    "Пользователь с таким именем пользователя уже существует",
                    loc=["parsed_body", "username"],
                    error_type=AuthErrorCode.USERNAME_EXISTS,
                ),
                status_code=HTTPStatus.BAD_REQUEST,
            )

        if parsed_body.email and User.objects.filter(email=parsed_body.email).exists():
            raise APIError(
                self.format_error(
                    "Пользователь с таким email уже существует",
                    loc=["parsed_body", "email"],
                    error_type=AuthErrorCode.EMAIL_EXISTS,
                ),
                status_code=HTTPStatus.BAD_REQUEST,
            )

        user = User.objects.create_user(
            username=parsed_body.username,
            password=parsed_body.password,
            email=parsed_body.email or "",
            first_name=parsed_body.first_name,
            last_name=parsed_body.last_name,
        )
        return UserResponse.model_validate(user)


class TokenRefreshController(
    views.RefreshTokenSyncController[
        PydanticFastSerializer,
        views.RefreshTokenPayload,
        views.ObtainTokensResponse,
    ],
):
    """Обновление пары токенов с ротацией refresh токена и занесением старого в blacklist."""

    tags = ["Auth"]
    summary = "Обновление пары токенов с ротацией refresh"
    auth = None
    jwt_expiration = settings.JWT_ACCESS_TOKEN_LIFETIME
    jwt_refresh_expiration = settings.JWT_REFRESH_TOKEN_LIFETIME
    jwt_algorithm = settings.JWT_ALGORITHM

    @override
    def convert_refresh_payload(self, payload: views.RefreshTokenPayload) -> str:
        return payload["refresh_token"]

    @override
    def make_api_response(self) -> views.ObtainTokensResponse:
        now = dt.datetime.now(dt.UTC)
        return {
            "access_token": self.create_jwt_token(
                expiration=now + self.jwt_expiration,
                token_type="access",
            ),
            "refresh_token": self.create_jwt_token(
                expiration=now + self.jwt_refresh_expiration,
                token_type="refresh",
            ),
        }

    @override
    def check_auth(self, user: AbstractBaseUser, token: JWToken) -> None:
        super().check_auth(user, token)
        if token.jti and is_token_blacklisted(token.jti):
            raise APIError(
                self.format_error(
                    "Токен находится в чёрном списке",
                    loc=["parsed_body", "refresh_token"],
                    error_type=AuthErrorCode.TOKEN_BLACKLISTED,
                ),
                status_code=HTTPStatus.UNAUTHORIZED,
            )

    @override
    def refresh(self, parsed_body: views.RefreshTokenPayload) -> views.ObtainTokensResponse:
        """Валидировать refresh-токен, отозвать старый и выдать новую пару токенов."""
        token = self._decode_and_validate_refresh_token(
            self.convert_refresh_payload(parsed_body),
        )
        user = self.get_user(token)
        self.check_auth(user, token)
        if token.jti:
            blacklist_token(token.jti, token.exp)
        self.set_request_attrs(self.request, user)
        return self.make_api_response()


class TokenBlacklistController(Controller[PydanticFastSerializer]):
    """Выход из системы: отзыв refresh токена с добавлением его в чёрный список Redis."""

    tags = ["Auth"]
    summary = "Выход из системы (добавление refresh токена в blacklist)"

    @modify(
        status_code=HTTPStatus.OK,
        extra_responses=[
            ResponseSpec(
                return_type=Controller.error_model,
                status_code=HTTPStatus.BAD_REQUEST,
            ),
        ],
    )
    def post(self, parsed_body: Body[views.RefreshTokenPayload]) -> MessageResponse:
        """Аннулировать переданный refresh-токен и занести его в черный список Redis."""
        try:
            token = JWToken.decode(
                encoded_token=parsed_body["refresh_token"],
                secret=settings.SECRET_KEY,
                algorithm=settings.JWT_ALGORITHM,
            )
            if token.extras.get("type") != "refresh":
                raise ValueError("Токен не является refresh токеном")
            if token.jti:
                blacklist_token(token.jti, token.exp)
        except Exception as err:
            raise APIError(
                self.format_error(
                    f"Не удалось аннулировать токен: {err}",
                    loc=["parsed_body", "refresh_token"],
                    error_type=AuthErrorCode.INVALID_TOKEN,
                ),
                status_code=HTTPStatus.BAD_REQUEST,
            ) from err

        return MessageResponse(detail="Токен успешно добавлен в чёрный список")


class MeController(Controller[PydanticFastSerializer]):
    """Получение профиля текущего аутентифицированного пользователя."""

    tags = ["Users"]
    summary = "Получение профиля текущего пользователя"
    auth = [jwt_auth]
    request: AuthenticatedHttpRequest[User]

    def get(self) -> UserResponse:
        """Получить информацию о текущем авторизованном пользователе."""
        return UserResponse.model_validate(self.request.user)
