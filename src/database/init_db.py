from typing import Optional


async def initialize(async_client) -> None:
    """Создать таблицы и заполнить начальные данные (seed).

    Принимает экземпляр AsyncClient (из database.AsyncClient).
    """
    # Импорт моделей локально, чтобы избежать проблем с циклическими импортами
    from .models import Tariff, Promocode, Payment_method
    from .database import Base

    # Убедимся, что движок существует
    if async_client.engine is None:
        async_client._create()

    assert async_client.engine is not None

    # Создаём таблицы
    async with async_client.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Заполняем начальными данными, если таблицы пусты
    if async_client.async_session is None:
        async_client._create()

    assert async_client.async_session is not None
    async with async_client.async_session() as session:
        # Tariffs
        q = session.execute(Tariff.__table__.select().limit(1))
        result = await q
        exists = result.scalars().first()
        if not exists:
            tariffs = [
                Tariff(name="basic", price=990000),
                Tariff(name="standard", price=1990000),
                Tariff(name="premium", price=2990000),
            ]
            session.add_all(tariffs)
            await session.commit()

        # Promocodes
        q2 = session.execute(Promocode.__table__.select().limit(1))
        result2 = await q2
        exists2 = result2.scalars().first()
        if not exists2:
            promocodes = [
                Promocode(code="KVITTO10", discount_percentage=10),
            ]
            session.add_all(promocodes)
            await session.commit()

        # Payment methods
        q3 = session.execute(Payment_method.__table__.select().limit(1))
        result3 = await q3
        exists3 = result3.scalars().first()
        if not exists3:
            payment_methods = [
                Payment_method(name="card", installment_months=None),
                Payment_method(name="sbp", installment_months=None),
                Payment_method(name='installment_3', installment_months=3),
                Payment_method(name='installment_6', installment_months=6),
                Payment_method(name='installment_12', installment_months=12),
            ]
            session.add_all(payment_methods)
            await session.commit()
