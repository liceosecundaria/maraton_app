# maraton_backend/settings.py
from pathlib import Path
import os
from datetime import timedelta
from django.utils.log import DEFAULT_LOGGING
import dj_database_url

# -------------------------
# BASE
# -------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG = False
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "dev-secret-key-ONLY-for-local"
)



ALLOWED_HOSTS = ["maraton-lma-backend.onrender.com", "localhost", "127.0.0.1",
                 "maraton.orgullosamenteliceo.com.mx"]

# Importante para HTTPS detrás del proxy de Render
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# -------------------------
# APPS
# -------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "registro",  # ← tu app
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]
ROOT_URLCONF = "maraton_backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # opcional si usas templates
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "maraton_backend.wsgi.application"

# -------------------------
# BASE DE DATOS
# -------------------------
# En local usa SQLite por defecto; en Render se configura DATABASE_URL
DEFAULT_SQLITE = {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": BASE_DIR / "db.sqlite3",
}

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    DATABASES = {"default": DEFAULT_SQLITE}

# -------------------------
# AUTENTICACIÓN / PASSWORDS
# -------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -------------------------
# i18n / TZ
# -------------------------
LANGUAGE_CODE = "es-mx"
TIME_ZONE = "America/Mexico_City"
USE_I18N = True
USE_TZ = True

# -------------------------
# ESTÁTICOS / MEDIA
# -------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"  # para collectstatic en Render
STATICFILES_DIRS = [
    BASE_DIR / "static",  # si tienes /static local
]

# Whitenoise para servir estáticos en producción
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
os.makedirs(MEDIA_ROOT, exist_ok=True)
# -------------------------
# DRF
# -------------------------
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ],
}

# -------------------------
# CORS / CSRF
# -------------------------
# Dominios frontend permitidos (agrega los que uses)
CORS_ALLOWED_ORIGINS = [
    "https://maraton.orgullosamenteliceo.com.mx",
    "https://maraton-lma-frontend.onrender.com",  # si tienes un front en Render
]
CSRF_TRUSTED_ORIGINS = [
    "https://maraton.orgullosamenteliceo.com.mx",
    "https://maraton-lma-backend.onrender.com",
    "https://*.onrender.com",
]

# Si necesitas leer cookies cross-site desde tu frontend en HTTPS
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# -------------------------
# LOGGING (útil para Render)
# -------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "[%(levelname)s] %(asctime)s %(name)s: %(message)s"}
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO"},
        "registro": {"handlers": ["console"], "level": "INFO"},
    },
}

# -------------------------
# VARIOS
# -------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
