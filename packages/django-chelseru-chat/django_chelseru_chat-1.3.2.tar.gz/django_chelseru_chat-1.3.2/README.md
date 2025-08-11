# Django Chelseru Chat

A simple real-time chat package for Django using Django Channels and WebSocket. It enables one-on-one private messaging secured with JWT authentication.

---

## Installation

```bash
pip install django-chelseru-chat
```

---

## Configuration

Ensure your Django project is ASGI-compatible and set up with JWT authentication for WebSocket connections.

### 1. Add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    'channels',
    'chelseru_chat',
]
```

### 2. Set `ASGI_APPLICATION` and `CHANNEL_LAYERS` in `settings.py`:

```python
ASGI_APPLICATION = '<your_project_name>.asgi.application'
```

> Replace `<your_project_name>` with the actual name of your Django project folder (e.g., `myproject`).

```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
```


### 3. Use your custom `asgi.py` with `JWTAuthMiddleware`:

```python
# <your_project_name>/asgi.py

import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

# Set environment and initialize Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '<your_project_name>.settings')
django.setup()

# Import routing and middleware AFTER setup
import chelseru_chat.routing
from chelseru_chat.middleware import JWTAuthMiddleware

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddleware(
        URLRouter(
            chelseru_chat.routing.websocket_urlpatterns
        )
    ),
})
```
> Again, replace `<your_project_name>` with your Django project's name.

---

## Models

### `ChatRoom`

```python
class ChatRoom(models.Model):
    user_1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user1_chats')
    user_2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user2_chats')
    created_at = models.DateTimeField(auto_now_add=True)
```

### `Message`

```python
class Message(models.Model):
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
```

---

## WebSocket Connection

To send and receive messages, connect via WebSocket to:

```
ws://<your-domain>/ws/chat/<chat_room_id>/?token=<your_jwt_access_token>
```

**Example:**

```
ws://qesa.chelseru.com/ws/chat/3/?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### To send a message:

```json
> {"message": "Sar barzi, Luria"}
```

### You will receive a response like:

```json
< {"message": "Sar barzi, Luria", "sender": "user"}
```

---

## Create ChatRoom Programmatically

```python
from chelseru_chat.models import ChatRoom
chat = ChatRoom.objects.create(user_1=user1, user_2=user2)
```

---

## JWT WebSocket Authentication

This package uses a custom `JWTAuthMiddleware` for authenticating users via JWT tokens.  
Token must be provided as a query parameter: `?token=...`

You can use [`djangorestframework-simplejwt`](https://django-rest-framework-simplejwt.readthedocs.io/) to issue tokens.

---

## Features

- Private 1-on-1 chat
- Real-time messaging via WebSocket
- JWT-authenticated WebSocket
- Message history per room
- Simple model structure

---

## TODO

- Group chat support
- Message read status
- Typing indicators

---

## License

MIT License

Sobhan Bahman | Rashnu

