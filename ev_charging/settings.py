from pathlib import Path
#settings for simpleJWT
from datetime import timedelta
import os
from pathlib import Path
from decouple import config
from dotenv import load_dotenv
import warnings

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-i9r%i5hq%av96r_&&%(qa2fto$bwx-1ka2u__7b8!@z40f#1t!'


# SECURITY WARNING: don't run with debug turned on in production!

#DEBUG = False

DEBUG = True

ALLOWED_HOSTS = ["evcharging-production-c179.up.railway.app", "localhost", "127.0.0.1"]

CSRF_TRUSTED_ORIGINS = [
    "https://evcharging-production-c179.up.railway.app",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# Use secure cookies only in production; disable for local HTTP development so session persists
if DEBUG:
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
else:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# Application definition

INSTALLED_APPS = [
    'django.contrib.sites',  # Required for allauth
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    #apps
    'charging_station',
    'VoltHub',
    'authentication',
    'ecommerce',
    'Cart',
    'Dashboards',

    'rest_framework',
    'rest_framework.authtoken',  
    'corsheaders',   
    'crispy_forms',
    'crispy_bootstrap4',
    'channels',
    'oauth2_provider',
    'axes', # For brute force protection
    'drf_yasg', #swagger
    'anymail', # For email backend

    # Email verification
    'dj_rest_auth',
    'dj_rest_auth.registration',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',


    #aws s3 storage
    'storages',
]


# DRF configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'user': '10/minute',
        'anon': '3/minute',
    },
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 1,
}


REST_AUTH_REGISTER_SERIALIZERS = {
    'REGISTER_SERIALIZER': 'charging_station.serializers.CustomRegisterSerializer',
}

#SimpleJWT setting

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
}



CRISPY_TEMPLATE_PACK = 'bootstrap4'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # External middlewares
    'charging_station.middleware.RequestLoggingMiddleware',
    'charging_station.middleware.PerformanceMonitoringMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'axes.middleware.AxesMiddleware',
    # allauth
    'allauth.account.middleware.AccountMiddleware',
    
]



AXES_FAILURE_LIMIT = 3 # Maximum number of login attempts before lockout
AXES_COOLOFF_TIME = 60  # This is the time (in minutes) that a user will be locked out after exceeding the failure limit


# Celery
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND")
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'



# Redis cache
# Read REDIS_URL early and try a quick reachability test. If Redis is not
# configured or not reachable (e.g., DNS resolution fails when using hosted
# services only available inside their network), fall back to an in-memory
# LocMemCache to avoid 500 errors from things like DRF throttling.
REDIS_URL = os.environ.get("REDIS_URL")
if REDIS_URL:
    try:
        import redis as _redis_client

        # This will raise an exception if Redis is not reachable
        client = _redis_client.from_url(REDIS_URL, socket_connect_timeout=2)
        client.ping()

        try:
            import django_redis

            CACHES = {
                "default": {
                    "BACKEND": "django_redis.cache.RedisCache",
                    "LOCATION": REDIS_URL,
                    "OPTIONS": {
                        "CLIENT_CLASS": "django_redis.client.DefaultClient",
                    },
                }
            }
        except ModuleNotFoundError:
            # If django redis isn't installed, fall back to LocMemCache
            CACHES = {
                "default": {
                    "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                    "LOCATION": "dev-local-cache",
                }
            }
    except Exception as e:
        import warnings
        # This will catch connection errors, timeout errors, etc.
        warnings.warn(f"Redis at {REDIS_URL} not reachable ({e}). Falling back to LocMemCache.")
        CACHES = {
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                "LOCATION": "dev-local-cache",
            }
        }
else:
    # No REDIS_URL configured use local in-memory cache for development
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "dev-local-cache",
        }
    }



CORS_ALLOW_ALL_ORIGINS = True #Adjusting for production

# CORS settings
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
]


ROOT_URLCONF = 'ev_charging.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'Cart.context_processors.cart_contents',  # Make cart available in all templates
            ],
        },
    },
]#'Cart.context_processors.cart',


WSGI_APPLICATION = 'ev_charging.wsgi.application'
ASGI_APPLICATION = 'ev_charging.asgi.application'

# Channels layer configuration
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

