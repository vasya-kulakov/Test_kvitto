from fastapi import FastAPI

from ..api.__init__ import router
from ..database import create_database, db

app = FastAPI()
app.include_router(router)


@app.on_event("startup")
async def on_startup() -> None:
    # Инициализация базы данных и создание таблиц/начальных данных
    await create_database()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    # Закрываем соединения с БД при завершении приложения
    await db.close()
