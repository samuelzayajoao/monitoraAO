# chat/routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    # O [-\w.]+ permite hífens, letras, números, underscores e pontos
    re_path(r"^ws/chat/(?P<room_name>[-\w.]+)/$", consumers.ChatConsumer.as_asgi()),
]
