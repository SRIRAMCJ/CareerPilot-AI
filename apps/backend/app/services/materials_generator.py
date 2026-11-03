from pathlib import Path
from uuid import uuid4

from docx import Document

from app.core.config import get_settings


def generate_application_pack(profile: dict, job: dict, output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"careerpilot_application_{uuid4().hex[:12]}.docx"
    destination = output_dir / filename

    document = Document()
    document.add_heading(profile["full_name"], level=0)
    contact = " | ".join(
        value for value in (profile.get("email"), profile.get("phone"), profile.get("location")) if value
    )
    if contact:
        document.add_paragraph(contact)
    if profile.get("headline"):
        document.add_paragraph(profile["headline"])

    document.add_heading("Professional Summary", level=1)
    summary = profile.get("professional_summary") or ""
    if summary:
        document.add_paragraph(summary)
    else:
        roles = ", ".join(profile.get("target_roles") or [])
        skills = ", ".join(profile.get("skills") or [])
        document.add_paragraph(
            f"Candidate targeting {roles or job['title']}. Verified skills include {skills or 'not yet provided'}."
        )

    document.add_heading("Skills", level=1)
    skills = list(dict.fromkeys((profile.get("skills") or []) + (profile.get("tools_and_technologies") or [])))
    document.add_paragraph(", ".join(skills) if skills else "No verified skills have been added.")

    for heading, key in (
        ("Experience", "experience"),
        ("Projects", "projects"),
        ("Education", "education"),
        ("Certifications", "certifications"),
    ):
        entries = profile.get(key) or []
        if entries:
            document.add_heading(heading, level=1)
            for entry in entries:
                document.add_paragraph(entry, style="List Bullet")

    document.add_page_break()
    document.add_heading("Cover Letter Draft", level=0)
    document.add_paragraph(f"Application for {job['title']} at {job['company']}")
    document.add_paragraph("Dear Hiring Team,")
    opening = (
        f"I am interested in the {job['title']} opportunity at {job['company']}."
    )
    if profile.get("current_role"):
        opening += f" I currently work as {profile['current_role']}."
    document.add_paragraph(opening)
    verified_skills = ", ".join(skills)
    if verified_skills:
        document.add_paragraph(
            f"My profile lists skills in {verified_skills}. "
            "I would welcome the opportunity to discuss how this verified background aligns with your requirements."
        )
    if summary:
        document.add_paragraph(summary)
    document.add_paragraph(
        "Thank you for your time and consideration. I would be glad to provide any further information."
    )
    document.add_paragraph("Sincerely,")
    document.add_paragraph(profile["full_name"])
    document.save(destination)
    return {"filename": filename, "path": str(destination)}


def generated_material_directory() -> Path:
    
    configured = get_settings().careerpilot_generated_dir
    directory = Path(configured).expanduser() if configured else Path.home() / ".careerpilot" / "generated"
    directory.mkdir(parents=True, exist_ok=True)
    return directory
