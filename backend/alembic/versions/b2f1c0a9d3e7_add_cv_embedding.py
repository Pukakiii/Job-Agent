"""add cv embedding

Revision ID: b2f1c0a9d3e7
Revises: 00e191b3e6e3
Create Date: 2026-06-14 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import pgvector.sqlalchemy.vector

# revision identifiers, used by Alembic.
revision: str = 'b2f1c0a9d3e7'
down_revision: Union[str, Sequence[str], None] = '00e191b3e6e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Cache the CV embedding so searches reuse it instead of re-embedding the CV text.
    Nullable: existing rows (and CVs whose embed step failed) stay NULL and matching
    falls back to embedding the query text live. The `vector` extension already exists
    (created in the initial migration)."""
    op.add_column(
        "cvs",
        sa.Column("embedding", pgvector.sqlalchemy.vector.VECTOR(dim=768), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("cvs", "embedding")
