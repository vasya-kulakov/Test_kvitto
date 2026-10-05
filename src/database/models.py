from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime
import json

from .database import Base


class Tariff(Base):
    __tablename__ = "tariffs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(length=100), unique=True, nullable=False, index=True)
    price = Column(Integer, nullable=False, comment="Price in kopecks")

    def __repr__(self) -> str:  # pragma: no cover - простая отладочная строка
        return f"<Tariff id={self.id} name={self.name} price={self.price}>"


class Promocode(Base):
    __tablename__ = "promocodes"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(length=50), unique=True, nullable=False, index=True)
    discount_percentage = Column(Integer, nullable=False, comment="Discount percentage")


class Payment_method(Base):
    __tablename__ = "payment_methods"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(length=100), unique=True, nullable=False, index=True)
    installment_months = Column(Integer, nullable=True, comment='For installment plan')



class Payment(Base):
    __tablename__ = 'payments'
    id: int = Column(Integer, primary_key=True, index=True)
    status: str = Column(String(length=50), nullable=False, index=True)
    tariff_id: int = Column(Integer, nullable=False)
    amount: int = Column(Integer, nullable=False, comment="Amount in kopecks")
    discount: int | None = Column(Integer, nullable=True, comment="Discount in kopecks")
    method: str = Column(String(length=50), nullable=False)
    installment_months: int | None = Column(Integer, nullable=True)
    # schedule хранится как JSON-строка списка частей платежа в копейках
    schedule: int | None = Column(String, nullable=True, comment="Schedule as JSON string")
    email: str = Column(String(length=100), nullable=False, index=True)
    created_at: str = Column(DateTime, default=datetime.utcnow)
    idempotency_key: str | None = Column(String(length=100), unique=True, nullable=True, index=True)
    def to_response(self) -> dict:
        """Вернуть словарь-ответ для API, скрывая idempotency_key."""
        return {
            "id": self.id,
            "status": self.status,
            "tariff_id": self.tariff_id,
            "amount": self.amount,
            "discount": self.discount,
            "method": self.method,
            "installment_months": self.installment_months,
            "schedule": json.loads(self.schedule) if self.schedule else None,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at is not None else None,
        }



class AcceptBank(Base):
    __tablename__ = 'accept_bank'
    id: int = Column(Integer, primary_key=True, index=True)
    payment_id: int = Column(Integer, nullable=False)
    status: str = Column(String(length=50), nullable=False)
    