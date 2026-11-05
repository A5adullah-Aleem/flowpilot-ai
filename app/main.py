from fastapi import FastAPI
from sqlalchemy import text

from app.core.config import settings
from app.db.session import engine
from app.api.router import api_router

app = FastAPI(title=settings.app_name)




app.include_router(
    api_router,
    prefix="/api/v1",
)




@app.get("/")
def root():
    return {
        "message": "Welcome to FlowPilot AI",
        "status": "running",
    }


@app.get("/health")
def health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected",
        }

    except Exception:
        return {
            "status": "unhealthy",
            "database": "disconnected",
        }