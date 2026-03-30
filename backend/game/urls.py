from django.urls import path
from . import views

urlpatterns = [
    path('state/', views.get_state, name='get_state'),
    path('action/', views.take_action, name='take_action'),
]
