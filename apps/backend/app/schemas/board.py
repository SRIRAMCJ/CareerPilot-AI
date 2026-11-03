from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class BoardCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    provider: Literal["greenhouse", "lever", "ashby", "workable"]
    company_slug: str = Field(min_length=1, max_length=60, pattern=r"^[A-Za-z0-9_-]+$")

    def normalized_slug(self) -> str:
        return self.company_slug.lower()


class DiscoveryRunRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    query: str | None = Field(default=None, max_length=120)
    limit_per_board: int = Field(default=50, ge=1, le=100)
