"""Notification service: WhatsApp, Telegram, (email stub)."""
from __future__ import annotations

import hashlib
import hmac
import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

WHATSAPP_API_URL = "https://graph.facebook.com/v19.0"


async def send_whatsapp_text(to: str, message: str) -> bool:
    """Send a WhatsApp text message via Meta Business API."""
    if not settings.WHATSAPP_TOKEN or not settings.WHATSAPP_PHONE_NUMBER_ID:
        logger.warning("WhatsApp not configured — skipping send to %s", to)
        return False

    url = f"{WHATSAPP_API_URL}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"preview_url": False, "body": message},
    }
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            return True
    except Exception as exc:
        logger.error("send_whatsapp_text failed: %s", exc)
        return False


async def send_whatsapp_template(
    to: str,
    template_name: str,
    language_code: str = "en",
    components: list[dict] | None = None,
) -> bool:
    """Send a WhatsApp template message."""
    if not settings.WHATSAPP_TOKEN or not settings.WHATSAPP_PHONE_NUMBER_ID:
        return False

    url = f"{WHATSAPP_API_URL}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language_code},
            "components": components or [],
        },
    }
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            return True
    except Exception as exc:
        logger.error("send_whatsapp_template failed: %s", exc)
        return False


def verify_whatsapp_signature(payload: bytes, signature_header: str) -> bool:
    """Verify Meta webhook HMAC-SHA256 signature."""
    if not settings.WHATSAPP_TOKEN:
        return True  # Skip verification in dev
    mac = hmac.new(settings.WHATSAPP_TOKEN.encode(), payload, hashlib.sha256)
    expected = "sha256=" + mac.hexdigest()
    return hmac.compare_digest(expected, signature_header)


async def send_telegram_text(chat_id: str | int, message: str) -> bool:
    """Send a Telegram message via Bot API."""
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.warning("Telegram not configured — skipping send to %s", chat_id)
        return False

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            return True
    except Exception as exc:
        logger.error("send_telegram_text failed: %s", exc)
        return False


def parse_whatsapp_webhook(body: dict) -> list[dict]:
    """Extract messages from Meta WhatsApp webhook payload."""
    messages = []
    for entry in body.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            for msg in value.get("messages", []):
                messages.append(
                    {
                        "from": msg.get("from"),
                        "id": msg.get("id"),
                        "type": msg.get("type"),
                        "text": msg.get("text", {}).get("body", "") if msg.get("type") == "text" else "",
                        "phone_number_id": value.get("metadata", {}).get("phone_number_id"),
                        "timestamp": msg.get("timestamp"),
                    }
                )
    return messages


def parse_telegram_webhook(body: dict) -> dict | None:
    """Extract message from Telegram update payload."""
    message = body.get("message") or body.get("edited_message")
    if not message:
        return None
    return {
        "chat_id": message.get("chat", {}).get("id"),
        "from_id": message.get("from", {}).get("id"),
        "username": message.get("from", {}).get("username"),
        "text": message.get("text", ""),
        "message_id": message.get("message_id"),
    }


async def send_email_stub(to: str, subject: str, html_body: str) -> bool:
    """Email via SendGrid — stub until Phase 3 document/notification features."""
    if not settings.SENDGRID_API_KEY:
        logger.info("Email stub: would send to %s — subject: %s", to, subject)
        return True
    # TODO: Phase 3 — implement via SendGrid HTTP API
    logger.warning("send_email_stub: SendGrid integration pending (Phase 3)")
    return False
