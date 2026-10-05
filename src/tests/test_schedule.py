import asyncio
from itertools import product

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.database.database import Base
from src.database.repository import PaymentRepository


from src.tests.utils import run_with_db


def run_test_for_months(months):
    async def op(session):
        from src.database.models import Tariff, Payment_method

        t = Tariff(name=f"t{months}", price=100)
        session.add(t)
        await session.flush()
        await session.commit()

        # добавим метод оплаты, соответствующий рассрочке
        pm = Payment_method(name=f"installment_{months}", installment_months=months)
        session.add(pm)
        await session.flush()
        await session.commit()

        payment_repo = PaymentRepository(session)

        amount = t.price
        resp, created = await payment_repo.post_new_payment(
            amount=amount,
            idempotency_key=None,
            tariff_id=t.id,
            installment_months=months,
            email="test@example.com",
            method=pm.name,
        )
        assert created is True
        schedule = resp.get("schedule")
        assert schedule is not None
        assert len(schedule) == months
        assert sum(schedule) == amount

    run_with_db(op)


def test_schedule_sum_equals_amount_3():
    run_test_for_months(3)


def test_schedule_sum_equals_amount_6():
    run_test_for_months(6)


def test_schedule_sum_equals_amount_12():
    run_test_for_months(12)
