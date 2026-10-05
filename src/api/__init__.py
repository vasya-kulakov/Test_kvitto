from .tariffs import router as tariffs_router
from fastapi import APIRouter
from .payments import router as payments_router
from .admin import router as admin_router
from .banks import router as banks_router
router = APIRouter()
router.include_router(tariffs_router)
router.include_router(payments_router)
router.include_router(admin_router)
router.include_router(banks_router)