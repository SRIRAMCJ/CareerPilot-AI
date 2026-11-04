import ipaddress
import re
from pathlib import Path
from urllib.parse import urlparse

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field

from app.core.applications_database import get_application
from app.core.audit_database import record_event
from app.core.config import get_settings
from app.core.database import read_profile
from app.core.jobs_database import get_job
from app.core.resume_database import get_resume_record, list_resume_records
from app.core.submission_database import claim_submission_attempt, finish_submission_attempt, get_submission_attempt

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
    if host == "localhost" or host.endswith(".localhost"):
        raise HTTPException(status_code=400, detail="Local network destinations are not allowed.")
    try:
        address = ipaddress.ip_address(host)
        if not address.is_global:
            raise HTTPException(status_code=400, detail="Private network destinations are not allowed.")
    except ValueError:
        pass
    return value


async def _browser():
    global _CONTEXT, _PLAYWRIGHT
    settings = get_settings()
    if not settings.browser_automation_enabled:
        raise HTTPException(status_code=503, detail="Set BROWSER_AUTOMATION_ENABLED=true to enable browser assistance.")
    try:
        from playwright.async_api import async_playwright
    except ImportError as error:
        raise HTTPException(
            status_code=503,
            detail="Install optional browser support: pip install -e '.[browser]' and playwright install chromium.",
        ) from error
    if _CONTEXT is None:
        profile_dir = Path(settings.browser_profile_dir) if settings.browser_profile_dir else (
            Path.home() / ".careerpilot" / "browser-profile"
        )
        profile_dir.mkdir(parents=True, exist_ok=True)
        _PLAYWRIGHT = await async_playwright().start()
        _CONTEXT = await _PLAYWRIGHT.chromium.launch_persistent_context(
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
    sensitive = (
        "password", "captcha", "otp", "ssn", "aadhaar", "pan", "visa",
        "sponsorship", "salary", "gender", "disability", "ethnicity",
        "veteran", "legal", "consent",
    )
    if any(term in key for term in sensitive):
        return None
    if "email" in key or "e-mail" in key:
        return profile.get("email")
    if any(term in key for term in ("phone", "mobile", "telephone")):
        return profile.get("phone")
    if any(term in key for term in ("first_name", "first name", "given_name", "given name")):
        return (profile.get("full_name") or "").split(" ", 1)[0]
    if any(term in key for term in ("last_name", "last name", "family_name", "family name")):
        return (profile.get("full_name") or "").partition(" ")[2]
    if any(term in key for term in ("full name", "fullname", "your name", "candidate name")):
        return profile.get("full_name")
    if key.strip() in {"name", "yourname", "applicant_name"}:
        return profile.get("full_name")
    if any(term in key for term in ("location", "city", "current address")):
        return profile.get("location")
    if any(term in key for term in ("headline", "professional title")):
        return profile.get("headline") or profile.get("current_role")
    if any(term in key for term in ("summary", "about", "profile")):
        return profile.get("professional_summary")
    return None


async def _fill_visible_fields(page, profile: dict) -> tuple[list[str], list[str]]:
    filled: list[str] = []
    skipped: list[str] = []
    fields = page.locator("input:not([type=hidden]):not([type=submit]):not([type=button]), textarea")
    count = await fields.count()
    for index in range(min(count, 100)):
        field = fields.nth(index)
        try:
            if not await field.is_visible() or await field.is_disabled() or not await field.is_editable():
                continue
            kind = (await field.get_attribute("type") or "text").casefold()
            if kind in {"checkbox", "radio", "file", "password", "submit", "button"}:
                continue
            descriptor = " ".join(filter(None, [
                await field.get_attribute("name"), await field.get_attribute("id"),
                await field.get_attribute("placeholder"), await field.get_attribute("aria-label"),
                await field.get_attribute("autocomplete"),
            ]))
            value = _field_value(descriptor, profile)
            if value:
                await field.fill(str(value))
                filled.append(descriptor[:100] or f"field_{index}")
            else:
                skipped.append(descriptor[:100] or f"field_{index}")
        except Exception:
            skipped.append(f"field_{index}")
    return filled, skipped


async def _attach_selected_resume(page, resume_id: int | None) -> dict:
    records = list_resume_records()
    selected = get_resume_record(resume_id) if resume_id is not None else (
        get_resume_record(records[0]["id"]) if records else None
    )
    if selected is None:
        return {"status": "not_attached", "reason": "No saved resume is available."}
    path = Path(selected["stored_path"]).expanduser()
    if path.suffix.casefold() not in {".pdf", ".docx"} or not path.is_file():
        return {"status": "not_attached", "resume_id": selected["id"],
                "reason": "The selected saved resume file is unavailable or has an unsupported type."}
    inputs = page.locator('input[type="file"]')
    for index in range(min(await inputs.count(), 10)):
        field = inputs.nth(index)
        descriptor = " ".join(filter(None, [
            await field.get_attribute("name"), await field.get_attribute("id"),
            await field.get_attribute("accept"), await field.get_attribute("aria-label"),
        ])).casefold()
        if "resume" not in descriptor and "cv" not in descriptor and "curriculum" not in descriptor:
            continue
        await field.set_input_files(str(path))
        return {"status": "attached_for_review", "resume_id": selected["id"],
                "filename": selected["filename"], "reason": "Attached to a clearly labelled resume/CV input. Verify it in the employer form."}
    return {"status": "not_attached", "resume_id": selected["id"],
            "filename": selected["filename"],
            "reason": "No clearly labelled resume/CV upload field was found; no file was attached."}


@router.post("/applications/{application_id}/prepare")
async def prepare_application_form(
    application_id: int, resume_id: int | None = Query(default=None, gt=0)
) -> dict:
    application = get_application(application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application tracker not found.")
    job = get_job(application["job_id"])
    url = _safe_job_url(job.get("url") if job else None)
    profile = _profile_payload()
    context = await _browser()
    page = await context.new_page()
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=45000)
    except Exception as error:
        await page.close()
        raise HTTPException(status_code=502, detail="Could not open the job application page in the local browser.") from error
    filled, skipped = await _fill_visible_fields(page, profile)
    resume_attachment = await _attach_selected_resume(page, resume_id)
    _PAGES[application_id] = page
    record_event("application.form_prepared", "application", application_id,
                 {"fields_filled": len(filled), "fields_skipped": len(skipped),
                  "resume_attachment": resume_attachment["status"],
                  "resume_id": resume_attachment.get("resume_id")})
    return {
        "status": "form_prepared", "application_id": application_id,
        "page_title": await page.title(), "page_url": page.url,
        "filled_fields": filled, "skipped_fields": skipped,
        "resume_attachment": resume_attachment, "review_required": True,
        "message": "Review every field and the attached resume in the visible browser. Complete declarations yourself.",
    }


@router.get("/applications/{application_id}/submission")
def submission_status(application_id: int) -> dict:
    if not get_application(application_id):
        raise HTTPException(status_code=404, detail="Application tracker not found.")
    attempt = get_submission_attempt(application_id)
    return {"application_id": application_id, "attempt": attempt}


@router.post("/applications/{application_id}/submit")
async def submit_application(application_id: int, request: SubmissionConfirmation) -> dict:
    settings = get_settings()
    if not settings.application_submission_enabled:
        raise HTTPException(status_code=403, detail="Application submission is disabled. Set APPLICATION_SUBMISSION_ENABLED=true after reviewing the safety guidance.")
    if request.confirmation != "SUBMIT APPLICATION":
        raise HTTPException(status_code=400, detail="Type SUBMIT APPLICATION to confirm this external action.")
    application = get_application(application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application tracker not found.")
    page = _PAGES.get(application_id)
    if page is None or await page.is_closed():
        raise HTTPException(status_code=409, detail="Prepare the application form in the visible browser first.")
    try:
        button = page.get_by_role(
            "button", name=re.compile(r"^(submit application|send application|submit)$", re.I)
        ).last
        if await button.count() == 0 or not await button.is_visible() or not await button.is_enabled():
            raise HTTPException(status_code=409, detail="No unambiguous enabled submit button was found.")
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=502, detail="Could not inspect the application submit control.") from error

    attempt = claim_submission_attempt(application_id, page.url)
    if attempt is None:
        existing = get_submission_attempt(application_id)
        raise HTTPException(
            status_code=409,
            detail={
                "message": "A submission attempt is already recorded. Duplicate clicks are blocked.",
                "attempt": existing,
                "next_step": "Check the employer website and reconcile the result manually before taking any further action.",
            },
        )
    record_event("application.submission_attempt_started", "application", application_id,
                 {"attempt_id": attempt["id"], "page_url": page.url})
    try:
        await button.click(timeout=10000)
        finish_submission_attempt(attempt["id"], "clicked")
        record_event("application.submission_clicked", "application", application_id,
                     {"attempt_id": attempt["id"], "action": "explicit_user_confirmation", "page_url": page.url})
        return {
            "status": "submit_action_clicked", "attempt": get_submission_attempt(application_id),
            "message": "The submit control was clicked. Verify the employer website's confirmation; CareerPilot does not mark this as applied automatically.",
            "automatic_success_claimed": False,
        }
    except Exception as error:
        finish_submission_attempt(attempt["id"], "outcome_unknown")
        record_event("application.submission_outcome_unknown", "application", application_id,
                     {"attempt_id": attempt["id"], "page_url": page.url})
        raise HTTPException(
            status_code=502,
            detail="The browser did not confirm whether the submit action completed. The attempt is locked to prevent a duplicate. Check the employer site and reconcile manually.",
        ) from error
