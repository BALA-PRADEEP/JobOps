import json
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from source.Utils.ApplicationState import ApplicationState
from source.Utils.Errors import ConflictError
from source.dal.ApplicationModels import Application
from source.dal.ApplicationRepository import ApplicationEventRepository, ApplicationRepository
from source.dal.JobModels import Job
from source.dal.JobRepository import JobRepository
from source.schemas.JobSchemas import DiscoveredJobCreate, JobRecord


class JobIntakeService:
    """Accept jobs from scheduled discovery without assuming the discovery URL is the apply form."""

    def __init__(self, session: Session):
        self.session = session
        self.jobs = JobRepository(session)
        self.applications = ApplicationRepository(session)
        self.events = ApplicationEventRepository(session)

    def intake(self, payload: DiscoveredJobCreate) -> JobRecord:
        existing = self.jobs.get_by_source_identity(payload.source, payload.source_job_id)
        if existing is not None:
            return JobRecord.model_validate(existing)

        discovery_url = str(payload.discovery_url)
        job = Job(
            source=payload.source,
            source_job_id=payload.source_job_id,
            company=payload.company,
            title=payload.title,
            location=payload.location,
            work_mode=payload.work_mode,
            posted_at=payload.posted_at,
            apply_url=discovery_url,
            discovery_url=discovery_url,
            canonical_job_url=None,
            application_url=None,
            resolver_status="PENDING",
            description=payload.description,
            salary_min_inr=payload.salary_min_inr,
            salary_max_inr=payload.salary_max_inr,
            ats_type="pending",
        )
        self.jobs.add(job)
        try:
            self.session.flush()
        except IntegrityError as exc:
            self.session.rollback()
            raise ConflictError("Duplicate job") from exc

        application = Application(
            job_id=job.id,
            state=ApplicationState.DISCOVERED.value,
            blockers_json=json.dumps(["application_url_unresolved"]),
        )
        self.applications.add(application)
        self.session.flush()
        self.events.append(application.id, "JOB_DISCOVERED", payload.model_dump_json())
        self.session.commit()
        self.session.refresh(job)
        return JobRecord.model_validate(job)
