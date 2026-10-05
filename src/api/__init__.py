from .tariffs import router as tariffs_router
from fastapi import APIRouter

 
router = APIRouter()
router.include_router(tariffs_router)