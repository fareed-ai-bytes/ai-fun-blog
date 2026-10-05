from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["health"])


class HealthStatus(BaseModel):
    status: str


@router.get(
    "/health",
    response_model=HealthStatus,
    status_code=200,
    operation_id="health_get",
    summary="Liveness check",
)
def get_health() -> HealthStatus:
    return HealthStatus(status="ok")
