from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from source.api.JobOpsAPI import app
from source.dal.ApplicationRepository import ApplicationRepository
from source.dal.db_session import SessionLocal
from source.externalService.ats.ATSAdapterRegistry import ATSAdapterRegistry
from source.schemas.ApplicationSchemas import (
    BrowserTraceEvent,
    DryRunResult,
)

client = TestClient(app)


class FakeAdapter:
    def run_dry_run(
        self,
        url: str,
        artifact_dir: str | None = None,
    ):
        return DryRunResult(
            status="NEEDS_INPUT",
            ats_type="greenhouse",
            filled_fields=["First Name", "Email"],
            missing_fields=["Why do you want to work here?"],
            protected_fields=["Expected salary"],
            resume_uploaded=True,
            captcha_detected=False,
            submit_clicked=False,
            trace=[
                BrowserTraceEvent(
                    step="submit_gate",
                    status="stopped",
                    detail="dry run",
                )
            ],
            fields=[],
        )


def test_dry_run_persists_safe_state_transition(monkeypatch):
    monkeypatch.setattr(
        ATSAdapterRegistry,
        "create",
        classmethod(
            lambda cls, *args, **kwargs: FakeAdapter()
        ),
    )
    source_job_id = f"exec-{uuid4()}"
    payload = {
        "source": "pytest",
        "source_job_id": source_job_id,
        "company": "Example",
        "title": "Product Engineer Applied AI",
        "location": "Bengaluru",
        "work_mode": "hybrid",
        "posted_at": datetime.now(timezone.utc).isoformat(),
        "apply_url": (
            "https://boards.greenhouse.io/example/jobs/exec"
        ),
        "description": (
            "2+ years Python FastAPI REST APIs OAuth PostgreSQL React "
            "TypeScript RAG embeddings vector search Azure Playwright"
        ),
        "salary_min_inr": 2_000_000,
        "salary_max_inr": 3_000_000,
    }
    analyzed = client.post("/v1/jobs/analyze", json=payload)
    assert analyzed.status_code == 200
    job_id = analyzed.json()["job"]["id"]

    dry_run = client.post(
        f"/v1/jobs/{job_id}/dry-run"
    )
    assert dry_run.status_code == 200
    body = dry_run.json()
    assert body["status"] == "NEEDS_INPUT"
    assert body["submit_clicked"] is False

    with SessionLocal() as session:
        application = ApplicationRepository(
            session
        ).get_by_job_id(job_id)
        assert application is not None
        assert application.state == "NEEDS_INPUT"
