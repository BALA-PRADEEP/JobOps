from datetime import datetime, timezone
from sqlalchemy import DateTime, Float, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from source.dal.db_session import Base


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (UniqueConstraint("source", "source_job_id", name="uq_job_source_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String(50), index=True)
    source_job_id: Mapped[str] = mapped_column(String(255))
    company: Mapped[str] = mapped_column(String(255), index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    location: Mapped[str] = mapped_column(String(255), default="")
    work_mode: Mapped[str | None] = mapped_column(String(50), nullable=True)
    posted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    apply_url: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    salary_min_inr: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_max_inr: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ats_type: Mapped[str] = mapped_column(String(50), default="generic")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class JobScore(Base):
    __tablename__ = "job_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int] = mapped_column(Integer, index=True)
    total: Mapped[float] = mapped_column(Float)
    classification: Mapped[str] = mapped_column(String(50))
    details_json: Mapped[str] = mapped_column(Text)
    resume_key: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
