from typing import List, Optional

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Tariff

class TariffRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_tariffs(self, limit: int = 100, offset: int = 0) -> List[Tariff]:
        q = select(Tariff)
        result = await self.session.execute(q)  
        return result.scalars().all()

    async def get_tariff_by_id(self, tariff_id: int) -> Optional[Tariff]:
        q = select(Tariff).where(Tariff.id == tariff_id)
        result = await self.session.execute(q)
        return result.scalars().first()