"""sensor readings and sampling

Revision ID: 528b479f59a7
Revises: b969746388c3
Create Date: 2026-09-30 10:51:32.760096
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "528b479f59a7"
down_revision: Union[str, Sequence[str], None] = "b969746388c3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create sensor_readings table
    op.create_table(
        "sensor_readings",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False,),
        sa.Column("device_id", sa.UUID(), nullable=False,),
        sa.Column("value", sa.Numeric(), nullable=False,),
        sa.Column("unit", sa.String(length=32), nullable=False,),
        sa.Column("source", sa.String(length=32), nullable=False,),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.text("now()"),nullable=False,),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"], ondelete="CASCADE",),
        sa.PrimaryKeyConstraint("id"),
    )

    # Index for reading history / latest reading
    op.create_index("ix_sensor_readings_device_recorded_at", "sensor_readings",
        [
            "device_id",
            sa.literal_column("recorded_at DESC"),
        ],
        unique=False,
    )

    # Add sampling settings to devices
    op.add_column(
        "devices",
        sa.Column(
            "sampling_interval_seconds",
            sa.Integer(),
            server_default=sa.text("300"),
            nullable=False,
        ),
    )

    op.add_column(
        "devices",
        sa.Column(
            "tracking_enabled",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
    )

    # Backfill sampling interval from default_config.
    # Use the old value only when it contains digits.
    # Otherwise keep the default value 300.
    op.execute(
        """
        UPDATE devices
        SET sampling_interval_seconds =
            (default_config->>'sampling_interval_seconds')::integer
        WHERE default_config->>'sampling_interval_seconds'
              ~ '^[0-9]+$'
        """
    )


def downgrade() -> None:
    op.drop_column("devices","tracking_enabled",)
    op.drop_column("devices","sampling_interval_seconds",)
    op.drop_index("ix_sensor_readings_device_recorded_at",table_name="sensor_readings",)
    op.drop_table("sensor_readings",)