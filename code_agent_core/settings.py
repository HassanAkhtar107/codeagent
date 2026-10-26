"""
Django settings for code_agent_core project (Code Agent Platform).
"""

import os
import environ

try:
    env = environ.Env()
    HAS_ENVIRON = True
except ImportError:
    class DummyEnv:
        def str(self, key, default=""): return os.environ.get(key, default)
        def bool(self, key, default=False): return os.environ.get(key, str(default)).lower() in ("true", "1")
        def list(self, key, default=None): return os.environ.get(key, "").split(",") if os.environ.get(key) else (default or [])
    env = DummyEnv()
    HAS_ENVIRON = False

DEBUG = True

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if HAS_ENVIRON:
    environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env.str("SECRET_KEY", "DEFAULT_KEY")

ALLOWED_HOSTS = env.list("HOST", default=["*"])
SITE_ID = 1

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env.bool("SECURE_REDIRECT", default=False)

BASE_INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
]

LOCAL_APPS = [
    "users.apps.UsersConfig",
    "agents.apps.AgentsConfig",
    "conversations.apps.ConversationsConfig",
    "executor.apps.ExecutorConfig",
    "projects.apps.ProjectsConfig",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework.authtoken",
    "dj_rest_auth",
    "dj_rest_auth.registration",
    "bootstrap4",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "django_extensions",
    "drf_yasg",
    "storages",
    "django_filters",
    "corsheaders",
    "django_crontab",
    "django_celery_beat",
    "django_celery_results",
    "dbbackup",
]

import importlib
INSTALLED_APPS = []
for app in BASE_INSTALLED_APPS + THIRD_PARTY_APPS:
    mod_name = app.split(".")[0]
    try:
        importlib.import_module(mod_name)
        INSTALLED_APPS.append(app)
    except ImportError:
        pass

INSTALLED_APPS += LOCAL_APPS

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

ROOT_URLCONF = "code_agent_core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "templates"),
        ],
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

WSGI_APPLICATION = "code_agent_core.wsgi.application"

POSTGRES_ENGINE = env.str("POSTGRES_ENGINE", default="django.db.backends.postgresql")
POSTGRES_DB = env.str("POSTGRES_DB", default="")
POSTGRES_USER = env.str("POSTGRES_USER", default="")
POSTGRES_PASSWORD = env.str("POSTGRES_PASSWORD", default="")
POSTGRES_HOST = env.str("POSTGRES_HOST", default="")
POSTGRES_PORT = env.str("POSTGRES_PORT", default="5432")

if POSTGRES_DB and POSTGRES_HOST:
    DATABASES = {
        "default": {
            "ENGINE": POSTGRES_ENGINE,
            "NAME": POSTGRES_DB,
            "USER": POSTGRES_USER,
            "PASSWORD": POSTGRES_PASSWORD,
            "HOST": POSTGRES_HOST,
            "PORT": POSTGRES_PORT,
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }


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

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
] if os.path.exists(os.path.join(BASE_DIR, "static")) else []
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = "optional"
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_UNIQUE_EMAIL = True

REST_AUTH = {
    "PASSWORD_RESET_SERIALIZER": "users.api.serializers.PasswordSerializer",
    "REGISTER_SERIALIZER": "users.api.serializers.SignupSerializer",
}

AUTH_USER_MODEL = "users.User"

# ── AI Provider Keys ──────────────────────────────────────────────────────────
OPENAI_API_KEY = env.str("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = env.str("ANTHROPIC_API_KEY", "")
GEMINI_API_KEY = env.str("GEMINI_API_KEY", "")

# ── Code Execution Sandbox ────────────────────────────────────────────────────
EXECUTOR_TIMEOUT_SECONDS = env.str("EXECUTOR_TIMEOUT_SECONDS", "30")
EXECUTOR_MAX_OUTPUT_BYTES = env.str("EXECUTOR_MAX_OUTPUT_BYTES", "65536")

SWAGGER_SETTINGS = {
    "DEFAULT_INFO": f"{ROOT_URLCONF}.api_info",
}

REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "DATETIME_FORMAT": "%Y-%m-%d %H:%M:%S",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 20,
}

from corsheaders.defaults import default_headers

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_HEADERS = list(default_headers) + [
    "x-session-id",
    "x-agent-id",
]

CELERY_BROKER_URL = env.str("REDIS_URL", default="redis://redis:6379")
CELERY_RESULT_BACKEND = env.str("REDIS_URL", default="redis://redis:6379")

# ── Jazzmin Admin Theme ───────────────────────────────────────────────────────
JAZZMIN_SETTINGS = {
    "site_title": "Code Agent Admin",
    "site_header": "Code Agent",
    "site_brand": "Code Agent",
    "welcome_sign": "Welcome to Code Agent Admin Panel",
    "copyright": "Code Agent",
}
