from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from ..database.database import AsyncClient, get_session
from ..database.repository import TariffRepository
router = APIRouter()

@router.get('/tariffs')
async def tariffs(session: AsyncSession = Depends(get_session)):
    ans = await TariffRepository(session).get_tariffs()
    return ans

