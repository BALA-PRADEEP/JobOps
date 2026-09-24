import json
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from source.Utils.ApplicationState import ApplicationState
from source.Utils.Errors import ConflictError
from source.dal.ApplicationModels import Application
from source.dal.ApplicationRepository import ApplicationEventRepository, ApplicationRepository
from source.dal.JobModels import Job, JobScore
from source.dal.JobRepository import JobRepository, JobScoreRepository
from source.schemas.JobSchemas import AnalyzeResponse, JobCreate, JobRecord
from source.service.JobAnalysisService import JobAnalysisService


class JobIngestionService:
    def __init__(self, session: Session):
        self.session = session
        self.jobs = JobRepository(session)
        self.scores = JobScoreRepository(session)
        self.applications = ApplicationRepository(session)
        self.events = ApplicationEventRepository(session)
        self.analysis = JobAnalysisService()

    def analyze_and_store(self, payload: JobCreate) -> AnalyzeResponse:
        existing = self.jobs.get_by_source_identity(payload.source, payload.source_job_id)
        if existing is not None:
            latest_score = self.scores.get_latest_for_job(existing.id)
            if latest_score is None:
                raise ConflictError("Job exists without analysis")
            from source.schemas.JobSchemas import JobAnalysis
            analysis = JobAnalysis.model_validate_json(latest_score.details_json)
            return AnalyzeResponse(job=JobRecord.model_validate(existing), analysis=analysis)

        analysis = self.analysis.analyze(payload)
        job = Job(
            source=payload.source,
            source_job_id=payload.source_job_id,
            company=payload.company,
            title=payload.title,
            location=payload.location,
            work_mode=payload.work_mode,
            posted_at=payload.posted_at,
            apply_url=str(payload.apply_url),
            description=payload.description,
            salary_min_inr=payload.salary_min_inr,
            salary_max_inr=payload.salary_max_inr,
            ats_type=analysis.ats_type,
        )
        self.jobs.add(job)
        try:
            self.session.flush()
        except IntegrityError as exc:
            self.session.rollback()
            raise ConflictError("Duplicate job") from exc

        score = JobScore(
            job_id=job.id,
            total=analysis.total_score,
            classification=analysis.classification,
            details_json=analysis.model_dump_json(),
            resume_key=analysis.resume_key,
        )
        self.scores.add(score)

        application = Application(
            job_id=job.id,
            state=ApplicationState.DISCOVERED.value,
            resume_key=analysis.resume_key,
            blockers_json=json.dumps(analysis.blockers),
        )
        self.applications.add(application)
        self.session.flush()
        self.events.append(application.id, "JOB_DISCOVERED", payload.model_dump_json())
        self.applications.transition(application, ApplicationState.ANALYZED)
        self.events.append(application.id, "JOB_ANALYZED", analysis.model_dump_json())
        target = (
            ApplicationState.SKIPPED
            if analysis.classification == "SKIP"
            else ApplicationState.SHORTLISTED
        )
        self.applications.transition(application, target)
        self.events.append(application.id, f"APPLICATION_{target.value}", analysis.model_dump_json())
        self.session.commit()
        self.session.refresh(job)
        return AnalyzeResponse(job=JobRecord.model_validate(job), analysis=analysis)

    def list_jobs(self, limit: int = 100) -> list[JobRecord]:
        return [JobRecord.model_validate(job) for job in self.jobs.list_recent(limit=limit)]
