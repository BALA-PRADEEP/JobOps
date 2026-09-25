"""add discovery and application resolution fields

Revision ID: 0002_job_resolution
Revises: 0001_initial_architecture
Create Date: 2026-09-25
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002_job_resolution"
down_revision: Union[str, None] = "0001_initial_architecture"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("jobs", sa.Column("discovery_url", sa.Text(), nullable=True))
    op.add_column("jobs", sa.Column("canonical_job_url", sa.Text(), nullable=True))
    op.add_column("jobs", sa.Column("application_url", sa.Text(), nullable=True))
    op.add_column(
        "jobs",
        sa.Column(
            "resolver_status",
            sa.String(length=30),
            nullable=False,
            server_default="RESOLVED",
        ),
    )
    op.execute("UPDATE jobs SET discovery_url = apply_url, application_url = apply_url")


def downgrade() -> None:
    op.drop_column("jobs", "resolver_status")
    op.drop_column("jobs", "application_url")
    op.drop_column("jobs", "canonical_job_url")
    op.drop_column("jobs", "discovery_url")
