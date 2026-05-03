from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    version: str


class ServiceStatus(BaseModel):
    status: str
    detail: str | None = None


class ReadinessResponse(BaseModel):
    status: str
    services: dict[str, ServiceStatus]
