import re
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.core.audit_database import record_event
from app.core.resume_database import (
    create_resume_record, delete_resume_record, get_resume_record,
    list_resume_records, local_resume_directory,
)
from app.schemas.resume import ResumeRecord, ResumeUploadResult
from app.services.resume_parser import extract_facts, extract_text

router = APIRouter(prefix="/api/v1/resumes", tags=["resume intelligence"])
MAX_RESUME_BYTES = 10 * 1024 * 1024


def _validate_file(filename: str, content: bytes) -> str:
    suffix = Path(filename).suffix.casefold()
    if suffix == ".pdf" and content.startswith(b"%PDF-"):
        return "pdf"
    if suffix == ".docx" and content.startswith(b"PK"):
        return "docx"
    raise HTTPException(status_code=415, detail="Upload a valid PDF or DOCX resume.")


@router.post("", response_model=ResumeUploadResult, status_code=status.HTTP_201_CREATED)
async def upload_resume(file: UploadFile = File(...)) -> dict:
    filename = Path(file.filename or "resume").name
    content = await file.read(MAX_RESUME_BYTES + 1)
    await file.close()
    if not content:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    if len(content) > MAX_RESUME_BYTES:
        raise HTTPException(status_code=413, detail="Resume exceeds the 10 MB limit.")
    file_type = _validate_file(filename, content)
    try:
        extracted = extract_text(content, file_type)
    except Exception as error:
        raise HTTPException(status_code=422, detail="The resume could not be parsed. Check that the file is valid and readable.") from error
    if not extracted:
        raise HTTPException(status_code=422, detail="No selectable text was found. Scanned-image PDFs need OCR, which is not enabled yet.")
    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", filename)[:120] or "resume"
    destination = local_resume_directory() / f"{uuid4().hex}_{safe_name}"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(content)
    try:
        record = create_resume_record(safe_name, file_type, len(content), str(destination), extracted)
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    record_event("resume.uploaded", "resume", record["id"], {"file_type": file_type, "file_size": len(content), "text_length": len(extracted)})
    facts = extract_facts(extracted)
    return {
        **record,
        "extracted_text_length": len(extracted),
        "extracted_skills": facts["skills"],
        "extracted_email": facts["email"],
        "extracted_phone": facts["phone"],
    }


@router.get("", response_model=list[ResumeRecord])
def list_resumes() -> list[dict]:
    return list_resume_records()


@router.get("/{resume_id}/preview")
def preview_resume(resume_id: int) -> dict:
    record = get_resume_record(resume_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Resume not found.")
    facts = extract_facts(record["extracted_text"])
    return {
        "id": record["id"],
        "filename": record["filename"],
        "text": record["extracted_text"],
        "facts": facts,
    }


@router.delete("/{resume_id}")
def delete_resume(resume_id: int) -> dict:
    record = delete_resume_record(resume_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Resume not found.")
    Path(record["stored_path"]).unlink(missing_ok=True)
    record_event("resume.deleted", "resume", resume_id)
    return {"status": "deleted", "id": resume_id}
