from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    """Схема запроса регистрации нового пользователя."""

    username: str = Field(min_length=3, max_length=150, description="Уникальное имя пользователя")
    password: str = Field(min_length=8, description="Пароль пользователя (не менее 8 символов)")
    email: EmailStr | None = Field(default=None, description="Адрес электронной почты")
    first_name: str = Field(default="", description="Имя пользователя")
    last_name: str = Field(default="", description="Фамилия пользователя")


class UserResponse(BaseModel):
    """Схема ответа с данными пользователя."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Уникальный идентификатор пользователя")
    username: str = Field(description="Имя пользователя")
    email: str = Field(description="Электронная почта пользователя")
    first_name: str = Field(description="Имя")
    last_name: str = Field(description="Фамилия")


class MessageResponse(BaseModel):
    """Схема ответа с текстовым сообщением."""

    detail: str = Field(description="Информационное сообщение")
