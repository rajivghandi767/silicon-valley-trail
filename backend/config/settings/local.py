# backend/config/settings/local.py
from .base import *
import os

# ============================================================================
# DEVELOPMENT SETTINGS
# ============================================================================

DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY',
                       'django-insecure-local-dev-key-svt')

ALLOWED_HOSTS = os.getenv(
    'ALLOWED_HOSTS', 'localhost,127.0.0.1,backend').split(',')

# ============================================================================
# DEVELOPMENT-SPECIFIC APPS AND MIDDLEWARE
# ============================================================================
if 'corsheaders' not in INSTALLED_APPS:
    INSTALLED_APPS += ['corsheaders']

if 'corsheaders.middleware.CorsMiddleware' not in MIDDLEWARE:
    MIDDLEWARE.insert(1, 'corsheaders.middleware.CorsMiddleware')

# ============================================================================
# CORS & CSRF SETTINGS
# ============================================================================
CORS_ALLOWED_ORIGINS = os.getenv(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:5173,http://127.0.0.1:5173'
).split(',')

CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = os.getenv(
    'CSRF_TRUSTED_ORIGINS',
    'http://localhost:5173,http://127.0.0.1:5173'
).split(',')

# ============================================================================
# LOCAL COOKIE SECURITY
# ============================================================================
# Disable HTTPS requirement for cookies locally
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

# Allow cookies to be sent across different localhost ports
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'

# Ensure the CSRF cookie is accessible to the frontend JavaScript
CSRF_COOKIE_HTTPONLY = False

# ============================================================================
# DATABASE (Targeting svt-local-db container)
# ============================================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'svt_db'),
        'USER': os.getenv('POSTGRES_USER', 'svt_user'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'svt_password'),
        'HOST': os.getenv('POSTGRES_HOST', 'db'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
    }
}

# ============================================================================
# CACHING (Targeting svt-local-redis container)
# ============================================================================
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://redis:6379/0'),
    }
}

# ============================================================================
# LOGGING FOR DEVELOPMENT
# ============================================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'game': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
