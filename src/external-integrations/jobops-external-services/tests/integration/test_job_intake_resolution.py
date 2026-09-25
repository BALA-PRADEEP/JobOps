from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from source.api.JobOpsAPI import app

client = TestClient(app)


def test_discovery_url_is_kept_separate_from_application_url():
    source_job_id = f"linkedin-{uuid4()}"
    intake_payload = {
        "source": "linkedin",
        "source_job_id": source_job_id,
        "company": "DigiCert",
        "title": "Software Engineer",
        "location": "Bengaluru, Karnataka",
        "work_mode": "hybrid",
        "posted_at": datetime.now(timezone.utc).isoformat(),
        "discovery_url": (
            "https://www.linkedin.com/jobs/view/software-engineer-at-digicert-4460939937/"
        ),
        "description": (
            "Software engineering role using Python, REST APIs, React, "
            "TypeScript and PostgreSQL."
        ),
    }

    intake = client.post("/v1/jobs/intake", json=intake_payload)
    assert intake.status_code == 200
    job = intake.json()
    assert job["resolver_status"] == "PENDING"
    assert job["discovery_url"].startswith("https://www.linkedin.com/")
    assert job["application_url"] is None
    assert job["ats_type"] == "pending"

    resolved = client.post(
        f"/v1/jobs/{job['id']}/resolve",
        json={
            "canonical_job_url": "https://www.digicert.com/company/careers/job/123",
            "application_url": "https://boards.greenhouse.io/digicert/jobs/123",
        },
    )
    assert resolved.status_code == 200
    body = resolved.json()
    assert body["job"]["resolver_status"] == "RESOLVED"
    assert body["job"]["application_url"].startswith("https://boards.greenhouse.io/")
    assert body["job"]["ats_type"] == "greenhouse"
    assert body["analysis"]["ats_type"] == "greenhouse"
    assert body["analysis"]["classification"] in {
        "STRONG_MATCH",
        "REVIEW",
        "SELECTIVE",
        "SKIP",
    }
