from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from source.api.JobOpsAPI import app
from source.dal.ApplicationRepository import (
    ApplicationRepository,
    ExecutionRequestRepository,
)
from source.dal.db_session import SessionLocal

client = TestClient(app)


def test_dry_run_endpoint_queues_worker_execution():
    source_job_id = f"exec-{uuid4()}"
    payload = {
        "source": "pytest",
        "source_job_id": source_job_id,
        "company": "Example",
        "title": "Product Engineer Applied AI",
        "location": "Bengaluru",
        "work_mode": "hybrid",
        "posted_at": datetime.now(timezone.utc).isoformat(),
        "apply_url": "https://boards.greenhouse.io/example/jobs/exec",
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

    queued = client.post(f"/v1/jobs/{job_id}/dry-run")
    assert queued.status_code == 200
    body = queued.json()
    assert body["status"] == "QUEUED"
    assert body["action"] == "DRY_RUN"
    assert body["attempt_count"] == 0

    duplicate = client.post(f"/v1/jobs/{job_id}/dry-run")
    assert duplicate.status_code == 200
    assert duplicate.json()["id"] == body["id"]

    request_status = client.get(
        f"/v1/jobs/execution-requests/{body['id']}"
    )
    assert request_status.status_code == 200
    assert request_status.json()["status"] == "QUEUED"

    with SessionLocal() as session:
        application = ApplicationRepository(session).get_by_job_id(job_id)
        assert application is not None
        request = ExecutionRequestRepository(session).get(body["id"])
        assert request is not None
        assert request.application_id == application.id
        assert request.status == "QUEUED"
