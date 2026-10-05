from FastApi import ApiRouter
from ..database import AsyncSession
from ..repository import TariffRepository
router = ApiRouter()


@router.get('/tariffs')
async def tariffs(session: AsyncSession):
    ans = await TariffRepository(session).get_tariffs()
    return ans