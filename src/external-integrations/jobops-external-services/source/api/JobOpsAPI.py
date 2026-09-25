from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from source.Utils.Config import settings
from source.api.HealthAPI import HEALTH_API
from source.api.JobsAPI import JOBS_API

app = FastAPI(
    title="JobOps External Services",
    version="0.4.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(HEALTH_API, prefix="/v1")
app.include_router(JOBS_API, prefix="/v1")
