from fastapi import APIRouter, Depends, HTTPException, Body, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ..scripts.idempotency import IdempotentRequest, generate_key
from fastapi.responses import JSONResponse
from .pydantic_shamples import PaymentModel
from ..database import get_session
from ..database.repository import (
    PaymentRepository,
    TariffRepository,
    PromocodeRepository,
    PaymentMethodRepository,
)

router = APIRouter()


@router.post("/payments")
async def create_payment(
    payload: PaymentModel = Body(...),
    idempotency_key: str | None = Depends(IdempotentRequest()),
    session: AsyncSession = Depends(get_session),
    request: Request = None,
):
    """Создать платёж с поддержкой идемпотентности и промокодов."""
    # Репозитории
    tariff_repo = TariffRepository(session)
    promocode_repo = PromocodeRepository(session)
    pm_repo = PaymentMethodRepository(session)
    payment_repo = PaymentRepository(session)

    # Получаем тариф
    tariff = await tariff_repo.get_tariff_by_id(payload.tariff_id)
    if not tariff:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid tariff_id")

    # Обработка промокода (если передан)
    discount_amount = 0
    if payload.promo_code:
        code = payload.promo_code.upper()
        promocode = await promocode_repo.get_promocode_by_code(code)
        if not promocode:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid promocode")
        # скидка в процентах
        discount_amount = (tariff.price * int(promocode.discount_percentage)) // 100

    # Определяем метод оплаты и installment_months
    pm = await pm_repo.get_payment_method_by_name(payload.method)
    if not pm:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid payment method")

    installment_months = pm.installment_months if pm.installment_months is not None else payload.installment_months

    # Итоговая сумма
    amount = tariff.price - (discount_amount or 0)

    # Если idempotency_key не передан — сгенерируем свой
    if not idempotency_key:
        idempotency_key = generate_key()

    # Вызов репозитория: он вернёт кортеж (response_dict, created_flag)
    payment, created = await payment_repo.post_new_payment(
        amount=amount,
        idempotency_key=idempotency_key,
        status="pending",
        tariff_id=payload.tariff_id,
        discount=discount_amount,
        method=pm.name,
        installment_months=installment_months,
        schedule=None,
        email=payload.email,
    )
    return JSONResponse(content=payment, status_code=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


@router.get("/payments/{payment_id}")
async def get_payment(payment_id: int, session: AsyncSession = Depends(get_session)):
    """Получить платёж по ID."""
    payment_repo = PaymentRepository(session)
    payment = await payment_repo.get_payment_by_id(payment_id)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    return payment
