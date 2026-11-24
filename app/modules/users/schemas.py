from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)


# -------------------- base classes -------------------- #
class UserBase(BaseModel):
    email: EmailStr
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    country: str = Field(..., max_length=100)
    affiliation: str = Field(..., max_length=100)
    phone_number: str = Field(..., max_length=100)


# -------------------- create -------------------- #
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


# -------------------- update -------------------- #
class UserUpdate(BaseModel):
    email: EmailStr | None = Field(default=None, max_length=255)
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    country: str | None = Field(default=None, min_length=1, max_length=100)
    affiliation: str | None = Field(default=None, min_length=1, max_length=100)
    phone_number: str | None = Field(default=None, min_length=1, max_length=100)

    @model_validator(mode="before")
    @classmethod
    def reject_explicit_nulls(cls, data: object) -> object:
        if isinstance(data, dict):
            required_fields = (
                "email",
                "first_name",
                "last_name",
                "country",
                "affiliation",
                "phone_number",
            )
            for field in required_fields:
                if field in data and data[field] is None:
                    raise ValueError(f"{field} cannot be null.")
        return data

    @field_validator(
        "email",
        "first_name",
        "last_name",
        "country",
        "affiliation",
        "phone_number",
        mode="before",
    )
    @classmethod
    def strip_and_reject_blank(cls, value: object, info) -> object:
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                raise ValueError(f"{info.field_name} cannot be blank.")
            return stripped
        return value


class AuthorUpdate(BaseModel):
    orcid: str | None = Field(default=None, min_length=1, max_length=50)
    research_area_ids: list[int] | None = None

    @model_validator(mode="before")
    @classmethod
    def reject_explicit_nulls(cls, data: object) -> object:
        if (
            isinstance(data, dict)
            and "research_area_ids" in data
            and data["research_area_ids"] is None
        ):
            raise ValueError("research_area_ids cannot be null.")
        return data

    @field_validator("orcid", mode="before")
    @classmethod
    def strip_and_reject_blank_orcid(cls, value: object) -> object:
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                raise ValueError("orcid cannot be blank.")
            return stripped
        return value


class ReviewerUpdate(BaseModel):
    years_of_experience: int | None = Field(default=None, ge=0, le=100)
    expertise_area_ids: list[int] | None = None

    @model_validator(mode="before")
    @classmethod
    def reject_explicit_nulls(cls, data: object) -> object:
        if isinstance(data, dict):
            for field in ("years_of_experience", "expertise_area_ids"):
                if field in data and data[field] is None:
                    raise ValueError(f"{field} cannot be null.")
        return data


# -------------------- response -------------------- #
class AuthorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    author_id: int
    orcid: str | None = None
    research_area_ids: list[int] = Field(default_factory=list)


class ReviewerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    reviewer_id: int
    years_of_experience: int
    expertise_area_ids: list[int] = Field(default_factory=list)


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    author: AuthorResponse | None = Field(
        default=None, validation_alias="author_profile"
    )
    reviewer: ReviewerResponse | None = Field(
        default=None, validation_alias="reviewer_profile"
    )
