from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import InvalidAreaError, NotFoundError
from app.database.db import DBSession
from app.modules.users import service
from app.modules.users.schemas import (
    AuthorResponse,
    AuthorUpdate,
    ReviewerResponse,
    ReviewerUpdate,
    UserCreate,
    UserResponse,
    UserUpdate,
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
def get_all_users(
    db: DBSession,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
):
    return service.get_all_users_from_db(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_user_by_id(db: DBSession, user_id: int):
    try:
        return service.get_user_by_id_from_db(db, user_id)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.patch("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def update_user(user_id: int, payload: UserUpdate, db: DBSession):
    try:
        return service.update_user_in_db(db, user_id=user_id, data=payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.patch(
    "/authors/{author_id}",
    response_model=AuthorResponse,
    status_code=status.HTTP_200_OK,
)
def update_author(author_id: int, payload: AuthorUpdate, db: DBSession):
    try:
        return service.update_author_in_db(db, author_id=author_id, data=payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.patch(
    "/reviewers/{reviewer_id}",
    response_model=ReviewerResponse,
    status_code=status.HTTP_200_OK,
)
def update_reviewer(reviewer_id: int, payload: ReviewerUpdate, db: DBSession):
    try:
        return service.update_reviewer_in_db(db, reviewer_id=reviewer_id, data=payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
