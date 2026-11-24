from fastapi import APIRouter, HTTPException, Query, status

from app.core.exceptions import NotFoundError
from app.database.db import DBSession
from app.modules.tracks import service
from app.modules.tracks.schemas import TrackResponse, TrackUpdate

router = APIRouter(prefix="/tracks", tags=["tracks"])


@router.get("/", response_model=list[TrackResponse], status_code=status.HTTP_200_OK)
def get_all_tracks(
    db: DBSession,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
):
    return service.get_all_tracks_from_db(db, skip=skip, limit=limit)


@router.get("/{track_id}", response_model=TrackResponse, status_code=status.HTTP_200_OK)
def get_track_by_id(db: DBSession, track_id: int):
    try:
        return service.get_track_by_id_from_db(db, track_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.patch(
    "/{track_id}", response_model=TrackResponse, status_code=status.HTTP_200_OK
)
def update_track(db: DBSession, track_id: int, payload: TrackUpdate):
    try:
        return service.update_track_in_db(db, track_id=track_id, data=payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.delete("/{track_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_track(db: DBSession, track_id: int):
    try:
        service.delete_track_from_db(db, track_id=track_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
