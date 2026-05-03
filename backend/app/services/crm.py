"""CRM integration service: Zoho + HubSpot adapters (Sprint 2 stubs, full in Phase 3)."""
from __future__ import annotations

import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class ZohoAdapter:
    """Zoho CRM adapter. Full OAuth flow in Phase 3."""

    BASE_URL = "https://www.zohoapis.com/crm/v3"

    async def _get_access_token(self) -> str | None:
        if not all([settings.ZOHO_CLIENT_ID, settings.ZOHO_CLIENT_SECRET, settings.ZOHO_REFRESH_TOKEN]):
            return None
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(
                    "https://accounts.zoho.com/oauth/v2/token",
                    params={
                        "refresh_token": settings.ZOHO_REFRESH_TOKEN,
                        "client_id": settings.ZOHO_CLIENT_ID,
                        "client_secret": settings.ZOHO_CLIENT_SECRET,
                        "grant_type": "refresh_token",
                    },
                )
                resp.raise_for_status()
                return resp.json().get("access_token")
        except Exception as exc:
            logger.error("Zoho token refresh failed: %s", exc)
            return None

    async def upsert_lead(self, lead_data: dict) -> str | None:
        """Create or update a Zoho CRM contact. Returns Zoho contact ID."""
        token = await self._get_access_token()
        if not token:
            logger.info("Zoho not configured — skipping CRM sync")
            return None
        try:
            payload = {
                "data": [
                    {
                        "Last_Name": lead_data.get("full_name", "Unknown"),
                        "Email": lead_data.get("email"),
                        "Phone": lead_data.get("phone"),
                        "Lead_Source": lead_data.get("source_channel", "Web"),
                        "Description": f"Budget: {lead_data.get('budget_max_aed')} AED",
                    }
                ]
            }
            headers = {"Authorization": f"Zoho-oauthtoken {token}"}
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(f"{self.BASE_URL}/Leads", json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                return data.get("data", [{}])[0].get("details", {}).get("id")
        except Exception as exc:
            logger.error("Zoho upsert_lead failed: %s", exc)
            return None


class HubSpotAdapter:
    """HubSpot CRM adapter."""

    BASE_URL = "https://api.hubapi.com"

    async def upsert_contact(self, lead_data: dict) -> str | None:
        """Create or update a HubSpot contact. Returns HubSpot contact ID."""
        if not settings.HUBSPOT_API_KEY:
            logger.info("HubSpot not configured — skipping CRM sync")
            return None
        try:
            payload = {
                "properties": {
                    "firstname": (lead_data.get("full_name") or "").split()[0] if lead_data.get("full_name") else "",
                    "lastname": " ".join((lead_data.get("full_name") or "").split()[1:]),
                    "email": lead_data.get("email"),
                    "phone": lead_data.get("phone"),
                    "hs_lead_status": "NEW",
                }
            }
            headers = {
                "Authorization": f"Bearer {settings.HUBSPOT_API_KEY}",
                "Content-Type": "application/json",
            }
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(
                    f"{self.BASE_URL}/crm/v3/objects/contacts",
                    json=payload,
                    headers=headers,
                )
                resp.raise_for_status()
                return str(resp.json().get("id"))
        except Exception as exc:
            logger.error("HubSpot upsert_contact failed: %s", exc)
            return None


zoho_adapter = ZohoAdapter()
hubspot_adapter = HubSpotAdapter()


async def sync_lead_to_crm(lead_data: dict) -> str | None:
    """Try Zoho first, fall back to HubSpot. Returns external CRM contact ID."""
    if settings.ZOHO_CLIENT_ID:
        contact_id = await zoho_adapter.upsert_lead(lead_data)
        if contact_id:
            return f"zoho:{contact_id}"

    if settings.HUBSPOT_API_KEY:
        contact_id = await hubspot_adapter.upsert_contact(lead_data)
        if contact_id:
            return f"hubspot:{contact_id}"

    return None
