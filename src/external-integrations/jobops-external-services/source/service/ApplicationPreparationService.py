import json
from sqlalchemy.orm import Session

from source.Utils.ApplicationState import ApplicationState
from source.Utils.Errors import NotFoundError
from source.dal.ApplicationRepository import ApplicationEventRepository, ApplicationRepository
from source.dal.JobRepository import JobRepository, JobScoreRepository
from source.schemas.ApplicationSchemas import ApplicationPackage
from source.schemas.JobSchemas import JobAnalysis
from source.service.CandidateProfileService import CandidateProfileService
from source.service.ResumeSelectionService import ResumeSelectionService


class ApplicationPreparationService:
    def __init__(self, session: Session):
        self.session = session
        self.jobs = JobRepository(session)
        self.scores = JobScoreRepository(session)
        self.applications = ApplicationRepository(session)
        self.events = ApplicationEventRepository(session)

    def build(self, job_id: int) -> ApplicationPackage:
        job = self.jobs.get(job_id)
        if job is None:
            raise NotFoundError("Job not found")
        score = self.scores.get_latest_for_job(job_id)
        if score is None:
            raise NotFoundError("Analysis not found")
        application = self.applications.get_by_job_id(job_id)
        if application is None:
            raise NotFoundError("Application not found")
        if application.state == ApplicationState.SKIPPED.value:
            raise ValueError("Skipped jobs cannot build an application package")

        analysis = JobAnalysis.model_validate_json(score.details_json)
        profile = CandidateProfileService.get_profile()
        identity = profile["identity"]
        protected = profile["protected_facts"]
        missing = [key for key, value in protected.items() if value is None]

        known_fields = {
            "name": identity["name"],
            "email": identity["email"],
            "phone": identity["phone"],
            "linkedin": identity["linkedin"],
            "portfolio": identity["portfolio"],
            "current_location": identity["current_location"],
        }
        generated_drafts = {
            "professional_summary": (
                "Software/product engineer with 2+ years of startup experience across Python/FastAPI backends, "
                "React/TypeScript workflows, databases, external integrations, and applied AI."
            )
        }

        target_state = (
            ApplicationState.READY_FOR_REVIEW
            if analysis.auto_apply_eligible
            else ApplicationState.NEEDS_INPUT
        )

        if application.state == ApplicationState.SHORTLISTED.value:
            self.applications.transition(application, ApplicationState.PREPARING)
        if application.state == ApplicationState.PREPARING.value:
            self.applications.transition(application, target_state)
        elif application.state not in {
            ApplicationState.READY_FOR_REVIEW.value,
            ApplicationState.NEEDS_INPUT.value,
        }:
            raise ValueError(f"Application cannot be prepared from state {application.state}")

        state = ApplicationState(application.state)
        application.blockers_json = json.dumps(missing)

        package = ApplicationPackage(
            job_id=job.id,
            application_id=application.id,
            state=state.value,
            resume_key=analysis.resume_key,
            resume_path=str(ResumeSelectionService.get_path(analysis.resume_key)),
            known_fields=known_fields,
            missing_protected_fields=missing,
            generated_drafts=generated_drafts,
            ats_type=analysis.ats_type,
            apply_url=job.apply_url,
            submit_allowed=False,
        )
        self.events.append(
            application.id,
            "APPLICATION_PACKAGE_BUILT",
            package.model_dump_json(),
        )
        self.session.commit()
        return package
