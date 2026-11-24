from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import NotFoundError
from app.database.db import DBSession
from app.modules.conferences import service
from app.modules.conferences.schemas import (
    ConferenceCreate,
    ConferenceResponse,
    ConferenceUpdate,
)

router = APIRouter(prefix="/conferences", tags=["conferences"])


@router.post(
    "/", response_model=ConferenceResponse, status_code=status.HTTP_201_CREATED
)
def create_new_conference(db: DBSession, payload: ConferenceCreate):
    try:
        return service.add_new_conference_to_db(db, payload)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid conference data or constraint violation.",
        )


@router.get(
    "/", response_model=list[ConferenceResponse], status_code=status.HTTP_200_OK
)
def get_all_conferences(
    db: DBSession,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
):
    return service.get_all_conferences_from_db(db, skip=skip, limit=limit)


@router.get(
    "/{conference_id}",
    response_model=ConferenceResponse,
    status_code=status.HTTP_200_OK,
)
def get_conference_by_id(db: DBSession, conference_id: int):
    try:
        return service.get_conference_by_id_from_db(db, conference_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.patch(
    "/{conference_id}",
    response_model=ConferenceResponse,
    status_code=status.HTTP_200_OK,
)
def update_conference(db: DBSession, conference_id: int, payload: ConferenceUpdate):
    try:
        return service.update_conference_in_db(
            db, conference_id=conference_id, data=payload
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.delete(
    "/{conference_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_conference(db: DBSession, conference_id: int):
    try:
        service.delete_conference_from_db(db, conference_id=conference_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
