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
#DEBUG = True

DEBUG = False

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

    'rest_framework',
    'rest_framework.authtoken',  
    'corsheaders',   
    'crispy_forms',
    'crispy_bootstrap4',
    'channels',
    'oauth2_provider',
    'axes', # For brute-force protection
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
    'REFRESH_TOKEN_TOKEN': timedelta(days=14),
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
try:
    import django_redis
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": os.environ.get("REDIS_URL"),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
        }
    }
except ModuleNotFoundError:
    # Fallback for development when django-redis isn't installed
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "dev-local-cache",
        }
    }

REDIS_URL = os.environ.get("REDIS_URL")


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
DB_LIVE = os.environ.get("DB_LIVE", "").lower() in ("1", "true", "yes")
if DB_LIVE:
    # Support Railway/MySQL environment variables as fallbacks
    db_name = os.environ.get('DB_NAME') or os.environ.get('MYSQLDATABASE') or os.environ.get('MYSQL_DATABASE')
    db_user = os.environ.get('DB_USER') or os.environ.get('MYSQLUSER') or os.environ.get('MYSQL_USER')
    db_password = os.environ.get('DB_PASSWORD') or os.environ.get('MYSQLPASSWORD') or os.environ.get('MYSQL_PASSWORD')
    db_host = os.environ.get('DB_HOST') or os.environ.get('MYSQLHOST') or os.environ.get('MYSQL_HOST') or 'localhost'
    db_port = int(os.environ.get('DB_PORT') or os.environ.get('MYSQLPORT') or os.environ.get('MYSQL_PORT') or 3306)

    db_options = {}
    # Optional SSL configuration for hosted MySQL providers
    mysql_ssl = os.environ.get('MYSQL_SSL') or os.environ.get('DB_SSL')
    if mysql_ssl and mysql_ssl.lower() in ('1', 'true', 'yes', 'required'):
        db_options['ssl'] = {}
        if os.environ.get('MYSQL_SSL_CA'):
            db_options['ssl']['ca'] = os.environ.get('MYSQL_SSL_CA')

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': db_name,
            'USER': db_user,
            'PASSWORD': db_password,
            'HOST': db_host,
            'PORT': db_port,
            'OPTIONS': db_options,
        }
    }
else:

"""

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get("DB_NAME"),
        'USER': os.environ.get("DB_USER"),
        'PASSWORD': os.environ.get("DB_PASSWORD"),
        'HOST': os.environ.get("DB_HOST"),
        'PORT': os.environ.get("DB_PORT"),
    }
}


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
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

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/


BASE_DIR = Path(__file__).resolve().parent.parent


STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'
STATIC_DIR = BASE_DIR / 'static'
STATICFILES_DIRS = [STATIC_DIR] if STATIC_DIR.exists() else []

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"



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

"""
#smtp settings(email)
# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#EMAIL_HOST = config("EMAIL_HOST", default="localhost")
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", cast=int, default=587)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool, default=True)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="noreply@volthub.com")
"""



# Allauth
SITE_ID = 1

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



AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None

DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'



# Open Charge Map API Key
OPEN_CHARGE_API_KEY = os.environ.get("OPEN_CHARGE_API_KEY")