from datetime import datetime
from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator, model_validator


class InterviewCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    application_id: int = Field(gt=0)
    title: str = Field(min_length=2, max_length=180)
    event_type: Literal["interview", "assessment", "recruiter_call", "technical_round", "other"] = "interview"
    starts_at: datetime
    ends_at: datetime
    timezone_name: str = Field(default="Asia/Kolkata", min_length=1, max_length=80)
    meeting_url: HttpUrl | None = None
    notes: str = Field(default="", max_length=4000)
    reminder_minutes: int = Field(default=30, ge=0, le=10080)

    @field_validator("timezone_name")
    @classmethod
    def validate_timezone(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as error:
            raise ValueError("Use a valid IANA timezone, such as Asia/Kolkata.") from error
        return value

    @model_validator(mode="after")
    def validate_times(self):
        if self.starts_at.tzinfo is None or self.starts_at.utcoffset() is None:
            raise ValueError("starts_at must include a timezone offset.")
        if self.ends_at.tzinfo is None or self.ends_at.utcoffset() is None:
            raise ValueError("ends_at must include a timezone offset.")
        if self.ends_at <= self.starts_at:
            raise ValueError("ends_at must be after starts_at.")
        return self


class InterviewUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    title: str | None = Field(default=None, min_length=2, max_length=180)
    event_type: Literal["interview", "assessment", "recruiter_call", "technical_round", "other"] | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    timezone_name: str | None = Field(default=None, min_length=1, max_length=80)
    meeting_url: HttpUrl | None = None
    notes: str | None = Field(default=None, max_length=4000)
    reminder_minutes: int | None = Field(default=None, ge=0, le=10080)

    @model_validator(mode="after")
    def validate_time_pair(self):
        for field in ("title", "event_type", "starts_at", "ends_at", "timezone_name", "notes", "reminder_minutes"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null.")
        if self.starts_at is not None and (self.starts_at.tzinfo is None or self.starts_at.utcoffset() is None):
            raise ValueError("starts_at must include a timezone offset.")
        if self.ends_at is not None and (self.ends_at.tzinfo is None or self.ends_at.utcoffset() is None):
            raise ValueError("ends_at must include a timezone offset.")
        if self.starts_at and self.ends_at and self.ends_at <= self.starts_at:
            raise ValueError("ends_at must be after starts_at.")
        return self
