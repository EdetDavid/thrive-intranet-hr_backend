import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(os.path.join(BASE_DIR, ".env"))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# Read SECRET_KEY from environment; fall back to the hard-coded key only for local development.
SECRET_KEY = os.environ.get(
    "SECRET_KEY", "django-insecure-4iei53l-39e-r-puj3k85m)^u6r##q*phs-x*w=auue01($=!l")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG", "True") == "True"

# Allow hosts: read from environment variable HOSTS (comma-separated) or use sensible defaults.
# Example: HOSTS=dvooskid.pythonanywhere.com,thrive-intranet-ten.vercel.app
env_hosts = os.environ.get("HOSTS", "").strip()
if env_hosts:
    ALLOWED_HOSTS = [h.strip() for h in env_hosts.split(",") if h.strip()]
else:
    ALLOWED_HOSTS = [
        'dvooskid.pythonanywhere.com',
        'localhost',
        '127.0.0.1',
    ]

# LOCALHOST override: if the environment variable LOCALHOST is set to a truthy value
# (true/1/yes) force local-friendly settings useful for development/testing on
# a developer machine where you want predictable local storage, email backend
# and database regardless of other environment variables.
LOCALHOST = os.environ.get(
    "LOCALHOST", "False").lower() in ("true", "1", "yes")
if LOCALHOST:
    # Always enable debug locally when LOCALHOST is set
    DEBUG = True

    # Allow typical local hostnames
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]

    # Use a local sqlite DB inside the project dir for localhost testing
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }

    # Use local filesystem storage for static/media
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
    STATIC_URL = "/static/"
    MEDIA_URL = "/media/"
    MEDIA_ROOT = os.path.join(BASE_DIR, "media")
    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

    # Use console email backend locally unless explicitly overridden
    if not os.environ.get('EMAIL_BACKEND'):
        EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

    # Point APP_BASE_URL to local frontend by default
    APP_BASE_URL = os.environ.get(
        
        'APP_BASE_URL', 'http://localhost:3000')

# Security settings
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "files",
    "users",
    "leaves",
]


MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# CORS settings: allow all origins only in DEBUG. In production, specify allowed origins via
# env var CORS_ALLOWED_ORIGINS (comma separated) or default to the public frontend URL.
CORS_ALLOW_CREDENTIALS = True
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOWED_ORIGINS = ["http://localhost:3000", ]
else:
    CORS_ALLOW_ALL_ORIGINS = False
    raw = os.environ.get("CORS_ALLOWED_ORIGINS", "")
    if raw:
        CORS_ALLOWED_ORIGINS = [o.strip() for o in raw.split(",") if o.strip()]
    else:
        # Default to the known frontend URL in production
        CORS_ALLOWED_ORIGINS = [os.environ.get(
            "APP_BASE_URL", "https://thrive-intranet-ten.vercel.app")]

    # Expose Content-Disposition header so frontend JS can read filenames from responses
    # (useful for downloads). We expose it in all environments; it's safe for local dev.
    CORS_EXPOSE_HEADERS = ["Content-Disposition"]
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.MultiPartParser",  # Required for file uploads
        "rest_framework.parsers.FormParser",
    ],
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}


APPEND_SLASH = False


AUTH_USER_MODEL = "users.User"
ROOT_URLCONF = "hr_intranet.urls"

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
    },
]

WSGI_APPLICATION = "hr_intranet.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",  # Use SQLite for development
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

# Add storages and extensions to INSTALLED_APPS
INSTALLED_APPS += ["storages", "django_extensions"]

# Blackblaze B2 Settings
B2_KEY_ID = os.environ.get("B2_KEY_ID")
B2_APPLICATION_KEY = os.environ.get("B2_APPLICATION_KEY")
B2_BUCKET_NAME = os.environ.get("B2_BUCKET_NAME")
B2_ENDPOINT = os.environ.get("B2_ENDPOINT")

# Required S3 compatibility settings for B2
AWS_ACCESS_KEY_ID = B2_KEY_ID
AWS_SECRET_ACCESS_KEY = B2_APPLICATION_KEY
AWS_STORAGE_BUCKET_NAME = B2_BUCKET_NAME
AWS_S3_ENDPOINT_URL = "https://s3.us-east-005.backblazeb2.com"
AWS_S3_REGION_NAME = "us-east-005"

# S3/B2 configuration for public bucket
AWS_S3_VERIFY = True
AWS_QUERYSTRING_AUTH = False  # Don't add authentication parameters to URLs
AWS_DEFAULT_ACL = 'public-read'  # Make uploaded files publicly readable
AWS_S3_FILE_OVERWRITE = False
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",
}
AWS_BUCKET_ACL = 'public-read'
AWS_AUTO_CREATE_BUCKET = False  # Bucket already exists
AWS_S3_SIGNATURE_VERSION = 's3v4'

