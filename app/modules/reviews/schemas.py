from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Recommendation = Literal["accept", "reject"]


class ReviewBase(BaseModel):
    reviewer_id: int = Field(..., ge=1)
    paper_id: int = Field(..., ge=1)
    overall_score: int = Field(..., ge=1, le=5)
    recommendation: Recommendation
    comments_for_authors: str = Field(..., max_length=500)
    confidential_comments: str = Field(..., max_length=500)
    submission_date: date


class ReviewCreate(ReviewBase):
    pass


class ReviewResponse(ReviewBase):
    model_config = ConfigDict(from_attributes=True)

    review_id: int
