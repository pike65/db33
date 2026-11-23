from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class UserBase(BaseModel):
    email: EmailStr
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    country: str = Field(..., max_length=100)
    affiliation: str = Field(..., max_length=100)
    phone_number: str = Field(..., max_length=100)


class AuthorCreate(BaseModel):
    orcid: Annotated[str | None, Field(min_length=19, max_length=19)] = None
    research_area_ids: list[int] = Field(default_factory=list, min_length=1)


class ReviewerCreate(BaseModel):
    years_of_experience: int = Field(..., ge=0)
    expertise_area_ids: list[int] = Field(default_factory=list, min_length=1)


class UserCreate(UserBase):
    author: AuthorCreate | None = None
    reviewer: ReviewerCreate | None = None

    @model_validator(mode="after")
    def require_at_least_one_specialization(self) -> UserCreate:
        if self.author is None and self.reviewer is None:
            raise ValueError(
                "User must have at least one specialization: author or reviewer."
            )
        return self


class AuthorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    author_id: int
    orcid: str | None = None


class ReviewerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    reviewer_id: int
    years_of_experience: int


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    author: AuthorResponse | None = Field(
        default=None, validation_alias="author_profile"
    )
    reviewer: ReviewerResponse | None = Field(
        default=None, validation_alias="reviewer_profile"
    )
