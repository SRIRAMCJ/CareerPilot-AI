from pydantic import BaseModel, ConfigDict, Field


class CandidateProfile(BaseModel):
    """Verified candidate facts and job-search preferences.

    Keep this data on the user's device. Do not populate it from assumptions.
    """

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    full_name: str = Field(min_length=1, max_length=120)
    email: str | None = Field(default=None, max_length=254)
    phone: str | None = Field(default=None, max_length=40)
    location: str | None = Field(default=None, max_length=120)
    headline: str | None = Field(default=None, max_length=160)
    professional_summary: str | None = Field(default=None, max_length=3000)
    current_role: str | None = Field(default=None, max_length=160)
    years_experience: float | None = Field(default=None, ge=0, le=60)
    target_roles: list[str] = Field(default_factory=list, max_length=30)
    preferred_locations: list[str] = Field(default_factory=list, max_length=30)
    preferred_work_modes: list[str] = Field(default_factory=list, max_length=5)
    minimum_salary: int | None = Field(default=None, ge=0)
    salary_currency: str = Field(default="INR", min_length=3, max_length=3)
    skills: list[str] = Field(default_factory=list, max_length=100)
    tools_and_technologies: list[str] = Field(default_factory=list, max_length=100)
    education: list[str] = Field(default_factory=list, max_length=20)
    experience: list[str] = Field(default_factory=list, max_length=30)
    projects: list[str] = Field(default_factory=list, max_length=50)
    certifications: list[str] = Field(default_factory=list, max_length=50)
    preferred_job_types: list[str] = Field(default_factory=list, max_length=10)
    notice_period: str | None = Field(default=None, max_length=80)
    resume_file_path: str | None = Field(default=None, max_length=500)
