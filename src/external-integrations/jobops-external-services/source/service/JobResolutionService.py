import json
from sqlalchemy.orm import Session

from source.Utils.ATSDetector import detect_ats
from source.Utils.ApplicationState import ApplicationState
from source.Utils.Errors import NotFoundError
from source.dal.ApplicationRepository import ApplicationEventRepository, ApplicationRepository
from source.dal.JobModels import JobScore
from source.dal.JobRepository import JobRepository, JobScoreRepository
from source.schemas.JobSchemas import AnalyzeResponse, JobAnalysis, JobCreate, JobRecord, JobResolutionRequest
from source.service.JobAnalysisService import JobAnalysisService


class JobResolutionService:
    def __init__(self, session: Session):
        self.session = session
        self.jobs = JobRepository(session)
        self.scores = JobScoreRepository(session)
        self.applications = ApplicationRepository(session)
        self.events = ApplicationEventRepository(session)
        self.analysis_service = JobAnalysisService()

    def resolve_and_analyze(self, job_id: int, payload: JobResolutionRequest) -> AnalyzeResponse:
        job = self.jobs.get(job_id)
        if job is None:
            raise NotFoundError("Job not found")

        application_url = str(payload.application_url)
        job.application_url = application_url
        job.apply_url = application_url
        job.canonical_job_url = (
            str(payload.canonical_job_url)
            if payload.canonical_job_url is not None
            else job.discovery_url
        )
        job.resolver_status = "RESOLVED"
        job.ats_type = detect_ats(application_url)

        analysis_input = JobCreate(
            source=job.source,
            source_job_id=job.source_job_id,
            company=job.company,
            title=job.title,
            location=job.location,
            work_mode=job.work_mode,
            posted_at=job.posted_at,
            apply_url=application_url,
            description=job.description,
            salary_min_inr=job.salary_min_inr,
            salary_max_inr=job.salary_max_inr,
        )
        analysis: JobAnalysis = self.analysis_service.analyze(analysis_input)

        existing_score = self.scores.get_latest_for_job(job.id)
        if existing_score is None:
            self.scores.add(
                JobScore(
                    job_id=job.id,
                    total=analysis.total_score,
                    classification=analysis.classification,
                    details_json=analysis.model_dump_json(),
                    resume_key=analysis.resume_key,
                )
            )

        application = self.applications.get_by_job_id(job.id)
        if application is None:
            raise NotFoundError("Application not found")
        application.resume_key = analysis.resume_key
        application.blockers_json = json.dumps(analysis.blockers)

        if application.state == ApplicationState.DISCOVERED.value:
            self.applications.transition(application, ApplicationState.ANALYZED)
            self.events.append(application.id, "JOB_ANALYZED", analysis.model_dump_json())
            target = (
                ApplicationState.SKIPPED
                if analysis.classification == "SKIP"
                else ApplicationState.SHORTLISTED
            )
            self.applications.transition(application, target)
            self.events.append(application.id, f"APPLICATION_{target.value}", analysis.model_dump_json())

        self.events.append(
            application.id,
            "JOB_APPLICATION_URL_RESOLVED",
            json.dumps({
                "discovery_url": job.discovery_url,
                "canonical_job_url": job.canonical_job_url,
                "application_url": job.application_url,
                "ats_type": job.ats_type,
            }),
        )
        self.session.commit()
        self.session.refresh(job)
        return AnalyzeResponse(job=JobRecord.model_validate(job), analysis=analysis)
