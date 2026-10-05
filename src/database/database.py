import os
from typing import AsyncGenerator, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")

Base = declarative_base()


class AsyncClient:
    """Клиент для асинхронной работы с базой данных через SQLAlchemy.

    Пример использования:
        async_client = AsyncClient(DATABASE_URL)
        await async_client.init()
        async with async_client.get_session() as session:
            ...
    """

    def __init__(self, url: str = DATABASE_URL, echo: bool = False):
        self.url = url
        self.echo = echo
        self.engine: Optional[AsyncEngine] = None
        self.async_session: Optional[async_sessionmaker] = None

    def _create(self) -> None:
        if self.engine is None:
            self.engine = create_async_engine(self.url, echo=self.echo, future=True)
            self.async_session = async_sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)

    async def init(self) -> None:
        """Инициализация движка и создание таблиц, если их нет."""
        self._create()
        assert self.engine is not None
        async with self.engine.begin() as conn:
            # Создание таблиц синхронно внутри асинхронного соединения
            await conn.run_sync(Base.metadata.create_all)

        # После создания таблиц — проверим и при необходимости заполним таблицу тарифов
        # Импорт модели внутри функции, чтобы избежать проблем с цикличными импортами
        from .models import Tariff  # local import

        if self.async_session is None:
            self._create()

        assert self.async_session is not None
        async with self.async_session() as session:
            q = select(Tariff).limit(1)
            result = await session.execute(q)
            exists = result.scalars().first()
            if not exists:
                tariffs = [
                    Tariff(name="basic", price=990000),
                    Tariff(name="standard", price=1990000),
                    Tariff(name="premium", price=2990000),
                ]
                session.add_all(tariffs)
                await session.commit()

    async def close(self) -> None:
        """Закрыть движок и соединения."""
        if self.engine is not None:
            await self.engine.dispose()
            self.engine = None
            self.async_session = None

    def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Вернуть контекстный менеджер для сессии.

        Используется как: async with async_client.get_session() as session:
        """

        if self.async_session is None:
            self._create()

        assert self.async_session is not None

        async def _session_generator() -> AsyncGenerator[AsyncSession, None]:
            async with self.async_session() as session:
                yield session

        return _session_generator()


# Глобальный клиент по умолчанию, его можно переопределить в приложении
async_client = AsyncClient()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Утилита-генератор для внедрения сессии (например, в FastAPI).

    Пример (FastAPI):
        @app.on_event("startup")
        async def startup():
            await async_client.init()

        async def get_db():
            async with async_client.get_session() as session:
                yield session
    """
    async with async_client.get_session() as session:
        yield session
