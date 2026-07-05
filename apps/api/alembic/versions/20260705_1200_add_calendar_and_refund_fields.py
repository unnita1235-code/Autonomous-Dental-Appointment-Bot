"""Add google_calendar_event_id, calendar_sync_failed, stripe_refund_id.

Revision ID: 20260705_1200
Revises: 20260427_1419
Create Date: 2026-07-05 12:00:00.000000

"""
from __future__ import annotations

from typing import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260705_1200"
down_revision: str | None = "20260427_1419"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("appointments", schema=None) as batch_op:
        batch_op.add_column(sa.Column("google_calendar_event_id", sa.String(255), nullable=True))
        batch_op.add_column(sa.Column("calendar_sync_failed", sa.Boolean(), nullable=False, server_default=sa.text("false")))
        batch_op.add_column(sa.Column("stripe_refund_id", sa.String(255), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("appointments", schema=None) as batch_op:
        batch_op.drop_column("stripe_refund_id")
        batch_op.drop_column("calendar_sync_failed")
        batch_op.drop_column("google_calendar_event_id")
