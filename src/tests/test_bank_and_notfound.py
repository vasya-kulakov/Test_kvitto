from src.tests.utils import run_with_db
from src.database.repository import PaymentRepository, BankRepository


def test_forbidden_status_transition_and_notfound():
    async def op(session):
        from src.database.models import Tariff, Payment

        # создаём тариф и платёж
        t = Tariff(name="bank", price=1000)
        session.add(t)
        await session.flush()

        p = Payment(amount=1000, status="succeeded", tariff_id=t.id, email="x@y.z", method="card")
        session.add(p)
        await session.flush()
        await session.commit()

        bank_repo = BankRepository(session)

        # запрещённый переход: succeeded -> pending
        try:
            await bank_repo.change_status(p.id, "pending")
            assert False, "Expected ValueError"
        except ValueError:
            pass

        # убедимся, что статус не изменился
        pr = PaymentRepository(session)
        got = await pr.get_payment_by_id(p.id)
        assert got is not None
        assert got["status"] == "succeeded"

        # несуществующий платеж
        notfound = await pr.get_payment_by_id(9999999)
        assert notfound is None

    run_with_db(op)
