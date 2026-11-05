from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.agents.task_planner import generate_plan

router = APIRouter(
    prefix="/planning",
    tags=["Planning"],
)


class TaskRequest(BaseModel):
    user_request: str = Field(
        min_length=5,
        max_length=5000,
    )


@router.post("/plan")
def create_execution_plan(request: TaskRequest):
    plan = generate_plan(request.user_request)

    return {
        "user_request": request.user_request,
        "execution_plan": plan,
    }