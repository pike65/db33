from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import InvalidAreaError, NotFoundError
from app.database.db import DBSession
from app.modules.users import service
from app.modules.users.schemas import (
    UserCreate,
    UserResponse,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_new_user(db: DBSession, payload: UserCreate):
    try:
        return service.create_user_with_specializations(db, payload)
    except InvalidAreaError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email or phone number already exists.",
        )


@router.get("/", response_model=list[UserResponse], status_code=status.HTTP_200_OK)
def get_all_users(db: DBSession):
    return service.get_all_users_from_db(db)


@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_user_by_id(db: DBSession, user_id: int):
    try:
        return service.get_user_by_id_from_db(db, user_id)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
