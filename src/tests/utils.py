import asyncio
from typing import Callable, Awaitable

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.database.database import Base


def run_with_db(fn: Callable[[AsyncSession], Awaitable[None]]) -> None:
    """Run an async function with a fresh in-memory DB and AsyncSession.

    The provided fn should be an async function accepting one parameter: session.
    This helper creates the engine, initializes tables, provides a session and
    disposes the engine afterwards.
    """

    async def _runner():
        engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        async with AsyncSessionLocal() as session:
            await fn(session)

        await engine.dispose()

    asyncio.run(_runner())
