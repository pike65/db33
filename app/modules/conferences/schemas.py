from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


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


# -------------------- input -------------------- #
class ConferenceTrackCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: str = Field(..., max_length=500)
    research_area_id: int = Field(..., ge=1)
    reviewer_id: int = Field(..., ge=1)


class ConferenceCreate(ConferenceBase):
    reviewer_ids: list[int] = Field(..., min_length=1)
    tracks: list[ConferenceTrackCreate] = Field(..., min_length=1)


# -------------------- output -------------------- #
class ConferenceResponse(ConferenceBase):
    model_config = ConfigDict(from_attributes=True)

    conference_id: int

    @field_validator("hosts", mode="before")
    @classmethod
    def extract_host_names(cls, value):
        if isinstance(value, list) and value and hasattr(value[0], "host_name"):
            return [host.host_name for host in value]
        return value
