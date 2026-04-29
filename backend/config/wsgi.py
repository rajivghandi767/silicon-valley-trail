import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'config.settings.production' if os.getenv(
        'DJANGO_ENV') == 'production' else 'config.settings.local'
)

application = get_wsgi_application()
