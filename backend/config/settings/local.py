from .base import *
import os
import socket
from urllib.parse import urlparse

# ============================================================================
# DEVELOPMENT SETTINGS
# ============================================================================

DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY',
                       'django-insecure-local-testing-key-svt')

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
# DYNAMIC CONNECTION TESTER
# ============================================================================


def is_service_available(host, port, timeout=0.2):
    """Attempts a socket connection to verify if a service is actually running."""
    if not host or not port:
        return False
    try:
        with socket.create_connection((host, int(port)), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, socket.gaierror, OSError):
        return False


# ============================================================================
# DATABASE FALLBACK LOGIC
# ============================================================================
POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_PORT = os.getenv('POSTGRES_PORT')

if is_service_available(POSTGRES_HOST, POSTGRES_PORT):
    print(f"✅ Connected to Postgres at {POSTGRES_HOST}:{POSTGRES_PORT}")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('POSTGRES_DB'),
            'USER': os.getenv('POSTGRES_USER'),
            'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
            'HOST': POSTGRES_HOST,
            'PORT': POSTGRES_PORT,
        }
    }
else:
    print("⚠️ Postgres unreachable. Falling back to SQLite.")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ============================================================================
# CACHING FALLBACK LOGIC
# ============================================================================
REDIS_URL = os.getenv('REDIS_URL')
redis_host, redis_port = None, None

try:
    parsed_url = urlparse(REDIS_URL)
    redis_host = parsed_url.hostname
    redis_port = parsed_url.port or 6379
except ValueError:
    pass

if is_service_available(redis_host, redis_port):
    print(f"✅ Connected to Redis at {redis_host}:{redis_port}")
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL,
        }
    }
else:
    print("⚠️ Redis unreachable. Falling back to LocMemCache.")
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'local-dev-cache',
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
