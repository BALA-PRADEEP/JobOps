"""initial JobOps schema

Revision ID: 0001_initial_architecture
Revises:
Create Date: 2026-09-24
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial_architecture"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("source_job_id", sa.String(length=255), nullable=False),
        sa.Column("company", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=False),
        sa.Column("work_mode", sa.String(length=50), nullable=True),
        sa.Column("posted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("apply_url", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("salary_min_inr", sa.Integer(), nullable=True),
        sa.Column("salary_max_inr", sa.Integer(), nullable=True),
        sa.Column("ats_type", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("source", "source_job_id", name="uq_job_source_id"),
    )
    op.create_index("ix_jobs_source", "jobs", ["source"])
    op.create_index("ix_jobs_company", "jobs", ["company"])
    op.create_index("ix_jobs_title", "jobs", ["title"])
    op.create_index("ix_jobs_posted_at", "jobs", ["posted_at"])

    op.create_table(
        "job_scores",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("total", sa.Float(), nullable=False),
        sa.Column("classification", sa.String(length=50), nullable=False),
        sa.Column("details_json", sa.Text(), nullable=False),
        sa.Column("resume_key", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_job_scores_job_id", "job_scores", ["job_id"])

    op.create_table(
        "applications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("state", sa.String(length=50), nullable=False),
        sa.Column("resume_key", sa.String(length=50), nullable=True),
        sa.Column("blockers_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("job_id", name="uq_application_job"),
    )
    op.create_index("ix_applications_job_id", "applications", ["job_id"])
    op.create_index("ix_applications_state", "applications", ["state"])

    op.create_table(
        "application_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("application_id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_application_events_application_id", "application_events", ["application_id"])
    op.create_index("ix_application_events_event_type", "application_events", ["event_type"])

    op.create_table(
        "browser_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("application_id", sa.Integer(), nullable=False),
        sa.Column("ats_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("artifact_json", sa.Text(), nullable=False),
        sa.Column("submit_clicked", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_browser_runs_application_id", "browser_runs", ["application_id"])
    op.create_index("ix_browser_runs_ats_type", "browser_runs", ["ats_type"])
    op.create_index("ix_browser_runs_status", "browser_runs", ["status"])


def downgrade() -> None:
    op.drop_index("ix_browser_runs_status", table_name="browser_runs")
    op.drop_index("ix_browser_runs_ats_type", table_name="browser_runs")
    op.drop_index("ix_browser_runs_application_id", table_name="browser_runs")
    op.drop_table("browser_runs")

    op.drop_index("ix_application_events_event_type", table_name="application_events")
    op.drop_index("ix_application_events_application_id", table_name="application_events")
    op.drop_table("application_events")

    op.drop_index("ix_applications_state", table_name="applications")
    op.drop_index("ix_applications_job_id", table_name="applications")
    op.drop_table("applications")

    op.drop_index("ix_job_scores_job_id", table_name="job_scores")
    op.drop_table("job_scores")

    op.drop_index("ix_jobs_posted_at", table_name="jobs")
    op.drop_index("ix_jobs_title", table_name="jobs")
    op.drop_index("ix_jobs_company", table_name="jobs")
    op.drop_index("ix_jobs_source", table_name="jobs")
    op.drop_table("jobs")
