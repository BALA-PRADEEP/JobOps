from datetime import datetime, timedelta, timezone

from source.schemas.JobSchemas import JobCreate
from source.service.JobAnalysisService import JobAnalysisService


def make_job(**overrides):
    data = dict(
        source="test",
        source_job_id="1",
        company="Example AI",
        title="Product Engineer",
        location="Bengaluru",
        work_mode="hybrid",
        posted_at=datetime.now(timezone.utc) - timedelta(hours=2),
        apply_url="https://boards.greenhouse.io/example/jobs/123",
        description=(
            "2+ years. Python FastAPI REST APIs PostgreSQL React TypeScript "
            "OAuth 2.0 multi-tenant SaaS RAG embeddings vector search "
            "Azure Playwright"
        ),
        salary_min_inr=2_000_000,
        salary_max_inr=3_500_000,
    )
    data.update(overrides)
    return JobCreate(**data)


def test_strong_match_and_greenhouse_detection():
    analysis = JobAnalysisService().analyze(make_job())
    assert analysis.classification in {"STRONG_MATCH", "REVIEW"}
    assert analysis.ats_type == "greenhouse"
    assert analysis.freshness == "preferred"
    assert analysis.resume_key in {
        "product_engineering",
        "applied_ai",
    }


def test_old_job_is_hard_skip():
    analysis = JobAnalysisService().analyze(
        make_job(
            posted_at=datetime.now(timezone.utc) - timedelta(hours=60)
        )
    )
    assert analysis.classification == "SKIP"
    assert analysis.hard_failures


def test_only_implemented_ats_enters_automatic_dry_run():
    greenhouse = JobAnalysisService().analyze(make_job())
    lever = JobAnalysisService().analyze(
        make_job(
            apply_url="https://jobs.lever.co/example/123"
        )
    )
    assert greenhouse.auto_apply_eligible is True
    assert lever.ats_type == "lever"
    assert lever.auto_apply_eligible is False
    assert "unsupported_or_unverified_ats" in lever.blockers
