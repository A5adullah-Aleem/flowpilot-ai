from fastapi import APIRouter

from app.api.routes.planning import router as planning_router
from app.api.routes.execution import router as execution_router

api_router = APIRouter()

api_router.include_router(planning_router)
api_router.include_router(execution_router)
