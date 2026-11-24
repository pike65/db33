from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# -------------------- base classes -------------------- #
class ConferenceBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: str = Field(..., max_length=500)
    acronym: str = Field(..., max_length=20)
    city: str = Field(..., max_length=100)
    country: str = Field(..., max_length=100)
    hosts: list[str] = Field(..., min_length=1)

    start_date: date
    end_date: date
    paper_submission_deadline: datetime
    paper_review_deadline: datetime


# -------------------- create -------------------- #
class ConferenceTrackCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: str = Field(..., max_length=500)
    research_area_id: int = Field(..., ge=1)
    reviewer_id: int = Field(..., ge=1)


class ConferenceCreate(ConferenceBase):
    reviewer_ids: list[int] = Field(..., min_length=1)
    tracks: list[ConferenceTrackCreate] = Field(..., min_length=1)


# -------------------- update -------------------- #
class ConferenceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, min_length=1, max_length=500)
    acronym: str | None = Field(default=None, min_length=1, max_length=20)
    city: str | None = Field(default=None, min_length=1, max_length=100)
    country: str | None = Field(default=None, min_length=1, max_length=100)
    hosts: list[str] | None = Field(default=None, min_length=1)

    start_date: date | None = None
    end_date: date | None = None
    paper_submission_deadline: datetime | None = None
    paper_review_deadline: datetime | None = None

    @model_validator(mode="before")
    @classmethod
    def reject_explicit_nulls(cls, data: object) -> object:
        if isinstance(data, dict):
            non_nullable_fields = (
                "name",
                "description",
                "acronym",
                "city",
                "country",
                "hosts",
                "start_date",
                "end_date",
                "paper_submission_deadline",
                "paper_review_deadline",
            )
            for field in non_nullable_fields:
                if field in data and data[field] is None:
                    raise ValueError(f"{field} cannot be null.")
        return data

    @field_validator(
        "name",
        "description",
        "acronym",
        "city",
        "country",
        mode="before",
    )
    @classmethod
    def strip_and_reject_blank_str(cls, value: object, info) -> object:
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                raise ValueError(f"{info.field_name} cannot be blank.")
            return stripped
        return value

    @field_validator("hosts", mode="before")
    @classmethod
    def clean_hosts(cls, value: object) -> object:
        if isinstance(value, list):
            cleaned: list[str] = []
            for host in value:
                if not isinstance(host, str) or not host.strip():
                    raise ValueError("Host names cannot be blank.")
                cleaned.append(host.strip())
            return cleaned
        return value


# -------------------- response -------------------- #
class ConferenceResponse(ConferenceBase):
    model_config = ConfigDict(from_attributes=True)

    conference_id: int

    @field_validator("hosts", mode="before")
    @classmethod
    def extract_host_names(cls, value):
        if isinstance(value, list) and value and hasattr(value[0], "host_name"):
            return [host.host_name for host in value]
        return value
