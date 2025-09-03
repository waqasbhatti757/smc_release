"""
ASGI config for smc_tracker project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from .asgi_jwt_middleware import JWTSessionASGIMiddleware
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smc_tracker.settings')

# application = get_asgi_application()
django_asgi_app = get_asgi_application()
application = JWTSessionASGIMiddleware(django_asgi_app)
