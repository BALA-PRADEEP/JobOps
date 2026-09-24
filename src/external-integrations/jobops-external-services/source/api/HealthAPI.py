from fastapi import APIRouter

from source.Utils.Config import settings
from source.externalService.ats.ATSAdapterRegistry import ATSAdapterRegistry

HEALTH_API = APIRouter(tags=["health"])


@HEALTH_API.get("/health")
def health():
    return {
        "status": "ok",
        "version": "0.3.0-application-execution",
        "auto_submit": settings.auto_submit,
        "dry_run_ats": sorted(ATSAdapterRegistry.supported()),
    }
