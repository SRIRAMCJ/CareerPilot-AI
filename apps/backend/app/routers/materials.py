from pathlib import Path

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.core import database
from app.core.applications_database import get_application
from app.core.config import get_settings
from app.core.jobs_database import get_job
from app.core.materials_database import create_material, get_material, list_materials
from app.services.ai_provider import generate_cover_letter
from app.services.materials_generator import generate_application_pack, generated_material_directory

router = APIRouter(prefix="/api/v1", tags=["application materials"])


@router.post("/applications/{application_id}/materials")
def create_application_materials(application_id: int) -> dict:
    application = get_application(application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Application tracker not found.")
    stored_profile = database.read_profile()
    if stored_profile is None:
        raise HTTPException(status_code=409, detail="Create and verify your candidate profile first.")
    profile = stored_profile["profile"]
    job = {
        "title": application["job_title"],
        "company": application["company"],
    }
    generated = generate_application_pack(profile, job, generated_material_directory())
    material = create_material(
        application_id, "resume_and_cover_letter", generated["filename"], generated["path"]
    )
    return {**material, "download_url": f"/api/v1/materials/{material['id']}/download"}


@router.get("/applications/{application_id}/materials")
def get_application_materials(application_id: int) -> dict:
    if get_application(application_id) is None:
        raise HTTPException(status_code=404, detail="Application tracker not found.")
    return {"items": list_materials(application_id)}


@router.get("/materials/{material_id}/download")
def download_material(material_id: int) -> FileResponse:
    material = get_material(material_id)
    if material is None or not Path(material["stored_path"]).is_file():
        raise HTTPException(status_code=404, detail="Generated material not found.")
    return FileResponse(
        material["stored_path"],
        filename=material["filename"],
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


@router.post("/applications/{application_id}/cover-letter/ai")
async def generate_ai_cover_letter(application_id: int) -> dict:
    application = get_application(application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Application tracker not found.")
    stored_profile = database.read_profile()
    if stored_profile is None:
        raise HTTPException(status_code=409, detail="Create and verify your candidate profile first.")
    settings = get_settings()
    if settings.ai_provider.casefold() != "ollama":
        raise HTTPException(status_code=409, detail="Set AI_PROVIDER=ollama to enable local AI drafting.")
    job = get_job(application["job_id"])
    if job is None:
        raise HTTPException(status_code=404, detail="Job listing not found.")
    try:
        draft = await generate_cover_letter(
            stored_profile["profile"], job, settings.ollama_base_url, settings.ollama_model
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except httpx.HTTPError as error:
        raise HTTPException(status_code=502, detail="The local Ollama model could not be reached.") from error
    return {
        "application_id": application_id,
        "draft": draft,
        "warning": "AI-generated draft. Verify every claim against your actual experience before using it.",
        "provider": "ollama",
        "model": settings.ollama_model,
    }
