"""
URL configuration for django_coolify app
"""
from django.urls import path
from . import views

app_name = 'django_coolify'

urlpatterns = [
    path('health/', views.health_check, name='health_check'),
]
