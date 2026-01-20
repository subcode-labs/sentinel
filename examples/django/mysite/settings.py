import os
from pathlib import Path
from sentinel_sdk import SentinelClient

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- SENTINEL INTEGRATION START ---
# Initialize Sentinel Client
# This expects SENTINEL_API_KEY (and optionally SENTINEL_ENDPOINT) in environment
# or via specific arguments.
try:
    print("🔐 Initializing Sentinel Client...")
    client = SentinelClient()

    # Example: Fetching Django's SECRET_KEY
    # We use a default/fallback here for the example if the key doesn't exist in Sentinel
    # In production, you might want to raise an error if critical secrets are missing.
    try:
        django_secret = client.get_secret("django_secret_key")
        if django_secret:
            SECRET_KEY = django_secret.value
            print(
                f"✅ SECRET_KEY loaded from Sentinel (version {django_secret.version})"
            )
        else:
            print(
                "⚠️ 'django_secret_key' not found in Sentinel. Falling back to insecure default."
            )
            SECRET_KEY = "django-insecure-fallback-key-for-demo-only"
    except Exception as e:
        print(f"⚠️ Error fetching 'django_secret_key': {e}")
        SECRET_KEY = "django-insecure-fallback-key-for-demo-only"

    # Example: Fetching DEBUG setting
    # Sentinel secrets are strings, so we need to parse boolean
    try:
        debug_secret = client.get_secret("django_debug")
        if debug_secret:
            DEBUG = debug_secret.value.lower() == "true"
            print(f"✅ DEBUG mode configured from Sentinel: {DEBUG}")
        else:
            DEBUG = True
            print("⚠️ 'django_debug' not found in Sentinel. Defaulting to True.")
    except Exception as e:
        print(f"⚠️ Error fetching 'django_debug': {e}")
        DEBUG = True

except Exception as e:
    print(f"❌ Failed to connect to Sentinel: {e}")
    print("⚠️ Falling back to local settings")
    SECRET_KEY = "django-insecure-fallback-key-for-demo-only"
    DEBUG = True
# --- SENTINEL INTEGRATION END ---

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "demo",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "mysite.urls"

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

WSGI_APPLICATION = "mysite.wsgi.application"

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Password validation
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
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
