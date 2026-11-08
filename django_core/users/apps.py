from django.apps import AppConfig, apps
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"
    verbose_name = _("Пользователи")

    def ready(self):
        try:
            apps.get_app_config("constance").verbose_name = _("Конфигурация")
        except LookupError:
            pass

        try:
            apps.get_app_config("django_dramatiq").verbose_name = _("Dramatiq задачи")
        except LookupError:
            pass
