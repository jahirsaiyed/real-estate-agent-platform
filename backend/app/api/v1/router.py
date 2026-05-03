from fastapi import APIRouter

from app.api.v1 import (
    appointments,
    auth,
    calculators,
    conversations,
    health,
    leads,
    properties,
    webhooks,
)
from app.api.v1.conversations import ws_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(properties.router)
api_router.include_router(conversations.router)
api_router.include_router(ws_router)
api_router.include_router(appointments.router)
api_router.include_router(leads.router)
api_router.include_router(calculators.router)
api_router.include_router(webhooks.router)
