from pydantic import BaseModel, HttpUrl


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


class BrowserRunResult(BaseModel):
    status: str
    ats_type: str
    filled_fields: list[str]
    missing_fields: list[str]
    protected_fields: list[str]
    resume_uploaded: bool
    captcha_detected: bool
    submit_clicked: bool = False
    screenshot_path: str | None = None
