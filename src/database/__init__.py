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
from .models import Tariff
from .repository import TariffRepository

# Точка подключения — удобный алиас на глобальный клиент async_client
db: AsyncClient = async_client

# Удобные алиасы
init_db = async_client.init
close_db = async_client.close


async def create_database() -> None:
    """Удобная функция инициализации БД (создание таблиц и начальные данные).

    Вызывать как: await create_database()
    Она вызывает db.init() и гарантирует, что модели импортированы и таблицы созданы.
    """
    await db.init()

__all__ = [
    "AsyncClient",
    "get_session",
    "Base",
    "async_client",
    "db",
    "init_db",
    "close_db",
    "Tariff",
    "TariffRepository"
]