# Database
"""
# Database (MySQL on Railway if env present, otherwise local sqlite)
if os.environ.get("DB_NAME") and os.environ.get("DB_USER"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.environ.get("DB_NAME"),
            "USER": os.environ.get("DB_USER"),
            "PASSWORD": os.environ.get("DB_PASSWORD", ""),
            "HOST": os.environ.get("DB_HOST"),
            "PORT": os.environ.get("DB_PORT", "3306"),
            "OPTIONS": {},
        }
    }
else:
"""
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Allauth
SITE_ID = 1


AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]


#This is for social account providers, so it can work with allauth, for example Google
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'], # this will request access to user's profile and email
        'AUTH_PARAMS': {'access_type': 'online'}, # 'online' or 'offline' for refresh token
    }
}


#This will redirect users to home page after login/logout
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'



# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/


BASE_DIR = Path(__file__).resolve().parent.parent
"""
STATIC_ROOT = "staticfiles"
#STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'
STATIC_DIR = BASE_DIR / 'static'
STATICFILES_DIRS = [STATIC_DIR] if STATIC_DIR.exists() else []

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
"""


# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'logs/requests.log',
        },
        'slow_file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': 'logs/slow_requests.log',
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'performance': {
            'handlers': ['slow_file', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


#AUTH_USER_MODEL = 'auth.User' # Using default User model

#AUTH_USER_MODEL = 'charging_station.CustomUser'


ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_USER_MODEL_USERNAME_FIELD = None


REST_USE_JWT = True

# Suppress noisy third-party deprecation warnings in runtime logs
warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    module="dj_rest_auth.registration.serializers",
)

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# Anymail configuration for email backend
EMAIL_BACKEND = "anymail.backends.brevo.EmailBackend"
ANYMAIL = {
    "BREVO_API_KEY": os.environ.get("BREVO_API_KEY"),
}
DEFAULT_FROM_EMAIL = "thatoselepe80@gmail.com"


# Who receives contact messages
CONTACT_RECEIVER_EMAIL = 'thatoselepe80@gmail.com'

# AWS S3 Cloud Storage
AWS_ACCESS_KEY_ID= os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY= os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME= os.environ.get("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = os.environ.get("AWS_S3_REGION_NAME")
AWS_S3_CUSTOM_DOMAIN = os.environ.get("AWS_S3_CUSTOM_DOMAIN")
AWS_DEFAULT_ACL = os.environ.get("AWS_DEFAULT_ACL")


AWS_LOCATION = 'static'

AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",
}


# Static and Media files settings
USE_S3 = (
    AWS_ACCESS_KEY_ID
    and AWS_SECRET_ACCESS_KEY
    and AWS_STORAGE_BUCKET_NAME
)

if USE_S3 and not DEBUG:
    # Static files
    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/"
    STATICFILES_STORAGE = "storages.backends.s3boto3.S3StaticStorage"
    STATIC_ROOT = BASE_DIR / "staticfiles"
    STATICFILES_DIRS = [BASE_DIR / "static"]
    

    # Media files
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

else:
    # This is for local development and when S3 is not configured
    STATIC_URL = "/static/"
    MEDIA_URL = "/media/"
    STATIC_ROOT = "staticfiles"
    MEDIA_ROOT = "media"

    STATIC_ROOT = BASE_DIR / "staticfiles"

    STATICFILES_DIRS = [BASE_DIR / "static"]
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"



AWS_S3_FILE_OVERWRITE = False

AWS_QUERYSTRING_AUTH = False
AWS_DEFAULT_ACL = "public-read" # this will make the files publicly accessible

AWS_S3_OBJECT_PARAMETERS = {
    "ACL": "public-read",
}



# Shopify API Credentials
SHOPIFY_SHOP_NAME = os.getenv("SHOPIFY_SHOP_NAME")
SHOPIFY_API_KEY = os.getenv("SHOPIFY_API_KEY")
SHOPIFY_API_SECRET = os.getenv("SHOPIFY_API_SECRET")
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
SHOPIFY_API_VERSION = "2026-01"

# This is for OAuth integration for Shopify
SHOPIFY_CLIENT_ID = os.getenv("SHOPIFY_CLIENT_ID")
SHOPIFY_CLIENT_SECRET = os.getenv("SHOPIFY_CLIENT_SECRET")
SHOPIFY_REDIRECT_URI = os.getenv("SHOPIFY_REDIRECT_URI")



# Open Charge Map API Key
OPEN_CHARGE_API_KEY = os.environ.get("OPEN_CHARGE_API_KEY")