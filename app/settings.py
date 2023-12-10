import os
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent

MISSING = object()


def get_env(name: str, default: Any = MISSING) -> Any:
    """Get an env var and raise the appropriate message if not set."""
    try:
        return os.environ[name]
    except KeyError:
        if default is not MISSING:
            return default

        print(f"settings.py: error: required environment variable {name!r} is not set.")
        exit(1)


# Debug
DEBUG = get_env("DEBUG", None) is not None

# Logging
loglevel = get_env("LOG_LEVEL", "DEBUG" if DEBUG else "INFO").upper()
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "colored_verbose": {
            "()": "coloredlogs.ColoredFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s: %(message)s",
        },
    },
    "handlers": {
        "colored_console": {
            "level": loglevel,
            "class": "logging.StreamHandler",
            "formatter": "colored_verbose",
        }
    },
    "loggers": {
        "django": {
            "handlers": ["colored_console"],
        },
        "gunicorn.access": {"handlers": ["colored_console"]},
        "gunicorn.error": {"handlers": ["colored_console"]},
    },
}

# Secret key
SECRET_KEY = get_env("SECRET_KEY", None)
if SECRET_KEY is None:
    if not DEBUG:
        print("settings.py: error: SECRET_KEY is not set and debug mode is disabled.")
        exit(1)
    SECRET_KEY = "IfIUseThisInProductionIWillBeFired"  # noqa: S105

# Allowed hosts
if DEBUG:
    ALLOWED_HOSTS = ["*"]
else:
    ALLOWED_HOSTS = get_env("ALLOWED_HOSTS").split(";")

# Apps
INSTALLED_APPS = [
    "rest_framework",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "django.contrib.messages",
]
if DEBUG:
    INSTALLED_APPS.append("django.contrib.admin")

# Database
if get_env("DATABASE_HOST", None) is not None:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": get_env("DATABASE_NAME"),
            "USER": get_env("DATABASE_USER"),
            "PASSWORD": get_env("DATABASE_PASSWORD"),
            "HOST": get_env("DATABASE_HOST"),
            "PORT": get_env("DATABASE_PORT"),
        }
    }
else:
    if DEBUG is False:
        print(
            "settings.py: warning: DATABASE_HOST is not set "
            "and debug mode is disabled. Using SQLite."
        )

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# Static files
STATIC_URL = "/static/"
STATIC_ROOT = "/tmp/www"  # noqa: S108 Why?
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]


# Templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

# Middlewares
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

### Default Settings
# Application definition

ROOT_URLCONF = "app.urls"

WSGI_APPLICATION = "app.wsgi.application"

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
