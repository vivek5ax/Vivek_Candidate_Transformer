from fastapi import APIRouter

from app.api.routes.health import router as health_router
from app.api.routes.extract import router as extract_router
from app.config.settings import settings

router = APIRouter(prefix=settings.API_PREFIX)

router.include_router(health_router)
router.include_router(extract_router, prefix="/extract")