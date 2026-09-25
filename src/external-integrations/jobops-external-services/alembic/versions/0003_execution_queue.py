"""add execution request queue

Revision ID: 0003_execution_queue
Revises: 0002_job_resolution
Create Date: 2026-09-25
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003_execution_queue"
down_revision: Union[str, None] = "0002_job_resolution"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "execution_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("application_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=30), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_execution_requests_application_id",
        "execution_requests",
        ["application_id"],
    )
    op.create_index(
        "ix_execution_requests_status",
        "execution_requests",
        ["status"],
    )


def downgrade() -> None:
    op.drop_index("ix_execution_requests_status", table_name="execution_requests")
    op.drop_index("ix_execution_requests_application_id", table_name="execution_requests")
    op.drop_table("execution_requests")
