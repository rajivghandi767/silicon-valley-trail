from .base import *
import os
from dotenv import load_dotenv

# ============================================================================
# LOAD ENV VARIABLES
# ============================================================================
env_path = BASE_DIR / '.env'
load_dotenv(dotenv_path=env_path, override=True)

# ============================================================================
# PRODUCTION SECURITY & PROXY SETTINGS
# ============================================================================
DEBUG = False
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

ALLOWED_HOSTS = [host.strip() for host in os.getenv(
    'ALLOWED_HOSTS', '').split(',') if host.strip()]

# Trust the upstream proxy's SSL termination
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ============================================================================
# STATIC & MEDIA FILES FOR PRODUCTION
# ============================================================================

STATIC_URL = '/static/'
STATIC_ROOT = '/home/backend/django/staticfiles'

os.makedirs(STATIC_ROOT, exist_ok=True)

# ============================================================================
# DATABASE & CACHE CONFIGURATION
# ============================================================================
DATABASES = {
    'default': {
        'ENGINE': 'django_prometheus.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': os.environ.get('POSTGRES_HOST'),
        'PORT': os.environ.get('POSTGRES_PORT'),
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# ============================================================================
# CSRF AND SESSION SETTINGS FOR PRODUCTION (CROSS-SUBDOMAIN)
# ============================================================================
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in os.getenv(
    'CSRF_TRUSTED_ORIGINS', '').split(',') if origin.strip()]

# Cross-Subdomain Scope dynamically injected via Jenkins
CSRF_COOKIE_DOMAIN = os.getenv('COOKIE_DOMAIN')
SESSION_COOKIE_DOMAIN = os.getenv('COOKIE_DOMAIN')

# CSRF configuration allowing the frontend to read the token
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'None'

# Session configuration (Strictly HttpOnly)
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_HTTPONLY = True

# ============================================================================
# LOGGING FOR PRODUCTION
# ============================================================================
# Updated to use absolute paths so logs are written to the persistent 'svt_logs'
# Docker volume rather than vanishing if the container rebuilds.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/home/backend/django/logs/svt.log',
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/home/backend/django/logs/errors.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file', 'error_file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'game': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# ============================================================================
# PROMETHEUS MONITORING CONFIGURATION
# ============================================================================
PROMETHEUS_EXPORT_MIGRATIONS = False
PROMETHEUS_LATENCY_BUCKETS = (
    0.008, 0.016, 0.032, 0.064, 0.128, 0.256, 0.512, 1.024, 2.048, 4.096, 8.192, 16.384, 32.768, 65.536, 131.072, 262.144,
)
