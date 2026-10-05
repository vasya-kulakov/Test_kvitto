from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime

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
