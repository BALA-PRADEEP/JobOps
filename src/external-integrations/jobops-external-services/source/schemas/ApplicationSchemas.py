from datetime import datetime
from pydantic import BaseModel, ConfigDict, HttpUrl


class ApplicationPackage(BaseModel):
    job_id: int
    application_id: int
    state: str
    resume_key: str
    resume_path: str
    known_fields: dict[str, str]
    missing_protected_fields: list[str]
    generated_drafts: dict[str, str]
    ats_type: str
    apply_url: HttpUrl
    submit_allowed: bool = False


class ExecutionRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    application_id: int
    action: str
    status: str
    attempt_count: int
    last_error: str | None = None
    created_at: datetime
    updated_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None


class BrowserTraceEvent(BaseModel):
    step: str
    status: str
    detail: str


class ApplicationFieldResult(BaseModel):
    descriptor: str
    field_type: str
    status: str
    value_source: str | None = None


class DryRunResult(BaseModel):
    status: str
    ats_type: str
    filled_fields: list[str]
    missing_fields: list[str]
    protected_fields: list[str]
    resume_uploaded: bool
    captcha_detected: bool
    submit_clicked: bool = False
    trace: list[BrowserTraceEvent]
    fields: list[ApplicationFieldResult]
    screenshot_path: str | None = None
    result_path: str | None = None
