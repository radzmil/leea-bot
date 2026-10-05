"""Short-lived, signed WebSocket authorization shared with the Vercel portal."""
from itsdangerous import URLSafeTimedSerializer

SALT = "leea-chat-v1"


def verify(secret, ticket, tenant):
    return URLSafeTimedSerializer(secret, salt=SALT).loads(ticket, max_age=120) == tenant