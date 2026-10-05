from src.tests.utils import run_with_db
from src.database.repository import PaymentRepository


def test_idempotency_prevents_duplicate():
    async def op(session):
        from src.database.models import Tariff, Payment_method

        t = Tariff(name="idemp", price=500)
        session.add(t)
        await session.flush()
        await session.commit()

        pm = Payment_method(name="card", installment_months=None)
        session.add(pm)
        await session.flush()
        await session.commit()

        payment_repo = PaymentRepository(session)
        key = "idem-key-123"

        resp1, created1 = await payment_repo.post_new_payment(
            amount=t.price,
            idempotency_key=key,
            tariff_id=t.id,
            email="a@b.c",
            method=pm.name,
        )
        assert created1 is True
        resp2, created2 = await payment_repo.post_new_payment(
            amount=t.price,
            idempotency_key=key,
            tariff_id=t.id,
            email="a@b.c",
            method=pm.name,
        )
        assert created2 is False
        assert resp1["id"] == resp2["id"]

    run_with_db(op)
