from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import NotFoundError
from app.database.db import DBSession
from app.modules.papers import service
from app.modules.papers.schemas import (
    PaperCreate,
    PaperResponse,
    PaperUpdate,
)

router = APIRouter(prefix="/papers", tags=["papers"])


@router.post("/", response_model=PaperResponse, status_code=status.HTTP_201_CREATED)
def create_new_paper(db: DBSession, payload: PaperCreate):
    try:
        return service.add_new_paper_to_db(db, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid paper data or constraint violation.",
        )


@router.get("/", response_model=list[PaperResponse], status_code=status.HTTP_200_OK)
def get_all_papers(
    db: DBSession,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
):
    return service.get_all_papers_from_db(db, skip=skip, limit=limit)


@router.get("/{paper_id}", response_model=PaperResponse, status_code=status.HTTP_200_OK)
def get_paper_by_id(db: DBSession, paper_id: int):
    try:
        return service.get_paper_by_id_from_db(db, paper_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.patch(
    "/{paper_id}", response_model=PaperResponse, status_code=status.HTTP_200_OK
)
def update_paper(db: DBSession, paper_id: int, payload: PaperUpdate):
    try:
        return service.update_paper_in_db(db, paper_id=paper_id, data=payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.delete("/{paper_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_paper(db: DBSession, paper_id: int):
    try:
        service.delete_paper_from_db(db, paper_id=paper_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
