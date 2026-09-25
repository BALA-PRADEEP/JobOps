import json
from sqlalchemy.orm import Session

from source.Utils.Errors import NotFoundError, UnsupportedATSError
from source.Utils.Constants import SUPPORTED_DRY_RUN_ATS
from source.dal.ApplicationRepository import (
    ApplicationEventRepository,
    ApplicationRepository,
    ExecutionRequestRepository,
)
from source.dal.JobRepository import JobRepository, JobScoreRepository
from source.schemas.ApplicationSchemas import ExecutionRequestResponse
from source.schemas.JobSchemas import JobAnalysis
from source.service.ApplicationPreparationService import ApplicationPreparationService


class ExecutionRequestService:
    def __init__(self, session: Session):
        self.session = session
        self.jobs = JobRepository(session)
        self.scores = JobScoreRepository(session)
        self.applications = ApplicationRepository(session)
        self.events = ApplicationEventRepository(session)
        self.requests = ExecutionRequestRepository(session)
        self.preparation = ApplicationPreparationService(session)

    def enqueue_dry_run(self, job_id: int) -> ExecutionRequestResponse:
        job = self.jobs.get(job_id)
        if job is None:
            raise NotFoundError("Job not found")

        score = self.scores.get_latest_for_job(job_id)
        if score is None:
            raise NotFoundError("Job has not been analyzed")

        analysis = JobAnalysis.model_validate_json(score.details_json)
        if analysis.ats_type not in SUPPORTED_DRY_RUN_ATS:
            raise UnsupportedATSError(
                f"ATS dry-run adapter not implemented: {analysis.ats_type}"
            )

        application = self.applications.get_by_job_id(job_id)
        if application is None:
            raise NotFoundError("Application not found")

        if application.state in {"SHORTLISTED", "PREPARING"}:
            package = self.preparation.build(job_id)
            application = self.applications.get(package.application_id)
            assert application is not None

        request = self.requests.enqueue(application.id, action="DRY_RUN")
        self.events.append(
            application.id,
            "EXECUTION_REQUEST_QUEUED",
            json.dumps({"request_id": request.id, "action": request.action}),
        )
        self.session.commit()
        self.session.refresh(request)
        return ExecutionRequestResponse.model_validate(request)

    def get_request(self, request_id: int) -> ExecutionRequestResponse:
        request = self.requests.get(request_id)
        if request is None:
            raise NotFoundError("Execution request not found")
        return ExecutionRequestResponse.model_validate(request)
