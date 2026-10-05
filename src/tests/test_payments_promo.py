from src.tests.utils import run_with_db
from src.database.repository import (
    PaymentRepository,
    TariffRepository,
    PromocodeRepository,
)


def test_payment_without_and_with_promo():
    async def op(session):
        from src.database.models import Tariff, Promocode, Payment_method

        t = Tariff(name="test", price=10000)
        session.add(t)
        await session.flush()

        promo = Promocode(code="KVITTO10", discount_percentage=10)
        session.add(promo)
        await session.commit()

        # репозитории
        tariff_repo = TariffRepository(session)
        promocode_repo = PromocodeRepository(session)
        payment_repo = PaymentRepository(session)

        # добавим метод оплаты
        pm = Payment_method(name="card", installment_months=None)
        session.add(pm)
        await session.flush()
        await session.commit()

        tariff_obj = await tariff_repo.get_tariff_by_id(t.id)
        assert tariff_obj.price == 10000

        # без промокода
        payment_resp, created = await payment_repo.post_new_payment(
            amount=tariff_obj.price,
            idempotency_key=None,
            status="pending",
            tariff_id=tariff_obj.id,
            email="a@b.c",
            method=pm.name,
        )
        assert created is True
        assert payment_resp["amount"] == tariff_obj.price

        # с промокодом в нижнем регистре
        code_lower = "kvitto10"
        promo_obj = await promocode_repo.get_promocode_by_code(code_lower.upper())
        assert promo_obj is not None
        discount_amount = (tariff_obj.price * int(promo_obj.discount_percentage)) // 100

        payment_resp2, created2 = await payment_repo.post_new_payment(
            amount=tariff_obj.price - discount_amount,
            idempotency_key=None,
            status="pending",
            tariff_id=tariff_obj.id,
            discount=discount_amount,
            email="promo@b.c",
            method=pm.name,
        )
        assert created2 is True
        assert payment_resp2["amount"] == tariff_obj.price - discount_amount
        assert payment_resp2["discount"] == discount_amount

    run_with_db(op)
