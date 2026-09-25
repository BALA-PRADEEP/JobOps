import json
from sqlalchemy.orm import Session

from source.Utils.ApplicationState import ApplicationState
from source.Utils.Errors import NotFoundError
from source.dal.ApplicationRepository import (
    ApplicationEventRepository,
    ApplicationRepository,
    BrowserRunRepository,
)
from source.dal.JobRepository import JobRepository, JobScoreRepository
from source.externalService.ats.ATSAdapterRegistry import ATSAdapterRegistry
from source.schemas.ApplicationSchemas import DryRunResult
from source.schemas.JobSchemas import JobAnalysis
from source.service.ApplicationPreparationService import ApplicationPreparationService
from source.service.CandidateProfileService import CandidateProfileService
from source.service.ResumeSelectionService import ResumeSelectionService


class ApplicationExecutionService:
    def __init__(self, session: Session):
        self.session = session
        self.jobs = JobRepository(session)
        self.scores = JobScoreRepository(session)
        self.applications = ApplicationRepository(session)
        self.events = ApplicationEventRepository(session)
        self.browser_runs = BrowserRunRepository(session)
        self.preparation = ApplicationPreparationService(session)

    def _resolve_execution_context(self, job_id: int):
        job = self.jobs.get(job_id)
        if job is None:
            raise NotFoundError("Job not found")
        application = self.applications.get_by_job_id(job_id)
        if application is None:
            raise NotFoundError("Application not found")

        if application.state in {
            ApplicationState.SHORTLISTED.value,
            ApplicationState.PREPARING.value,
        }:
            package = self.preparation.build(job_id)
            application = self.applications.get(package.application_id)
            assert application is not None
            return job, application, package.ats_type, package.resume_path

        score = self.scores.get_latest_for_job(job_id)
        if score is None:
            raise NotFoundError("Analysis not found")
        analysis = JobAnalysis.model_validate_json(score.details_json)
        return (
            job,
            application,
            analysis.ats_type,
            str(ResumeSelectionService.get_path(analysis.resume_key)),
        )

    def run_dry_run(self, job_id: int, artifact_dir: str | None = None) -> DryRunResult:
        job, application, ats_type, resume_path = self._resolve_execution_context(job_id)
        profile = CandidateProfileService.get_profile()
        adapter = ATSAdapterRegistry.create(ats_type, profile, resume_path)

        self.events.append(
            application.id,
            "ATS_DRY_RUN_STARTED",
            json.dumps({"ats_type": ats_type, "apply_url": job.apply_url}),
        )
        result = adapter.run_dry_run(job.apply_url, artifact_dir=artifact_dir)

        self.browser_runs.create(
            application_id=application.id,
            ats_type=ats_type,
            status=result.status,
            artifact_json=result.model_dump_json(),
            submit_clicked=result.submit_clicked,
        )
        self.events.append(application.id, "ATS_DRY_RUN_COMPLETED", result.model_dump_json())

        if (
            result.status == "NEEDS_INPUT"
            and application.state == ApplicationState.READY_FOR_REVIEW.value
        ):
            self.applications.transition(application, ApplicationState.NEEDS_INPUT)
            self.events.append(
                application.id,
                "APPLICATION_NEEDS_INPUT",
                json.dumps({
                    "protected_fields": result.protected_fields,
                    "missing_fields": result.missing_fields,
                }),
            )

        self.session.commit()
        return result
