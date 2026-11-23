from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

PaperStatus = Literal[
    "submitted",
    "under review",
    "accepted",
    "rejected",
    "withdrawn",
]


class PaperAuthorInput(BaseModel):
    author_id: int = Field(..., ge=1)
    author_order: int = Field(..., ge=1)
    is_corresponding: bool = False


class PaperVersionInput(BaseModel):
    version_number: int = Field(default=1, ge=1)
    file_location: str = Field(..., max_length=500)
    upload_datetime: datetime
    note: str | None = Field(default=None, max_length=500)


class PaperBase(BaseModel):
    title: str = Field(..., max_length=500)
    abstract: str = Field(..., max_length=500)
    submission_date: date
    track_id: int = Field(..., ge=1)
    session_id: int | None = Field(default=None, ge=1)
    keywords: list[str] = Field(..., min_length=1)


class PaperCreate(PaperBase):
    status: PaperStatus = "submitted"
    authors: list[PaperAuthorInput] = Field(..., min_length=1)
    version: PaperVersionInput


class PaperVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    version_number: int
    file_location: str
    upload_datetime: datetime
    note: str | None


class PaperAuthorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    author_id: int
    author_order: int
    is_corresponding: bool


class PaperResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    paper_id: int
    title: str
    abstract: str
    status: PaperStatus
    submission_date: date
    track_id: int
    session_id: int | None
    keywords: list[str]
    authors: list[PaperAuthorResponse]
    versions: list[PaperVersionResponse]

    @field_validator("keywords", mode="before")
    @classmethod
    def extract_keywords(cls, value):
        if isinstance(value, list) and value and hasattr(value[0], "keyword"):
            return [item.keyword for item in value]
        return value
