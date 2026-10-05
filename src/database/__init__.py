"""Пакет для работы с базой данных.

Экспортирует точку подключения `db` — глобальный AsyncClient, который можно
использовать для инициализации, закрытия и получения сессий.
Примеры:
    from src.database import db
    await db.init()
    async with db.get_session() as session:
        ...
"""
from .database import AsyncClient, get_session, Base, async_client
from .models import User, Tariff
from .repository import UserRepository

# Точка подключения — удобный алиас на глобальный клиент async_client
db: AsyncClient = async_client

# Удобные алиасы
init_db = async_client.init
close_db = async_client.close

__all__ = [
    "AsyncClient",
    "get_session",
    "Base",
    "async_client",
    "db",
    "init_db",
    "close_db",
    "User",
    "Tariff",
    "UserRepository",
]