"""devices

Revision ID: ea58679f7e69
Revises: 001
Create Date: 2026-09-09 11:25:43.394728
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "ea58679f7e69"
down_revision: Union[str, Sequence[str], None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "devices",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("device_type", sa.String(length=50), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("default_config", sa.JSON(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_devices_role",
        "devices",
        ["role"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_devices_role",
        table_name="devices",
    )
    op.drop_table("devices")