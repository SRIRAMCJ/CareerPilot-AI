from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ApplicationStatus = Literal[
    "saved", "shortlisted", "preparing", "applied", "assessment",
    "interview", "offer", "rejected", "withdrawn"
]


class ApplicationCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    job_id: int = Field(gt=0)
    status: ApplicationStatus = "saved"
    notes: str = Field(default="", max_length=5000)
    applied_date: date | None = None
    next_action: str | None = Field(default=None, max_length=300)
    follow_up_date: date | None = None


class ApplicationUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    status: ApplicationStatus | None = None
    notes: str | None = Field(default=None, max_length=5000)
    applied_date: date | None = None
    next_action: str | None = Field(default=None, max_length=300)
    follow_up_date: date | None = None
