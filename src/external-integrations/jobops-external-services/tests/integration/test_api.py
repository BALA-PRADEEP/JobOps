from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient
from source.api.JobOpsAPI import app

client = TestClient(app)


def test_health():
    response = client.get("/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["auto_submit"] is False
    assert body["dry_run_ats"] == ["greenhouse"]


def test_job_analysis_and_idempotent_application_package():
    source_job_id = f"api-{uuid4()}"
    payload = {
        "source": "pytest",
        "source_job_id": source_job_id,
        "company": "Example",
        "title": "Integration Engineer",
        "location": "Bangalore",
        "work_mode": "hybrid",
        "posted_at": datetime.now(timezone.utc).isoformat(),
        "apply_url": "https://boards.greenhouse.io/example/jobs/abc",
        "description": (
            "2+ years Python FastAPI REST APIs OAuth PostgreSQL React "
            "TypeScript webhooks RAG embeddings vector search Azure "
            "Playwright"
        ),
        "salary_min_inr": 2_000_000,
        "salary_max_inr": 3_000_000,
    }
    response = client.post("/v1/jobs/analyze", json=payload)
    assert response.status_code == 200
    body = response.json()
    job_id = body["job"]["id"]
    assert body["analysis"]["ats_type"] == "greenhouse"

    package_1 = client.get(
        f"/v1/jobs/{job_id}/application-package"
    )
    package_2 = client.get(
        f"/v1/jobs/{job_id}/application-package"
    )
    assert package_1.status_code == 200
    assert package_2.status_code == 200
    assert (
        package_1.json()["application_id"]
        == package_2.json()["application_id"]
    )
    assert package_1.json()["submit_allowed"] is False
