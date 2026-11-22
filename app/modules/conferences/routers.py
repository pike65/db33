from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import NotFoundError
from app.database.db import DBSession
from app.modules.conferences import service
from app.modules.conferences.schemas import ConferenceCreate, ConferenceResponse

router = APIRouter(prefix="/conferences", tags=["conferences"])


@router.post(
    "/", response_model=ConferenceResponse, status_code=status.HTTP_201_CREATED
)
def create_new_conference(db: DBSession, payload: ConferenceCreate):
    try:
        return service.add_new_conference_to_db(db, payload)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid conference data or constraint violation.",
        )


@router.get(
    "/", response_model=list[ConferenceResponse], status_code=status.HTTP_200_OK
)
def get_all_conferences(db: DBSession):
    return service.get_all_conferences_from_db(db)


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
