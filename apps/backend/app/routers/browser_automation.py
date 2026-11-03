import ipaddress
import re
from pathlib import Path
from urllib.parse import urlparse

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from app.core.applications_database import get_application
from app.core.audit_database import record_event
from app.core.config import get_settings
from app.core.database import read_profile
from app.core.jobs_database import get_job

router = APIRouter(prefix="/api/v1/browser", tags=["browser-assisted applications"])
_PAGES: dict[int, object] = {}
_CONTEXT = None
_PLAYWRIGHT = None


class SubmissionConfirmation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    confirmation: str = Field(min_length=1, max_length=40)


def _safe_job_url(value: str | None) -> str:
    if not value:
        raise HTTPException(status_code=400, detail="This tracked job has no application URL.")
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.hostname:
        raise HTTPException(status_code=400, detail="Only HTTPS job application URLs are allowed.")
    host = parsed.hostname.lower()
    if host in {"localhost", "localhost.localdomain"} or host.endswith(".localhost"):
        raise HTTPException(status_code=400, detail="Local network destinations are not allowed.")
    try:
        address = ipaddress.ip_address(host)
        if not address.is_global:
            raise HTTPException(status_code=400, detail="Private network destinations are not allowed.")
    except ValueError:
        pass
    return value


def _browser():
    global _CONTEXT, _PLAYWRIGHT
    settings = get_settings()
    if not settings.browser_automation_enabled:
        raise HTTPException(status_code=503, detail="Set BROWSER_AUTOMATION_ENABLED=true to enable browser assistance.")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as error:
        raise HTTPException(status_code=503, detail="Install optional browser support: pip install -e '.[browser]' and playwright install chromium.") from error
    if _CONTEXT is None:
        profile_dir = Path(settings.browser_profile_dir) if settings.browser_profile_dir else (
            Path.home() / ".careerpilot" / "browser-profile"
        )
        profile_dir.mkdir(parents=True, exist_ok=True)
        _PLAYWRIGHT = sync_playwright().start()
        _CONTEXT = _PLAYWRIGHT.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir), headless=False
        )
    return _CONTEXT


def _profile_payload() -> dict:
    saved = read_profile()
    if not saved or not saved.get("profile"):
        raise HTTPException(status_code=409, detail="Complete and verify your candidate profile first.")
    return saved["profile"]


def _field_value(descriptor: str, profile: dict) -> str | None:
    key = descriptor.casefold()
    if any(term in key for term in ("password", "captcha", "otp", "ssn", "aadhaar", "pan", "visa", "sponsorship", "salary", "gender", "disability", "ethnicity", "veteran", "legal", "consent")):
        return None
    if any(term in key for term in ("email", "e-mail")):
        return profile.get("email")
    if any(term in key for term in ("phone", "mobile", "telephone")):
        return profile.get("phone")
    if any(term in key for term in ("full name", "fullname", "your name", "candidate name", "name")):
        return profile.get("full_name")
    if any(term in key for term in ("location", "city", "current address")):
        return profile.get("location")
    if any(term in key for term in ("headline", "professional title")):
        return profile.get("headline") or profile.get("current_role")
    if any(term in key for term in ("summary", "about", "profile")):
        return profile.get("professional_summary")
    return None


def _fill_visible_fields(page, profile: dict) -> tuple[list[str], list[str]]:
    filled: list[str] = []
    skipped: list[str] = []
    fields = page.locator("input:not([type=hidden]):not([type=submit]):not([type=button]), textarea")
    for index in range(min(fields.count(), 100)):
        field = fields.nth(index)
        try:
            if not field.is_visible() or field.is_disabled() or field.is_readonly():
                continue
            kind = (field.get_attribute("type") or "text").casefold()
            if kind in {"checkbox", "radio", "file", "password", "submit", "button"}:
                continue
            descriptor = " ".join(filter(None, [
                field.get_attribute("name"), field.get_attribute("id"),
                field.get_attribute("placeholder"), field.get_attribute("aria-label"),
                field.get_attribute("autocomplete"),
            ]))
            value = _field_value(descriptor, profile)
            if value:
                field.fill(str(value))
                filled.append(descriptor[:100] or f"field_{index}")
            else:
                skipped.append(descriptor[:100] or f"field_{index}")
        except Exception:
            skipped.append(f"field_{index}")
    return filled, skipped


@router.post("/applications/{application_id}/prepare")
def prepare_application_form(application_id: int) -> dict:
    application = get_application(application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application tracker not found.")
    job = get_job(application["job_id"])
    url = _safe_job_url(job.get("url") if job else None)
    profile = _profile_payload()
    context = _browser()
    page = context.new_page()
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=45000)
    except Exception as error:
        page.close()
        raise HTTPException(status_code=502, detail="Could not open the job application page in the local browser.") from error
    filled, skipped = _fill_visible_fields(page, profile)
    _PAGES[application_id] = page
    record_event("application.form_prepared", "application", application_id,
                 {"fields_filled": len(filled), "fields_skipped": len(skipped)})
    return {
        "status": "form_prepared",
        "application_id": application_id,
        "page_title": page.title(),
        "page_url": page.url,
        "filled_fields": filled,
        "skipped_fields": skipped,
        "review_required": True,
        "message": "Review every field in the visible browser. Attach the correct resume and complete any declarations yourself.",
    }


@router.post("/applications/{application_id}/submit")
def submit_application(application_id: int, request: SubmissionConfirmation) -> dict:
    settings = get_settings()
    if not settings.application_submission_enabled:
        raise HTTPException(status_code=403, detail="Application submission is disabled. Set APPLICATION_SUBMISSION_ENABLED=true after reviewing the safety guidance.")
    if request.confirmation != "SUBMIT APPLICATION":
        raise HTTPException(status_code=400, detail="Type SUBMIT APPLICATION to confirm this external action.")
    page = _PAGES.get(application_id)
    if page is None or page.is_closed():
        raise HTTPException(status_code=409, detail="Prepare the application form in the visible browser first.")
    try:
        button = page.get_by_role(
            "button", name=re.compile(r"^(submit application|send application|submit)$", re.I)
        ).last
        if button.count() == 0 or not button.is_visible() or not button.is_enabled():
            raise HTTPException(status_code=409, detail="No unambiguous enabled submit button was found.")
        button.click(timeout=10000)
        record_event("application.submission_clicked", "application", application_id,
                     {"action": "explicit_user_confirmation"})
        return {
            "status": "submit_action_clicked",
            "message": "The submit control was clicked. Verify the website's confirmation and update the application status manually.",
            "automatic_success_claimed": False,
        }
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=502, detail="The application submit control could not be activated.") from error
