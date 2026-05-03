import enum
import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, new_uuid


class UserRole(str, enum.Enum):
    superadmin = "superadmin"
    tenant_admin = "tenant_admin"
    agent = "agent"
    readonly = "readonly"


class UserLanguage(str, enum.Enum):
    en = "en"
    ar = "ar"
    hi = "hi"
    ru = "ru"


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(sa.String(255), nullable=False, unique=True, index=True)
    full_name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        sa.Enum(UserRole, name="user_role"), nullable=False, server_default=UserRole.agent.value
    )
    language: Mapped[UserLanguage] = mapped_column(
        sa.Enum(UserLanguage, name="user_language"),
        nullable=False,
        server_default=UserLanguage.en.value,
    )
    is_active: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, server_default="true")
    last_login_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
