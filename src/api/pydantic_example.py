from typing import List, Optional
from pydantic import BaseModel, Field


class PaymentResponse(BaseModel):
    id: int
    status: str
    tariff_id: int
    amount: int
    discount: Optional[int] = None
    method: Optional[str] = None
    installment_months: Optional[int] = None
    schedule: Optional[List[int]] = None
    email: Optional[str] = None
    created_at: Optional[str] = None


# Примеры запросов/ответов для OpenAPI
create_payment_example = {
    "summary": "Пример создания платежа",
    "description": "Создать платёж с тарифом basic, методом card и без промокода",
    "value": {
        "tariff_id": 1,
        "email": "user@example.com",
        "method": "card",
        "installment_months": None,
        "promo_code": None,
    },
}

create_payment_promo_example = {
    "summary": "Пример с промокодом",
    "description": "Создать платёж со скидкой через промокод",
    "value": {
        "tariff_id": 2,
        "email": "promo@example.com",
        "method": "card",
        "installment_months": None,
        "promo_code": "KVITTO10",
    },
}

create_payment_installment_example = {
    "summary": "Пример рассрочки",
    "description": "Создать платёж в рассрочку: сумма будет разбита на части",
    "value": {
        "tariff_id": 3,
        "email": "split@example.com",
        "method": "installment_3",
        "installment_months": 3,
        "promo_code": None,
    },
}

payment_response_example = {
    "id": 123,
    "status": "pending",
    "tariff_id": 1,
    "amount": 990000,
    "discount": 0,
    "method": "card",
    "installment_months": None,
    "schedule": None,
    "email": "user@example.com",
    "created_at": "2024-01-01T12:00:00Z",
}
