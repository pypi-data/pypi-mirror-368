"""
Views for django_coolify app
"""
import json
import sys
import django
from django.http import JsonResponse
from django.db import connection
from django.conf import settings


def health_check(request):
    """
    Health check endpoint that returns application status.
    
    This endpoint performs basic health checks and returns:
    - Application status
    - Database connectivity
    - Django version
    - Python version
    - Debug mode status
    
    Returns HTTP 200 with JSON response if healthy,
    HTTP 503 with error details if unhealthy.
    """
    health_data = {
        "status": "healthy",
        "timestamp": None,
        "checks": {
            "database": "unknown",
            "django": "unknown",
            "python": "unknown"
        },
        "application": {
            "name": getattr(settings, 'APP_NAME', 'django-app'),
            "debug": settings.DEBUG,
            "django_version": django.get_version(),
            "python_version": sys.version.split()[0]
        }
    }
    
    # Import datetime here to avoid issues if not available
    try:
        from datetime import datetime
        health_data["timestamp"] = datetime.utcnow().isoformat() + "Z"
    except ImportError:
        health_data["timestamp"] = "unknown"
    
    # Check database connectivity
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            health_data["checks"]["database"] = "connected"
    except Exception as e:
        health_data["checks"]["database"] = f"error: {str(e)}"
        health_data["status"] = "unhealthy"
    
    # Basic Django check
    try:
        health_data["checks"]["django"] = f"ok (v{django.get_version()})"
    except Exception as e:
        health_data["checks"]["django"] = f"error: {str(e)}"
        health_data["status"] = "unhealthy"
    
    # Basic Python check  
    try:
        health_data["checks"]["python"] = f"ok (v{sys.version.split()[0]})"
    except Exception as e:
        health_data["checks"]["python"] = f"error: {str(e)}"
        health_data["status"] = "unhealthy"
    
    # Return appropriate HTTP status code
    status_code = 200 if health_data["status"] == "healthy" else 503
    
    return JsonResponse(health_data, status=status_code, json_dumps_params={'indent': 2})
