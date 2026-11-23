from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import NotFoundError
from app.database.db import DBSession
from app.modules.sessions import service
from app.modules.sessions.schemas import SessionCreate, SessionResponse

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_new_session(db: DBSession, payload: SessionCreate):
    try:
        return service.add_new_session_to_db(db, payload)
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


@router.get("/", response_model=list[SessionResponse], status_code=status.HTTP_200_OK)
def get_all_sessions(
    db: DBSession,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
):
    return service.get_all_sessions_from_db(db, skip=skip, limit=limit)


@router.get(
    "/{session_id}", response_model=SessionResponse, status_code=status.HTTP_200_OK
)
def get_session_by_id(db: DBSession, session_id: int):
    try:
        return service.get_session_by_id_from_db(db, session_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
