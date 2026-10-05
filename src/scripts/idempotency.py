from typing import Optional
from fastapi import Header
import uuid


def generate_key() -> str:
    """Сгенерировать уникальный idempotency key."""
    return uuid.uuid4().hex


class IdempotentRequest:
    """Dependency для получения заголовка Idempotency-Key.

    Возвращает переданный ключ или None.
    """

    def __init__(self):
        pass

    async def __call__(self, idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key")):
        return idempotency_key
