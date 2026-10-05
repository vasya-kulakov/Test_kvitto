from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..database.repository import BankRepository
from ..database.database import get_session


router = APIRouter()


@router.post("/webhooks/bank")
async def change_status(
    payment_id: int,
    status: str,
    session: AsyncSession = Depends(get_session),
):
    bank_repo = BankRepository(session)
    try:
        await bank_repo.change_status(payment_id, status)
        return { "result": "ok" }
    except ValueError:
        raise HTTPException(status_code=409, detail={'error': "invalid_transition" })
