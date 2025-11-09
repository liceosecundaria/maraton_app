from pathlib import Path
import os
import dj_database_url

# ---------------------------------------------------------------------
# Rutas base
# ---------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------
# Configuración básica
# ---------------------------------------------------------------------

# En Render pon SECRET_KEY en Environment. Si no, usa esta de desarrollo.
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-muy-insegura")

# En Render: DEBUG=False, en local puedes dejarlo True
DEBUG = os.environ.get("DEBUG", "True") == "True"

# En Render pon:
# ALLOWED_HOSTS = maraton-lma-backend.onrender.com,localhost,127.0.0.1
ALLOWED_HOSTS = os.environ.get(
    "ALLOWED_HOSTS",
    "localhost,127.0.0.1"
).split(",")

# ---------------------------------------------------------------------
# Aplicaciones
# ---------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "corsheaders",
    "rest_framework",

    "registro",
]

# ---------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "maraton_backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "maraton_backend.wsgi.application"

# ---------------------------------------------------------------------
# Base de datos
#   - En local usa SQLite
#   - En Render, si pones DATABASE_URL, dj_database_url la usa
# ---------------------------------------------------------------------
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}

# ---------------------------------------------------------------------
# Password validators
# ---------------------------------------------------------------------
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

# ---------------------------------------------------------------------
# Internacionalización
# ---------------------------------------------------------------------
LANGUAGE_CODE = "es-mx"
TIME_ZONE = "America/Mexico_City"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------
# Static & Media (para Render + local)
# ---------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------
# CORS / CSRF para frontend (local + dominio Hostinger)
# ---------------------------------------------------------------------
# Para simplificar ahora:
CORS_ALLOW_ALL_ORIGINS = False

# Si quieres dejarlo más restringido, comenta la línea de arriba
# y usa sólo CORS_ALLOWED_ORIGINS:
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",                         # desarrollo Vite
    "https://maraton.orgullosamenteliceo.com.mx",    # tu dominio en Hostinger
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    # muy importante: URL de Render SIEMPRE con https:
    #"https://maraton-lma-backend.onrender.com",
    # y tu dominio público si lo llegas a usar directo contra el backend:
    "https://maraton.orgullosamenteliceo.com.mx",
]

# ---------------------------------------------------------------------
# Token admin (para tu panel)
# ---------------------------------------------------------------------
ADMIN_TOKEN = "super-secreto-2025"
