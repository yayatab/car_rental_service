from fastapi import APIRouter, Depends, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import get_settings
from src.core.database import get_db_session
from src.schemas.common import HealthResponse

router = APIRouter(tags=["System"])
settings = get_settings()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns service health status and verifies database connectivity."
)
async def health_check(session: AsyncSession = Depends(get_db_session)) -> HealthResponse:
    db_status = "connected"
    try:
        await session.execute(text("SELECT 1"))
    except Exception as exc:
        db_status = f"unhealthy: {exc}"

    return HealthResponse(
        status="healthy" if db_status == "connected" else "degraded",
        version=settings.APP_VERSION,
        database=db_status
    )


@router.get(
    "/metrics",
    summary="Prometheus metrics",
    description="Exposes Prometheus metrics in standard exposition format."
)
async def metrics() -> Response:
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
