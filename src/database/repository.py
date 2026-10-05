from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
import json

from .models import Tariff, Promocode, Payment_method, Payment


class TariffRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_tariffs(self, limit: int = 100, offset: int = 0) -> List[Tariff]:
        q = select(Tariff).limit(limit).offset(offset)
        result = await self.session.execute(q)
        return result.scalars().all()

    async def get_tariff_by_id(self, tariff_id: int) -> Optional[Tariff]:
        q = select(Tariff).where(Tariff.id == tariff_id)
        result = await self.session.execute(q)
        return result.scalars().first()


class PromocodeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_promocode_by_code(self, code: str) -> Optional[Promocode]:
        q = select(Promocode).where(Promocode.code == code)
        result = await self.session.execute(q)
        return result.scalars().first()


class PaymentMethodRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_payment_method_by_name(self, name: str) -> Optional[Payment_method]:
        q = select(Payment_method).where(Payment_method.name == name)
        result = await self.session.execute(q)
        return result.scalars().first()


class BankRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def change_status(self, payment_id: int, new_status: str) -> None:
        right_changes = {
            "pending": ["succeeded", "failed"],
            "succeeded": ["refunded"]
        }
        q = select(Payment).where(Payment.id == payment_id)
        result = await self.session.execute(q)
        payment = result.scalars().first()
        if payment:
            if right_changes[payment.status] and new_status in right_changes[payment.status]:
                payment.status = new_status
                await self.session.commit()
            else:
                raise ValueError()

class PaymentRepository:
    """Репозиторий для работы с платежами.

    Логика идемпотентности основана на уникальном поле Payment.idempotency_key.
    При повторном запросе с тем же idempotency_key возвращается существующий
    платеж. Для предотвращения гонок обрабатываем IntegrityError.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_payment_by_id(self, payment_id: int) -> Optional[Payment]:
        q = select(Payment).where(Payment.id == payment_id)
        result = await self.session.execute(q)
        payment = result.scalars().first()
        return payment.to_response() if payment is not None else None

    async def post_new_payment(
        self,
        amount: int,
        idempotency_key: Optional[str] = None,
        status: str = "pending",
        tariff_id: Optional[int] = None,
        discount: Optional[int] = 0,
        method: Optional[str] = None,
        installment_months: Optional[int] = None,
        schedule: Optional[str] = None,
        email: Optional[str] = None,
    ) -> tuple[dict, bool]:
        """Создать новый платеж. Если передан idempotency_key — вернуть существующий
        платеж с таким ключом или создать новый; гонки обрабатываются через
        IntegrityError и повторный запрос к базе.
        """
        # Подготовим schedule: если рассрочка указана (>1), разобьём сумму на части
        schedule_json = None
        if installment_months and installment_months > 1:
            n = int(installment_months)
            total = int(amount)
            base = total // n
            rem = total % n
            # первые rem платежей получают по base+1, остальные по base
            parts = [base + 1] * rem + [base] * (n - rem)
            schedule_json = json.dumps(parts)

        # используем schedule_json при создании записи

        if idempotency_key:
            # Сначала проверим, нет ли уже платежа с таким ключом
            q = select(Payment).where(Payment.idempotency_key == idempotency_key)
            result = await self.session.execute(q)
            existing = result.scalars().first()
            if existing:
                return existing.to_response(), False

            # Не найден — пытаемся создать новый платеж с полем idempotency_key
            payment = Payment(
                amount=amount,
                status=status,
                tariff_id=tariff_id,
                discount=discount,
                method=method,
                installment_months=installment_months,
                schedule=schedule_json,
                email=email,
                idempotency_key=idempotency_key,
            )
            self.session.add(payment)
            try:
                await self.session.flush()
                await self.session.commit()
                await self.session.refresh(payment)
                return payment.to_response(), True
            except IntegrityError:
                # Гонка: другой процесс мог вставить запись с тем же ключом
                await self.session.rollback()
                q2 = select(Payment).where(Payment.idempotency_key == idempotency_key)
                result2 = await self.session.execute(q2)
                existing2 = result2.scalars().first()
                if existing2:
                    return existing2.to_response(), False
                raise
        else:
            # Обычное создание без idempotency
            payment = Payment(
                amount=amount,
                status=status,
                tariff_id=tariff_id,
                discount=discount,
                method=method,
                installment_months=installment_months,
                schedule=schedule_json,
                email=email,
            )
            self.session.add(payment)
            await self.session.flush()
            await self.session.commit()
            await self.session.refresh(payment)
            return payment.to_response(), True

