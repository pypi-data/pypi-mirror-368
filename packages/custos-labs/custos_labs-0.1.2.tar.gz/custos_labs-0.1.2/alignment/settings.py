import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url
from corsheaders.defaults import default_headers

# Load environment variables
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY", "fallback-insecure-key")
DEBUG = os.environ.get("DEBUG", "False") == "True"

# Helper to read comma-separated env lists
def get_env_list(key, default=None):
    val = os.environ.get(key)
    if val:
        return [x.strip() for x in val.split(',') if x.strip()]
    return default or []

ALLOWED_HOSTS = get_env_list('ALLOWED_HOSTS', ["custoslabs-backend.onrender.com", "localhost", "127.0.0.1"])
CORS_ALLOWED_ORIGINS = get_env_list('CORS_ALLOWED_ORIGINS', ["https://custoslabs.com", "https://custos-frontend.onrender.com"])
CSRF_TRUSTED_ORIGINS = get_env_list('CSRF_TRUSTED_ORIGINS', ["https://custoslabs.com", "https://custos-frontend.onrender.com"])

CORS_ALLOW_HEADERS = list(default_headers) + [
    'Authorization',
    'Content-Type',
]
CORS_ALLOW_METHODS = [
    "DELETE", "GET", "OPTIONS", "PATCH", "POST", "PUT",
]

INSTALLED_APPS = [
    'jazzmin',               
    'explorer',              
    # 'grappelli',             
    # 'django_admin_charts',   
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # My apps
    'api',
    'custos',
    'chatbot_ai',
    'simulator',

    # Third-party APIs and auth
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'dj_rest_auth',
    'dj_rest_auth.registration',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.github',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'alignment.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'alignment.wsgi.application'

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///db.sqlite3")
DATABASES = {
    'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}


# CELERY & REDIS
CELERY_BROKER_URL = os.environ.get("REDIS_URL")
CELERY_RESULT_BACKEND = f"{CELERY_BROKER_URL}?ssl_cert_reqs=CERT_NONE"
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": CELERY_BROKER_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "ssl_cert_reqs": None,
            },
        }
    }
}
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

CSRF_COOKIE_HTTPONLY = False
CSRF_USE_SESSIONS = False

SOCIALACCOUNT_PROVIDERS = {
    'github': {
        'APP': {
            'client_id': os.environ.get("GITHUB_CLIENT_ID"),
            'secret': os.environ.get("GITHUB_SECRET"),
            'key': ''
        }
    }
}

EMAIL_BACKEND = os.getenv('EMAIL_BACKEND')
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS') == 'True'
EMAIL_USE_HTML = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')

ADMINS = [('CustosLabs Dev Team', 'dev@custoslabs.com')]
MANAGERS = [('CustosLabs Support', 'support@custoslabs.com')]
SERVER_EMAIL = 'dev@custoslabs.com'

LOGIN_REDIRECT_URL = '/api/auth/success/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'usage_format': {
            'format': '[{asctime}] {levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'usage_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'usage.log'),
            'formatter': 'usage_format',
        },
    },
    'loggers': {
        'usage_logger': {
            'handlers': ['usage_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

DEBUG = False


# Email/Allauth registration settings
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_CONFIRM_EMAIL_ON_GET = True  
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = False 
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 2

# DJ-REST-AUTH
REST_USE_EMAIL = True

ACCOUNT_DEFAULT_HTTP_PROTOCOL = os.environ.get('ACCOUNT_DEFAULT_HTTP_PROTOCOL', 'https')
SITE_ID = 1  

# Redirect anonymous users to the login page after email confirmation
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = "https://custoslabs.com/login"
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = "https://custoslabs.com/login"

CORS_ALLOW_CREDENTIALS = True



X_FRAME_OPTIONS = "SAMEORIGIN" 
JAZZMIN_SETTINGS = {
    "site_title": "Custos Labs Admin Panel",
    "site_header": "Custos Labs Admin Dashboard",
    "site_brand": "Custos Labs",
    "welcome_sign": "Welcome to the Custos Labs Admin Dashboard",
    "search_model": ["auth.User", "api.APIKey"],
    "show_sidebar": True,
    "navigation_expanded": True,
}

ADMIN_TOOLS_INDEX_DASHBOARD = 'api.dashboard.CustomIndexDashboard'
