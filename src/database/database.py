from contextlib import asynccontextmanager
import os
from typing import AsyncGenerator, Optional

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

        # Убедимся, что движок и сессии созданы
        self._create()

        # Импортируем модуль init_db через importlib, чтобы гарантированно
        # получить модуль, а не одноимённый атрибут из пакета.
        import importlib

        init_db_mod = importlib.import_module(f"{__package__}.init_db")
        await init_db_mod.initialize(self)  # Теперь всё сработает


    async def close(self) -> None:
        """Закрыть движок и соединения."""
        if self.engine is not None:
            await self.engine.dispose()
            self.engine = None
            self.async_session = None

    async def reset(self, drop_sqlite_file: bool = False) -> None:
        """Удалить все таблицы из базы данных.

        Если используется sqlite и drop_sqlite_file=True, удалит файл базы данных.
        """
        # Убедимся, что движок создан
        self._create()

        if self.engine is None:
            return

        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

        # Опционально удалить файл sqlite
        if drop_sqlite_file and self.url.startswith("sqlite"):
            # ожидаем формат sqlite+aiosqlite:///./test.db или sqlite:///./test.db
            import re
            import os

            m = re.search(r"/{2,3}(.+)$", self.url)
            if m:
                path = m.group(1)
                # относительный путь
                if not os.path.isabs(path):
                    path = os.path.join(os.getcwd(), path)
                try:
                    if os.path.exists(path):
                        os.remove(path)
                except Exception:
                    # не фейлим при ошибке удаления
                    pass

    def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Вернуть контекстный менеджер для сессии.

        Используется как: async with async_client.get_session() as session:
        """

        if self.async_session is None:
            self._create()

        assert self.async_session is not None

        @asynccontextmanager
        async def _session_generator() -> AsyncGenerator[AsyncSession, None]:
            async with self.async_session() as session:
                yield session

        return _session_generator()


# Глобальный клиент по умолчанию, его можно переопределить в приложении
async_client = AsyncClient()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_client.get_session() as session:
        yield session
