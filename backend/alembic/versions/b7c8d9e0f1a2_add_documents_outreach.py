"""documents and outreach tables

Revision ID: b7c8d9e0f1a2
Revises: a1b2c3d4e5f6
Create Date: 2026-06-24 14:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b7c8d9e0f1a2"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_documenttype = sa.Enum("resume", "cover_letter", name="documenttype")
_outreachstatus = sa.Enum("draft", "sent", "failed", name="outreachstatus")


def upgrade() -> None:
    op.create_table(
        "generated_documents",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("job_id", sa.Uuid(), nullable=False),
        sa.Column("cv_id", sa.Uuid(), nullable=True),
        sa.Column("doc_type", _documenttype, nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["cv_id"], ["cvs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_generated_documents_user_id", "generated_documents", ["user_id"])

    op.create_table(
        "outreach_emails",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("job_id", sa.Uuid(), nullable=True),
        sa.Column("application_id", sa.Uuid(), nullable=True),
        sa.Column("to_address", sa.Text(), nullable=False),
        sa.Column("subject", sa.Text(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("status", _outreachstatus, nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["application_id"], ["job_applications.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_outreach_emails_user_id", "outreach_emails", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_outreach_emails_user_id", table_name="outreach_emails")
    op.drop_table("outreach_emails")
    op.drop_index("ix_generated_documents_user_id", table_name="generated_documents")
    op.drop_table("generated_documents")
    _outreachstatus.drop(op.get_bind(), checkfirst=True)
    _documenttype.drop(op.get_bind(), checkfirst=True)
