from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DiscoveryRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    provider: Literal["greenhouse", "lever", "ashby", "workable"]
    company_slug: str = Field(min_length=1, max_length=60, pattern=r"^[A-Za-z0-9_-]+$")
    query: str | None = Field(default=None, max_length=120)
    limit: int = Field(default=50, ge=1, le=100)

    @field_validator("company_slug")
    @classmethod
    def normalize_slug(cls, value: str) -> str:
        return value.lower()
