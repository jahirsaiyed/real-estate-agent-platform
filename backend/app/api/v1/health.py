from fastapi import APIRouter
from sqlalchemy import text

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.schemas.health import HealthResponse, ReadinessResponse, ServiceStatus

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["health"])
async def health() -> HealthResponse:
    return HealthResponse(status="ok", version=settings.APP_VERSION)


@router.get("/health/ready", response_model=ReadinessResponse, tags=["health"])
async def readiness() -> ReadinessResponse:
    services: dict[str, ServiceStatus] = {}

    # Check DB
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        services["database"] = ServiceStatus(status="connected")
    except Exception as exc:
        services["database"] = ServiceStatus(status="error", detail=str(exc))

    # Check Redis
    try:
        import redis.asyncio as aioredis

        client = aioredis.from_url(settings.REDIS_URL, socket_connect_timeout=2)
        await client.ping()
        await client.aclose()
        services["redis"] = ServiceStatus(status="connected")
    except Exception as exc:
        services["redis"] = ServiceStatus(status="error", detail=str(exc))

    # Check Qdrant (optional — may not be configured in local dev)
    try:
        from qdrant_client import AsyncQdrantClient

        qclient = AsyncQdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY or None)
        await qclient.get_collections()
        services["qdrant"] = ServiceStatus(status="connected")
    except Exception as exc:
        services["qdrant"] = ServiceStatus(status="error", detail=str(exc))

    overall = (
        "ok"
        if services.get("database", ServiceStatus(status="error")).status == "connected"
        else "degraded"
    )
    return ReadinessResponse(status=overall, services=services)
