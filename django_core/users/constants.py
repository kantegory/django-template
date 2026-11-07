from enum import StrEnum


class AuthErrorCode(StrEnum):
    """Машиночитаемые коды ошибок модуля аутентификации и пользователей."""

    USERNAME_EXISTS = "username_exists"
    EMAIL_EXISTS = "email_exists"
    INVALID_TOKEN = "invalid_token"
    TOKEN_BLACKLISTED = "token_blacklisted"
    INVALID_CREDENTIALS = "invalid_credentials"
