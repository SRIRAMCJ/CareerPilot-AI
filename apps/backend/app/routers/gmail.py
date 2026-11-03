import base64
from email.mime.text import MIMEText
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.audit_database import record_event
from app.core.config import get_settings

router = APIRouter(prefix="/api/v1/gmail", tags=["Gmail recruiter communication"])
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.send",
]
_OAUTH_STATES: set[str] = set()


class EmailDraft(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    to: list[EmailStr] = Field(min_length=1, max_length=10)
    subject: str = Field(min_length=1, max_length=250)
    body: str = Field(min_length=1, max_length=20000)
    thread_id: str | None = Field(default=None, max_length=200)
    in_reply_to: str | None = Field(default=None, max_length=500)
    references: str | None = Field(default=None, max_length=1000)


def _settings():
    settings = get_settings()
    if not settings.gmail_enabled:
        raise HTTPException(status_code=503, detail="Gmail integration is disabled. Set GMAIL_ENABLED=true.")
    if not settings.gmail_client_id or not settings.gmail_client_secret:
        raise HTTPException(status_code=503, detail="Configure GMAIL_CLIENT_ID and GMAIL_CLIENT_SECRET first.")
    return settings


def _token_path() -> Path:
    settings = get_settings()
    path = Path(settings.gmail_token_path) if settings.gmail_token_path else (
        Path.home() / ".careerpilot" / "gmail-token.json"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _google_modules():
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import Flow
        from googleapiclient.discovery import build
    except ImportError as error:
        raise HTTPException(status_code=503, detail="Install the backend Gmail dependencies.") from error
    return Request, Credentials, Flow, build


def _credentials():
    settings = _settings()
    Request, Credentials, _, _ = _google_modules()
    path = _token_path()
    if not path.exists():
        raise HTTPException(status_code=401, detail="Gmail is not connected. Start OAuth first.")
    credentials = Credentials.from_authorized_user_file(str(path), SCOPES)
    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        path.write_text(credentials.to_json(), encoding="utf-8")
    if not credentials.valid:
        raise HTTPException(status_code=401, detail="Gmail authorization expired. Reconnect Gmail.")
    return credentials


def _service():
    _, _, _, build = _google_modules()
    return build("gmail", "v1", credentials=_credentials(), cache_discovery=False)


@router.get("/status")
def gmail_status() -> dict:
    settings = get_settings()
    configured = bool(settings.gmail_enabled and settings.gmail_client_id and settings.gmail_client_secret)
    connected = False
    if configured and _token_path().exists():
        try:
            _credentials()
            connected = True
        except HTTPException:
            connected = False
    return {"enabled": settings.gmail_enabled, "configured": configured, "connected": connected}


@router.post("/auth/start")
def start_gmail_oauth() -> dict:
    settings = _settings()
    _, _, Flow, _ = _google_modules()
    flow = Flow.from_client_config(
        {"web": {
            "client_id": settings.gmail_client_id,
            "client_secret": settings.gmail_client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [settings.gmail_redirect_uri],
        }},
        scopes=SCOPES,
    )
    flow.redirect_uri = settings.gmail_redirect_uri
    authorization_url, state = flow.authorization_url(
        access_type="offline", include_granted_scopes="true", prompt="consent"
    )
    _OAUTH_STATES.add(state)
    return {"authorization_url": authorization_url, "state": state,
            "redirect_uri": settings.gmail_redirect_uri}


@router.get("/auth/callback")
def finish_gmail_oauth(code: str, state: str) -> dict:
    settings = _settings()
    if state not in _OAUTH_STATES:
        raise HTTPException(status_code=400, detail="OAuth state is invalid or expired. Start again.")
    _OAUTH_STATES.discard(state)
    _, _, Flow, _ = _google_modules()
    flow = Flow.from_client_config(
        {"web": {
            "client_id": settings.gmail_client_id,
            "client_secret": settings.gmail_client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [settings.gmail_redirect_uri],
        }},
        scopes=SCOPES, state=state,
    )
    flow.redirect_uri = settings.gmail_redirect_uri
    try:
        flow.fetch_token(code=code)
    except Exception as error:
        raise HTTPException(status_code=400, detail="Google OAuth exchange failed. Check redirect URI and consent setup.") from error
    token_file = _token_path()
    token_file.write_text(flow.credentials.to_json(), encoding="utf-8")
    try:
        token_file.chmod(0o600)
    except OSError:
        pass
    record_event("gmail.connected", "gmail_account", None, {"scopes": ["readonly", "compose", "send"]})
    return {"status": "connected", "message": "Gmail connected. Return to the CareerPilot dashboard."}


@router.get("/messages")
def search_gmail_messages(
    q: str = Query(default="newer_than:90d", max_length=500),
    max_results: int = Query(default=20, ge=1, le=50),
) -> dict:
    service = _service()
    result = service.users().messages().list(
        userId="me", q=q, maxResults=max_results
    ).execute()
    items = []
    for item in result.get("messages", []):
        message = service.users().messages().get(
            userId="me", id=item["id"], format="metadata",
            metadataHeaders=["From", "To", "Subject", "Date", "Message-ID", "References"],
        ).execute()
        headers = {h["name"].lower(): h["value"] for h in message.get("payload", {}).get("headers", [])}
        items.append({
            "id": message["id"], "thread_id": message.get("threadId"),
            "from": headers.get("from", ""), "to": headers.get("to", ""),
            "subject": headers.get("subject", "(no subject)"),
            "date": headers.get("date", ""), "snippet": message.get("snippet", ""),\n            "message_id_header": headers.get("message-id", ""),\n            "references_header": headers.get("references", ""),
        })
    return {"items": items, "next_page_token": result.get("nextPageToken")}


def _raw_message(item: EmailDraft) -> str:
    message = MIMEText(item.body, "plain", "utf-8")
    message["To"] = ", ".join(str(address) for address in item.to)
    message["Subject"] = item.subject
    if item.in_reply_to:
        message["In-Reply-To"] = item.in_reply_to
    if item.references:
        message["References"] = item.references
    return base64.urlsafe_b64encode(message.as_bytes()).decode("ascii")


@router.post("/drafts", status_code=201)
def create_gmail_draft(item: EmailDraft) -> dict:
    service = _service()
    payload = {"message": {"raw": _raw_message(item)}}
    if item.thread_id:
        payload["message"]["threadId"] = item.thread_id
    draft = service.users().drafts().create(userId="me", body=payload).execute()
    record_event("gmail.draft_created", "gmail_draft", None,
                 {"recipient_count": len(item.to), "subject_length": len(item.subject)})
    return {"id": draft["id"], "message_id": draft.get("message", {}).get("id"), "status": "draft_created"}


@router.post("/send")
def send_gmail_message(item: EmailDraft) -> dict:
    """Send only when the user explicitly invokes this endpoint from the UI."""
    service = _service()
    payload = {"raw": _raw_message(item)}
    if item.thread_id:
        payload["threadId"] = item.thread_id
    sent = service.users().messages().send(userId="me", body=payload).execute()
    record_event("gmail.message_sent", "gmail_message", None,
                 {"recipient_count": len(item.to), "subject_length": len(item.subject)})
    return {"id": sent["id"], "thread_id": sent.get("threadId"), "status": "sent"}
