from http import HTTPStatus
import datetime as dt
from pathlib import Path
import environ
from dmr.settings import Settings

# Build paths inside the project like this: BASE_DIR / "subdir".
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env
env = environ.Env()
env.read_env(BASE_DIR / ".env")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str("SECRET_KEY")

# SECURITY WARNING: don"t run with debug turned on in production!
DEBUG = env.bool("DEBUG", False)

ALLOWED_HOSTS = ["*"]

# URL prefix
BASE_URL = env.str("BASE_URL", "")
API_PREFIX = env.str("API_PREFIX", "api/")

HOST = env.str("HOST", "http://localhost/")

# Application definition

# Django-specific apps
DJANGO_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

# External apps
THIRD_PARTY_APPS = [
    "corsheaders",
    "django_dramatiq",
    "dmr",
    "tinymce",
    "constance",
    "constance.backends.database",
]

# Internal apps
INTERNAL_APPS = [
    "users.apps.UsersConfig",
]

INSTALLED_APPS = [*DJANGO_APPS, *THIRD_PARTY_APPS, *INTERNAL_APPS]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "django_core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.static",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

WSGI_APPLICATION = "django_core.wsgi.application"

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": env.str("DB_ENGINE"),
        "NAME": env.str("POSTGRES_DB"),
        "USER": env.str("POSTGRES_USER"),
        "PASSWORD": env.str("POSTGRES_PASSWORD"),
        "HOST": env.str("POSTGRES_HOST"),
        "PORT": env.str("POSTGRES_PORT"),
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# CSRF settings
CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS",
    default=["http://localhost:1337", "http://127.0.0.1:1337"],
)

# CORS headers
# https://pypi.org/project/django-cors-headers/

CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=["http://localhost:8080", "http://127.0.0.1:8080"],
)

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT"
]


# Internationalization

LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Connection max age

CONN_MAX_AGE = None

# Static files (CSS, JavaScript, Images)

STATIC_URL = f"/{BASE_URL}static/"
STATIC_ROOT = BASE_DIR / "static"
STATICFILES_DIRS = [
    BASE_DIR / "static_source",
]

MEDIA_URL = f"/{BASE_URL}media/"
MEDIA_ROOT = BASE_DIR / "media"


# Redis

REDIS_HOST = env.str("REDIS_HOST")
REDIS_PORT = env.str("REDIS_PORT")

# Dramatiq
# https://django-dramatiq.readthedocs.io/

DRAMATIQ_BROKER = {
    "BROKER": "dramatiq.brokers.redis.RedisBroker",
    "OPTIONS": {
        "url": env.str("DRAMATIQ_BROKER_URL", f"redis://{REDIS_HOST}:{REDIS_PORT}/0"),
    },
    "MIDDLEWARE": [
        "dramatiq.middleware.AgeLimit",
        "dramatiq.middleware.TimeLimit",
        "dramatiq.middleware.Callbacks",
        "dramatiq.middleware.Pipelines",
        "dramatiq.middleware.Retries",
        "django_dramatiq.middleware.DbConnectionsMiddleware",
        "django_dramatiq.middleware.AdminMiddleware",
        "periodiq.PeriodiqMiddleware",
    ],
}

DRAMATIQ_AUTODISCOVER_MODULES = ["tasks"]

# Django Modern REST
# https://github.com/wemake-services/django-modern-rest

DMR_SETTINGS = {
    Settings.exclude_validate_responses: {
        HTTPStatus.BAD_REQUEST,
        HTTPStatus.UNAUTHORIZED,
        HTTPStatus.FORBIDDEN,
        HTTPStatus.NOT_FOUND,
        HTTPStatus.INTERNAL_SERVER_ERROR,
    },
}

# JWT Authentication
JWT_ACCESS_TOKEN_LIFETIME = dt.timedelta(
    minutes=env.int("JWT_ACCESS_TOKEN_LIFETIME_MINUTES", default=15)
)
JWT_REFRESH_TOKEN_LIFETIME = dt.timedelta(
    days=env.int("JWT_REFRESH_TOKEN_LIFETIME_DAYS", default=7)
)
JWT_ALGORITHM = env.str("JWT_ALGORITHM", default="HS256")

