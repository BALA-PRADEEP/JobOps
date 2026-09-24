from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class JobCreate(BaseModel):
    source: str
    source_job_id: str
    company: str
    title: str
    location: str = ""
    work_mode: str | None = None
    posted_at: datetime
    apply_url: HttpUrl
    description: str
    salary_min_inr: int | None = None
    salary_max_inr: int | None = None


class JobRecord(JobCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    ats_type: str
    created_at: datetime


class JobAnalysis(BaseModel):
    freshness: str
    age_hours: float
    ats_type: str
    role_score: float
    experience_score: float
    backend_score: float
    integration_score: float
    frontend_score: float
    ai_score: float
    compensation_score: float
    location_score: float
    total_score: float = Field(ge=0, le=100)
    classification: str
    matched_skills: list[str]
    gaps: list[str]
    hard_failures: list[str]
    blockers: list[str]
    resume_key: str
    auto_apply_eligible: bool


class AnalyzeResponse(BaseModel):
    job: JobRecord
    analysis: JobAnalysis
