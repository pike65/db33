from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.database.db import DBSession
from app.modules.users import service
from app.modules.users.schemas import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_new_user(db: DBSession, payload: UserCreate):
    try:
        return service.add_new_user_to_db(db, payload)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email or phone number already exists.",
        )


@router.get("/", response_model=list[UserResponse])
def get_all_users(db: DBSession):
    return service.get_all_users_from_db(db)
