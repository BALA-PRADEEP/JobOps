from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from source.Utils.Errors import (
    ConflictError,
    JobOpsError,
    NotFoundError,
    UnsupportedATSError,
)
from source.dal.db_session import get_db
from source.schemas.ApplicationSchemas import ApplicationPackage, DryRunResult
from source.schemas.JobSchemas import (
    AnalyzeResponse,
    DiscoveredJobCreate,
    JobCreate,
    JobRecord,
    JobResolutionRequest,
)
from source.service.ApplicationExecutionService import ApplicationExecutionService
from source.service.ApplicationPreparationService import (
    ApplicationPreparationService,
)
from source.service.JobIngestionService import JobIngestionService
from source.service.JobIntakeService import JobIntakeService
from source.service.JobResolutionService import JobResolutionService

JOBS_API = APIRouter(prefix="/jobs", tags=["jobs"])


@JOBS_API.post("/intake", response_model=JobRecord)
def intake_discovered_job(
    payload: DiscoveredJobCreate,
    db: Session = Depends(get_db),
):
    try:
        return JobIntakeService(db).intake(payload)
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except JobOpsError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@JOBS_API.post("/analyze", response_model=AnalyzeResponse)
def analyze_job(payload: JobCreate, db: Session = Depends(get_db)):
    try:
        return JobIngestionService(db).analyze_and_store(payload)
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except JobOpsError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@JOBS_API.post("/{job_id}/resolve", response_model=AnalyzeResponse)
def resolve_job_application_url(
    job_id: int,
    payload: JobResolutionRequest,
    db: Session = Depends(get_db),
):
    try:
        return JobResolutionService(db).resolve_and_analyze(job_id, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except JobOpsError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@JOBS_API.get("", response_model=list[JobRecord])
def list_jobs(db: Session = Depends(get_db)):
    return JobIngestionService(db).list_jobs()


@JOBS_API.get(
    "/{job_id}/application-package",
    response_model=ApplicationPackage,
)
def build_application_package(
    job_id: int,
    db: Session = Depends(get_db),
):
    try:
        return ApplicationPreparationService(db).build(job_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (ValueError, JobOpsError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@JOBS_API.post(
    "/{job_id}/dry-run",
    response_model=DryRunResult,
)
def run_application_dry_run(
    job_id: int,
    db: Session = Depends(get_db),
):
    try:
        return ApplicationExecutionService(db).run_dry_run(job_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except UnsupportedATSError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except (ValueError, JobOpsError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
