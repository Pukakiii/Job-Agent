"""add cv is_active

Revision ID: a1b2c3d4e5f6
Revises: 4346c6b9d902
Create Date: 2026-06-24 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "4346c6b9d902"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "cvs",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.alter_column("cvs", "is_active", server_default=None)


def downgrade() -> None:
    op.drop_column("cvs", "is_active")
