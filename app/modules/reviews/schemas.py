from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Recommendation = Literal["accept", "reject"]


# -------------------- base classes -------------------- #
class ReviewBase(BaseModel):
    reviewer_id: int = Field(..., ge=1)
    paper_id: int = Field(..., ge=1)
    overall_score: int = Field(..., ge=1, le=5)
    recommendation: Recommendation
    comments_for_authors: str = Field(..., max_length=500)
    confidential_comments: str = Field(..., max_length=500)
    submission_date: date


# -------------------- create -------------------- #
class ReviewCreate(ReviewBase):
    pass


# -------------------- update -------------------- #
class ReviewUpdate(BaseModel):
    reviewer_id: int | None = Field(default=None, ge=1)
    paper_id: int | None = Field(default=None, ge=1)
    overall_score: int | None = Field(default=None, ge=1, le=5)
    recommendation: Recommendation | None = None
    comments_for_authors: str | None = Field(default=None, min_length=1, max_length=500)
    confidential_comments: str | None = Field(
        default=None, min_length=1, max_length=500
    )
    submission_date: date | None = None

    @model_validator(mode="before")
    @classmethod
    def reject_explicit_nulls(cls, data: object) -> object:
        if isinstance(data, dict):
            required_fields = (
                "reviewer_id",
                "paper_id",
                "overall_score",
                "recommendation",
                "comments_for_authors",
                "confidential_comments",
                "submission_date",
            )
            for field in required_fields:
                if field in data and data[field] is None:
                    raise ValueError(f"{field} cannot be null.")
        return data

    @field_validator("comments_for_authors", "confidential_comments", mode="before")
    @classmethod
    def strip_and_reject_blank(cls, value: object, info) -> object:
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                raise ValueError(f"{info.field_name} cannot be blank.")
            return stripped
        return value


# -------------------- response -------------------- #
class ReviewResponse(ReviewBase):
    model_config = ConfigDict(from_attributes=True)

    review_id: int
