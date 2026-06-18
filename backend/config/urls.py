from django.urls import path, include

from health_check.views import health_detailed, health_simple

urlpatterns = [
    path('api/', include('game.urls')),
    # Health Check Endpoints
    path('health/', health_simple, name='health_simple'),
    path('health/detailed/', health_detailed, name='health_detailed'),
    path('', include('django_prometheus.urls')),
]
