"""Add slug column to properties table.

Revision ID: 002
Revises: 001
Create Date: 2026-05-03
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "properties",
        sa.Column("slug", sa.String(600), nullable=True),
    )
    op.create_index("idx_properties_slug", "properties", ["tenant_id", "slug"])


def downgrade() -> None:
    op.drop_index("idx_properties_slug", table_name="properties")
    op.drop_column("properties", "slug")
