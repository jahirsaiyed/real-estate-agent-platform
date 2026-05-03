import enum
import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, new_uuid


class DocumentType(str, enum.Enum):
    passport = "passport"
    proof_of_funds = "proof_of_funds"
    noc = "noc"
    soa = "soa"
    brochure = "brochure"
    report = "report"
    contract = "contract"
    other = "other"


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    lead_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("leads.id", ondelete="SET NULL"), nullable=True, index=True
    )
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True
    )
    type: Mapped[DocumentType] = mapped_column(
        sa.Enum(DocumentType, name="document_type"), nullable=False
    )
    filename: Mapped[str] = mapped_column(sa.String(500), nullable=False)
    r2_key: Mapped[str] = mapped_column(sa.String(500), nullable=False)
    r2_url: Mapped[str | None] = mapped_column(sa.String(1000), nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    mime_type: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)
    is_rag_indexed: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, server_default="false")
    qdrant_point_id: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
    )
