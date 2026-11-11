from fastapi import APIRouter

from app.modules.accounts.router import router as accounts_router
from app.modules.data_exports.router import router as data_exports_router
from app.modules.health.router import router as health_router
from app.modules.image_jobs.router import router as image_jobs_router
from app.modules.insights.router import router as insights_router
from app.modules.media.router import router as media_router
from app.modules.notifications.router import router as notifications_router
from app.modules.outfits.router import router as outfits_router
from app.modules.planner.router import router as planner_router
from app.modules.settings.router import router as settings_router
from app.modules.support.router import router as support_router
from app.modules.wardrobe.router import router as wardrobe_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(health_router)
api_v1_router.include_router(accounts_router)
api_v1_router.include_router(settings_router)
api_v1_router.include_router(data_exports_router)
api_v1_router.include_router(notifications_router)
api_v1_router.include_router(support_router)
api_v1_router.include_router(media_router)
api_v1_router.include_router(image_jobs_router)
api_v1_router.include_router(wardrobe_router)
api_v1_router.include_router(outfits_router)
api_v1_router.include_router(planner_router)
api_v1_router.include_router(insights_router)

