import asyncio
import os

import pytest

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.database.database import Base


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the session.

    Required for pytest-asyncio when using async fixtures with session scope.
    """
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def db_engine(tmp_path_factory):
    """Create a temporary sqlite database for tests (file-based).

    We create the file under the temporary directory so multiple connections
    see the same database. The tables are created once per test session.
    """
    data_dir = tmp_path_factory.mktemp("data")
    db_file = data_dir / "test_db.sqlite"
    db_url = f"sqlite+aiosqlite:///{db_file}"

    engine = create_async_engine(db_url, future=True)

    # create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()
    try:
        os.remove(str(db_file))
    except Exception:
        pass


@pytest.fixture
async def db_session(db_engine):
    """Provide a database session for a test and rollback at the end.

    Each test runs inside a transaction which is rolled back, so tests are isolated.
    """
    # create a connection and a nested transaction so tests can run in isolation
    async with db_engine.connect() as conn:
        trans = await conn.begin()
        AsyncSessionLocal = async_sessionmaker(bind=conn, expire_on_commit=False, class_=AsyncSession)
        async with AsyncSessionLocal() as session:
            yield session
        # rollback any changes done in the test
        await trans.rollback()