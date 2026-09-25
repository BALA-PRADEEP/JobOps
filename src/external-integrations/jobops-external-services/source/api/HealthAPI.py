from fastapi import APIRouter

from source.Utils.Config import settings
from source.Utils.Constants import SUPPORTED_DRY_RUN_ATS

HEALTH_API = APIRouter(tags=["health"])


@HEALTH_API.get("/health")
def health():
    return {
        "status": "ok",
        "version": "0.4.0-free-runtime",
        "auto_submit": settings.auto_submit,
        "execution_mode": settings.execution_mode,
        "dry_run_ats": sorted(SUPPORTED_DRY_RUN_ATS),
    }
