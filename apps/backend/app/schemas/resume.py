from datetime import datetime

from pydantic import BaseModel


class ResumeUploadResult(BaseModel):
    id: int
    filename: str
    file_type: str
    file_size: int
    uploaded_at: datetime
    extracted_text_length: int
    extracted_skills: list[str]
    extracted_email: str | None
    extracted_phone: str | None


class ResumeRecord(BaseModel):
    id: int
    filename: str
    file_type: str
    file_size: int
    uploaded_at: str
