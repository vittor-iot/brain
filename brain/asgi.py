import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from app01 import urls

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'brain.settings')
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'brain.test_settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(urls.websocket_urlpatterns)
    ),
})
