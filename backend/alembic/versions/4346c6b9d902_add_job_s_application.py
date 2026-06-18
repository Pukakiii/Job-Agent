"""add job's application

Revision ID: 4346c6b9d902
Revises: b2f1c0a9d3e7
Create Date: 2026-06-18 13:13:14.485420

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '4346c6b9d902'
down_revision: Union[str, Sequence[str], None] = 'b2f1c0a9d3e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# ENUM values — kept in sync with ApplicationStatus in app/models/application.py
_applicationstatus = sa.Enum(
    "saved", "applied", "interviewing", "offered", "rejected", "withdrawn",
    name="applicationstatus",
)


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Create the Postgres ENUM type first (must exist before the column).
    _applicationstatus.create(op.get_bind(), checkfirst=True)

    # 2. Create the job_applications table.
    op.create_table(
        "job_applications",
        sa.Column("id",         sa.Uuid(),                     nullable=False),
        sa.Column("user_id",    sa.Uuid(),                     nullable=False),
        sa.Column("job_id",     sa.Uuid(),                     nullable=False),
        sa.Column("cv_id",      sa.Uuid(),                     nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM(
                "saved", "applied", "interviewing", "offered", "rejected", "withdrawn",
                name="applicationstatus",
                create_type=False,   # already created above
            ),
            nullable=False,
            server_default="saved",
        ),
        sa.Column("applied_at", sa.DateTime(timezone=True),    nullable=True),
        sa.Column("notes",      sa.Text(),                     nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),    nullable=False,
                  server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True),    nullable=False,
                  server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_id"],  ["jobs.id"],  ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["cv_id"],   ["cvs.id"],   ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "job_id", name="uq_application_user_job"),
    )

    # 3. Individual column indexes.
    op.create_index(op.f("ix_job_applications_user_id"), "job_applications", ["user_id"])
    op.create_index(op.f("ix_job_applications_job_id"),  "job_applications", ["job_id"])
    op.create_index(op.f("ix_job_applications_cv_id"),   "job_applications", ["cv_id"])


def downgrade() -> None:
    """Downgrade schema."""
    # Reverse order: indexes → table → ENUM type.
    op.drop_index(op.f("ix_job_applications_cv_id"),   table_name="job_applications")
    op.drop_index(op.f("ix_job_applications_job_id"),  table_name="job_applications")
    op.drop_index(op.f("ix_job_applications_user_id"), table_name="job_applications")
    op.drop_table("job_applications")
    _applicationstatus.drop(op.get_bind(), checkfirst=True)

