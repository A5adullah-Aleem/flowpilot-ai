from fastapi import APIRouter

from app.api.routes.planning import router as planning_router


api_router = APIRouter()

api_router.include_router(planning_router)