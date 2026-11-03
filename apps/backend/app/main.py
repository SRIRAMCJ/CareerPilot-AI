from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.routers.applications import router as applications_router
from app.routers.audit import router as audit_router
from app.routers.discovery import router as discovery_router
from app.routers.interviews import router as interviews_router
from app.routers.jobs import router as jobs_router
from app.routers.materials import router as materials_router
from app.routers.profile import router as profile_router
from app.routers.resumes import router as resumes_router

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Local-first personal career workflow API.",
)

app.include_router(profile_router)
app.include_router(jobs_router)
app.include_router(applications_router)
app.include_router(audit_router)
app.include_router(discovery_router)
app.include_router(resumes_router)
app.include_router(materials_router)
app.include_router(interviews_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.get("/api/v1/health", tags=["system"])
def health_check() -> dict[str, str]:
    """Liveness endpoint; does not expose environment variables or secrets."""
    return {"status": "ok", "service": "careerpilot-api"}


@app.get("/api/v1/system", tags=["system"])
def system_status() -> dict[str, object]:
    """Expose non-sensitive feature flags for the local dashboard."""
    return {
        "application": settings.app_name,
        "version": app.version,
        "environment": settings.app_env,
        "ai_provider": settings.ai_provider,
        "integrations": {
            "gmail": settings.gmail_enabled,
            "google_calendar": settings.google_calendar_enabled,
            "browser_automation": settings.browser_automation_enabled,
            "application_submission": settings.application_submission_enabled,
        },
    }


@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    return {"message": "CareerPilot AI API", "docs": "/docs"}
