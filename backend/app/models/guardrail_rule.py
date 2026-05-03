import enum
import uuid

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, new_uuid


class GuardrailRuleType(str, enum.Enum):
    blocked_topic = "blocked_topic"
    required_disclaimer = "required_disclaimer"
    competitor_mention = "competitor_mention"
    price_guarantee = "price_guarantee"


class GuardrailRule(TimestampMixin, Base):
    __tablename__ = "guardrail_rules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    rule_name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    rule_type: Mapped[GuardrailRuleType] = mapped_column(
        sa.Enum(GuardrailRuleType, name="guardrail_rule_type"), nullable=False
    )
    rule_pattern: Mapped[str] = mapped_column(sa.Text, nullable=False)
    disclaimer_text: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, server_default="true")