# Constance
# https://django-constance.readthedocs.io/en/latest/

CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"
CONSTANCE_DATABASE_CACHE_BACKEND = "default"

CONSTANCE_CONFIG = {
    "EXAMPLE_SETTING": (
        "Пример настройки",
        "Заголовок примера настройки",
        str,
    ),
}

CONSTANCE_CONFIG_FIELDSETS = {
    "Пример группы настроек": (
        "EXAMPLE_SETTING",
    ),
}

# Sentry

# if env.bool("USE_SENTRY", False):
#     import sentry_sdk
#     from sentry_sdk.integrations.django import DjangoIntegration
#     from sentry_sdk.integrations.logging import ignore_logger

#     SENTRY_DSN = env("SENTRY_DSN")
#     integrations = [DjangoIntegration()]
#     sentry_sdk.init(
#         dsn=SENTRY_DSN,
#         integrations=integrations,
#     )

#     ignore_logger("django.security.DisallowedHost")


# Log database queries (for optimization purposes)

if env.bool("LOG_DB_QUERIES", False):
    LOGGING = {
        "version": 1,
        "filters": {
            "require_debug_true": {
                "()": "django.utils.log.RequireDebugTrue",
            }
        },
        "handlers": {
            "console": {
                "level": "DEBUG",
                "filters": ["require_debug_true"],
                "class": "logging.StreamHandler",
            }
        },
        "loggers": {
            "django.db.backends": {
                "level": "DEBUG",
                "handlers": ["console"],
            }
        },
    }

# Cache
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    },
    "blacklist": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    },
    "endpoints": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/2",
        "TIMEOUT": 60 * 60 * 24,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    },
}

USE_ENDPOINT_CACHE = env.bool("USE_ENDPOINT_CACHE", True)


# S3
# https://pypi.org/project/django-storages/

S3_ENABLED = env.bool("S3_ENABLED", False)

if S3_ENABLED:
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }

AWS_ACCESS_KEY_ID = env.str("S3_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env.str("S3_SECRET_ACCESS_KEY")

S3_USE_SIGV4 = env.bool("S3_USE_SIGV4")
AWS_S3_REGION_NAME = env.str("S3_REGION_NAME", "")
AWS_S3_ENDPOINT_URL = env.str("S3_ENDPOINT_URL")
AWS_DEFAULT_ACL = "public-read"
AWS_STORAGE_BUCKET_NAME = env.str("S3_STORAGE_BUCKET_NAME")
AWS_S3_CUSTOM_DOMAIN = env.str("S3_CUSTOM_DOMAIN")
AWS_S3_ADDRESSING_STYLE = env.str("S3_ADDRESSING_STYLE")

# Jazzmin settings
# https://django-jazzmin.readthedocs.io/configuration/

JAZZMIN_SETTINGS = {
    # Title & Branding
    "site_title": "TEMPLATE",
    "site_header": "TEMPLATE",
    "site_brand": "TEMPLATE",
    "site_logo": None,
    "welcome_sign": "Добро пожаловать в TEMPLATE",
    "copyright": "TEMPLATE",
    "search_model": ["auth.User"],
    "user_avatar": None,

    # Top Menu
    "topmenu_links": [
        {"name": "Главная", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Swagger UI", "url": f"/{BASE_URL}{API_PREFIX}docs/swagger/", "new_window": True},
    ],

    # Icons (FontAwesome 5 Free Solid)
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.group": "fas fa-users",
        "constance": "fas fa-sliders-h",
        "constance.config": "fas fa-cogs",
        "django_dramatiq": "fas fa-tasks",
        "django_dramatiq.task": "fas fa-bolt",
    },
    "default_icon_parents": "fas fa-folder",
    "default_icon_children": "fas fa-circle",

    # UI Options
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": ["auth", "constance", "django_dramatiq"],
    "show_ui_builder": False,
    "custom_css": "css/admin_custom.css",
    "custom_js": "js/admin_custom.js",
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": False,
    "accent": "accent-primary",
    "navbar": "navbar-white navbar-light",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": True,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "default_theme_mode": "auto",
    "actions_sticky_top": True,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
}
