"""rename device family index

Revision ID: d07b7d3fe1be
Revises: 552aa9ec2998
Create Date: 2026-09-23 11:23:16.855322

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd07b7d3fe1be'
down_revision: Union[str, Sequence[str], None] = '552aa9ec2998'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index("ix_devices_device_family", table_name="devices")
    op.create_index(
        "ix_devices_family",
        "devices",
        ["device_family"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_devices_family", table_name="devices")
    op.create_index(
        "ix_devices_device_family",
        "devices",
        ["device_family"],
        unique=False,
    )
