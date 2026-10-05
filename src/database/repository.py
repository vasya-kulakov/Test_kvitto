from typing import List, Optional

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User


class TariffRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_tariffs(self, limit: int = 100, offset: int = 0) -> List[User]:
        q = select(User)
        result = await self.session.execute(q)
        return result.scalars().all()

    async def get_tariff_by_id(self, tariff_id: int) -> Optional[User]:
        q = select(User).where(User.id == tariff_id)
        result = await self.session.execute(q)
        return result.scalars().first()

class UserRepository:
    """Репозиторий для работы с моделью User."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, name: str, email: str) -> User:
        user = User(name=name, email=email)
        self.session.add(user)
        await self.session.flush()  # присвоит id
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_by_id(self, user_id: int) -> Optional[User]:
        q = select(User).where(User.id == user_id)
        result = await self.session.execute(q)
        return result.scalars().first()

    async def get_by_email(self, email: str) -> Optional[User]:
        q = select(User).where(User.email == email)
        result = await self.session.execute(q)
        return result.scalars().first()

    async def list_all(self, limit: int = 100, offset: int = 0) -> List[User]:
        q = select(User).limit(limit).offset(offset)
        result = await self.session.execute(q)
        return result.scalars().all()

    async def update(self, user_id: int, **fields) -> Optional[User]:
        q = select(User).where(User.id == user_id)
        result = await self.session.execute(q)
        user = result.scalars().first()
        if not user:
            return None
        for k, v in fields.items():
            if hasattr(user, k):
                setattr(user, k, v)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, user_id: int) -> bool:
        q = select(User).where(User.id == user_id)
        result = await self.session.execute(q)
        user = result.scalars().first()
        if not user:
            return False
        await self.session.delete(user)
        await self.session.commit()
        return True
