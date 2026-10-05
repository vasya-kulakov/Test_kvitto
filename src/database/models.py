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