# B2 URL configuration for public bucket
AWS_S3_CUSTOM_DOMAIN = f"{B2_BUCKET_NAME}.s3.us-east-005.backblazeb2.com"

# Static files configuration
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

# Configure storage to always use B2
if not DEBUG:
    # Production / non-debug: use Backblaze B2 (S3 compatible) storage backends
    STATICFILES_STORAGE = "hr_intranet.storage_backends.StaticStorage"
    DEFAULT_FILE_STORAGE = "hr_intranet.storage_backends.MediaStorage"

    # URLs for B2 storage (using public bucket URLs)
    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"
else:
    # Local development: use local filesystem storage so uploads/serving work without S3
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

    # Local URLs for static/media during development
    STATIC_URL = "/static/"
    MEDIA_URL = "/media/"

# Local directories for legacy support (always defined)
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Basic logging configuration to ensure INFO logs (including our email debug logs) appear in console during development
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO' if DEBUG else 'WARNING',
    },
}

# Email configuration
# Normalize DEFAULT_FROM_EMAIL (strip optional quotes)
raw_default_from = os.environ.get(
    'DEFAULT_FROM_EMAIL', 'thriveholdingswebmail@gmail.com')
DEFAULT_FROM_EMAIL = raw_default_from.strip('"').strip("'")

# Read SMTP details from env
EMAIL_HOST = os.environ.get('EMAIL_HOST', '')
EMAIL_PORT = None
if os.environ.get('EMAIL_PORT'):
    try:
        EMAIL_PORT = int(os.environ.get('EMAIL_PORT'))
    except ValueError:
        EMAIL_PORT = None

EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.environ.get(
    'EMAIL_USE_TLS', 'False').lower() in ('true', '1', 'yes')
EMAIL_USE_SSL = os.environ.get(
    'EMAIL_USE_SSL', 'False').lower() in ('true', '1', 'yes')

# Decide backend: explicit EMAIL_BACKEND env wins, otherwise use SMTP when EMAIL_HOST is provided,
# fall back to console backend for local development.
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND')
if not EMAIL_BACKEND:
    if EMAIL_HOST:
        EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    else:
        EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Public app base URL used in email templates to link back to the frontend
APP_BASE_URL = os.environ.get('APP_BASE_URL', 'http://localhost:3000')

# --- AWS SES configuration (optional) -------------------------------------
# Configure AWS SES as the email backend when USE_AWS_SES is truthy or
# when required AWS credentials are present. This supports both IAM
# credentials and the django-ses backend.
USE_AWS_SES = os.environ.get(
    'USE_AWS_SES', 'False').lower() in ('true', '1', 'yes')
AWS_SES_ACCESS_KEY_ID = os.environ.get(
    'AWS_SES_ACCESS_KEY_ID') or os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SES_SECRET_ACCESS_KEY = os.environ.get(
    'AWS_SES_SECRET_ACCESS_KEY') or os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_SES_REGION_NAME = os.environ.get(
    'AWS_SES_REGION_NAME') or os.environ.get('AWS_DEFAULT_REGION')

if USE_AWS_SES or (AWS_SES_ACCESS_KEY_ID and AWS_SES_SECRET_ACCESS_KEY and AWS_SES_REGION_NAME):
    # Prefer an explicit EMAIL_BACKEND env var if provided
    if not os.environ.get('EMAIL_BACKEND'):
        EMAIL_BACKEND = 'django_ses.SESBackend'

    # django-ses uses AWS credentials from environment or aws config; set safe fallbacks
    if AWS_SES_ACCESS_KEY_ID:
        os.environ.setdefault('AWS_ACCESS_KEY_ID', AWS_SES_ACCESS_KEY_ID)
    if AWS_SES_SECRET_ACCESS_KEY:
        os.environ.setdefault('AWS_SECRET_ACCESS_KEY',
                              AWS_SES_SECRET_ACCESS_KEY)
    if AWS_SES_REGION_NAME:
        os.environ.setdefault('AWS_DEFAULT_REGION', AWS_SES_REGION_NAME)

    # Optional SES settings
    AWS_SES_REGION_NAME = AWS_SES_REGION_NAME
    AWS_SES_REGION_ENDPOINT = os.environ.get('AWS_SES_REGION_ENDPOINT', '')

    # If EMAIL_HOST_USER not set, use the access key id (helps with some setups)
    if not EMAIL_HOST_USER:
        EMAIL_HOST_USER = AWS_SES_ACCESS_KEY_ID or ''

    # If still no DEFAULT_FROM_EMAIL is set, compose one from the AWS account (user can override via env)
    if not DEFAULT_FROM_EMAIL or DEFAULT_FROM_EMAIL == 'thriveholdingswebmail@gmail.com':
        DEFAULT_FROM_EMAIL = os.environ.get(
            'DEFAULT_FROM_EMAIL', f'no-reply@{os.environ.get("AWS_SES_REGION_NAME", "example.com")}')
