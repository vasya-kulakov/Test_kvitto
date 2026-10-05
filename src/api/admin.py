from fastapi import APIRouter

router = APIRouter()

@router.get("/admin/reset")
def reset_database():
    """
    Endpoint to reset the database.
    Drops all tables (and sqlite file) and then recreates tables and seeds initial data.
    """
    from ..database import reset_db, create_database
    import asyncio

    # Выполняем сброс и затем создание/инициализацию БД в одном event loop
    async def _reset_and_create():
        await reset_db(drop_sqlite_file=True)
        await create_database()

    asyncio.run(_reset_and_create())

    return {"message": "Database has been reset and initialized."}
