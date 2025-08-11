#===----------------------------------------------------------------------===#
#
#         STAIRLab -- STructural Artificial Intelligence Laboratory
#
#===----------------------------------------------------------------------===#
import os, environ
import dj_database_url

env = environ.Env(DEBUG=(bool, False))

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CORE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY", default="S#perS3crEt_007")

# SECURITY WARNING: don't run with debug turned on in production.
DEBUG = env("DEBUG")

ASSETS_ROOT = os.getenv("ASSETS_ROOT", "/static/assets")

# load production server from .env file
ALLOWED_HOSTS = [
    "brace2.herokuapp.com",
    "structures.live",
    "ca.structures.live"
] + ([
    "localhost",
    "localhost:85",
    "127.0.0.1",
] if DEBUG else [])

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:85",
    "http://127.0.0.1",
    "https://127.0.0.1",
#   "https://" + env("SERVER", default="127.0.0.1"),
] + [
    "https://" + host for host in [
        "brace2.herokuapp.com",
        "structures.live",
        "ca.structures.live"
    ]
]

# Application definition

INSTALLED_APPS = [
#   "irie.apps.admin_dash", # TODO
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    # IRiE
    "irie.init",
    "irie.apps.site",
    "irie.apps.events",
    "irie.apps.inventory",
    "irie.apps.prediction",
    "irie.apps.evaluation",
#   "irie.apps.networks",
    "irie.apps.documents", # TODO
    "crispy_forms",
    "crispy_bootstrap5",
    "formtools"

#   "django_extensions", # For generating graphs, remove for deployment
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "irie.core.urls"
LOGIN_REDIRECT_URL = "home"  # Route defined in site/urls.py
LOGOUT_REDIRECT_URL = "home"  # Route defined in site/urls.py
TEMPLATE_DIR = os.path.join(CORE_DIR, "apps/templates")  # ROOT dir for templates

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [TEMPLATE_DIR],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.context_processors.cfg_assets_root",
                "irie.apps.context_processors.irie_apps",
            ],
        },
    },
]

WSGI_APPLICATION = "irie.core.wsgi.application"

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
DATABASES = {}
if "DATABASE_URL" in os.environ:
    DATABASES["default"] = dj_database_url.config(
        #                             TODO:
        conn_max_age=600,
        ssl_require=False,
    )
elif os.environ.get("DB_ENGINE") and os.environ.get("DB_ENGINE") == "mysql":
    DATABASES = {
        "default": {
            "ENGINE":   "django.db.backends.mysql",
            "NAME":     os.getenv("DB_NAME",     "brace_db"),
            "USER":     os.getenv("DB_USERNAME", "brace_db_usr"),
            "PASSWORD": os.getenv("DB_PASS",     "pass"),
            "HOST":     os.getenv("DB_HOST",     "localhost"),
            "PORT":     os.getenv("DB_PORT",     3306),
        },
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": "db.sqlite3",
        }
    }

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated"),
}

#
# EMAIL
#
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
if DEBUG:
    EMAIL_HOST = "localhost"
    EMAIL_PORT = 1052
else:
    EMAIL_HOST = "smtp.gmail.com"
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = os.environ.get("EMAIL_USER", "")
    EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_PASSWORD", "")


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

#------------------------------------------------------------
# SRC: https://devcenter.heroku.com/articles/django-assets

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = os.path.join(CORE_DIR, "staticfiles")
STATIC_URL = "/static/"

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
        os.path.join(CORE_DIR, "apps/static"),
)

# cmp
FILE_UPLOAD_HANDLERS = (
    # "django.core.files.uploadhandler.MemoryFileUploadHandler",
    "django.core.files.uploadhandler.TemporaryFileUploadHandler",
)

#------------------------------------------------------------

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
}

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    # Specific to Heroku:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

