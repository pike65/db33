from pydantic import BaseModel, ConfigDict, EmailStr, Field


# -------------------- base classes -------------------- #
class UserBase(BaseModel):
    email: EmailStr
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    country: str = Field(..., max_length=100)
    affiliation: str = Field(..., max_length=100)
    phone_number: str = Field(..., max_length=100)


# -------------------- input -------------------- #
class UserCreate(UserBase):
    pass


# -------------------- output -------------------- #
class UserResponse(UserBase):
    user_id: int

    model_config = ConfigDict(from_attributes=True)
