import hmac

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.routers.applications import router as applications_router
from app.routers.audit import router as audit_router
from app.routers.browser_automation import router as browser_automation_router
from app.routers.discovery import router as discovery_router
from app.routers.gmail import router as gmail_router
from app.routers.integrations import router as integrations_router
from app.routers.interviews import router as interviews_router
from app.routers.jobs import router as jobs_router
from app.routers.materials import router as materials_router
from app.routers.profile import router as profile_router
from app.routers.resumes import router as resumes_router

settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.2.0", description="Local-first personal career workflow API.")

for api_router in (
    profile_router, jobs_router, applications_router, audit_router, discovery_router,
    resumes_router, materials_router, interviews_router, integrations_router,
    browser_automation_router, gmail_router,
):
    app.include_router(api_router)


@app.middleware("http")
async def require_server_proxy_token(request: Request, call_next):
    """Protect personal data APIs from direct public access in cloud deployments."""
    if request.url.path == "/api/v1/health" or not request.url.path.startswith("/api/v1/"):
        return await call_next(request)
    expected = settings.careerpilot_proxy_token
    if settings.app_env == "production" and not expected:
        return JSONResponse({"detail": "API proxy authentication is not configured."}, status_code=503,
                            headers={"Cache-Control": "no-store"})
    supplied = request.headers.get("x-careerpilot-proxy-token", "")
    if expected and not hmac.compare_digest(supplied, expected):
        return JSONResponse({"detail": "Unauthorized API proxy request."}, status_code=401,
                            headers={"Cache-Control": "no-store"})
    return await call_next(request)


app.add_middleware(
    CORSMiddleware, allow_origins=[settings.frontend_origin], allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.get("/api/v1/health", tags=["system"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "careerpilot-api"}


@app.get("/api/v1/system", tags=["system"])
def system_status() -> dict[str, object]:
    return {
        "application": settings.app_name, "version": app.version,
        "environment": settings.app_env, "ai_provider": settings.ai_provider,
        "integrations": {
            "gmail": settings.gmail_enabled,
            "gmail_configured": bool(settings.gmail_client_id and settings.gmail_client_secret),
            "google_calendar": settings.google_calendar_enabled,
            "browser_automation": settings.browser_automation_enabled,
            "application_submission": settings.application_submission_enabled,
        },
    }


@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    return {"message": "CareerPilot AI API", "docs": "/docs"}
