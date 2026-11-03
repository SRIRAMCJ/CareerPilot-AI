from datetime import date
from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class JobListingCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    title: str = Field(min_length=2, max_length=200)
    company: str = Field(min_length=1, max_length=160)
    location: str | None = Field(default=None, max_length=160)
    work_mode: str | None = Field(default=None, max_length=40)
    job_type: str | None = Field(default=None, max_length=60)
    source: str = Field(default="manual", min_length=1, max_length=80)
    source_job_id: str | None = Field(default=None, max_length=200)
    url: HttpUrl | None = None
    description: str = Field(default="", max_length=30000)
    required_skills: list[str] = Field(default_factory=list, max_length=100)
    salary_min: int | None = Field(default=None, ge=0)
    salary_max: int | None = Field(default=None, ge=0)
    salary_currency: str = Field(default="INR", min_length=3, max_length=3)
    posted_date: date | None = None


class JobListing(JobListingCreate):
    id: int
    status: str
    created_at: str


class JobMatch(BaseModel):
    job_id: int
    score: int
    decision: str
    matched_skills: list[str]
    missing_skills: list[str]
    reasons: list[str]
