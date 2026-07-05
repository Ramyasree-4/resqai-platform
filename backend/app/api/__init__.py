from fastapi import APIRouter
from .auth import router as auth_router
from .incidents import router as incidents_router
from .resources import router as resources_router
from .notifications import router as notifications_router
from .analytics import router as analytics_router
from .ai import router as ai_router
from .admin import router as admin_router

api_router = APIRouter(prefix="/v1")
api_router.include_router(auth_router)
api_router.include_router(incidents_router)
api_router.include_router(resources_router)
api_router.include_router(notifications_router)
api_router.include_router(analytics_router)
api_router.include_router(ai_router)
api_router.include_router(admin_router)

__all__ = ["api_router"]
