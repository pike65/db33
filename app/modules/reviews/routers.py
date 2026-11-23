from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import NotFoundError
from app.database.db import DBSession
from app.modules.reviews import service
from app.modules.reviews.schemas import ReviewCreate, ReviewResponse

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_new_review(db: DBSession, payload: ReviewCreate):
    try:
        return service.add_new_review_to_db(db, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid review data or constraint violation.",
        )


@router.get("/", response_model=list[ReviewResponse], status_code=status.HTTP_200_OK)
def get_all_reviews(
    db: DBSession,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
):
    return service.get_all_reviews_from_db(db, skip=skip, limit=limit)


@router.get(
    "/{review_id}", response_model=ReviewResponse, status_code=status.HTTP_200_OK
)
def get_review_by_id(db: DBSession, review_id: int):
    try:
        return service.get_review_by_id_from_db(db, review_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
