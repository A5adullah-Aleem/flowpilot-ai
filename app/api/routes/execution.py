from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.agents.tool_agent import run_agent


router = APIRouter(
    prefix="/execution",
    tags=["Execution"],
)


class ExecutionRequest(BaseModel):
    user_request: str = Field(
        min_length=5,
        max_length=5000,
    )


@router.post("/run")
def execute_task(request: ExecutionRequest):

    result = run_agent(request.user_request)

    return {
        "user_request": request.user_request,
        "result": result,
    }