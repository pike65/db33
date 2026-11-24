from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.database.models import (
    Author,
    AuthorHasPaper,
    Keyword,
    Paper,
    PaperVersion,
    Review,
    Track,
)
from app.database.models import (
    Session as ConfSession,
)
from app.modules.papers.schemas import PaperCreate, PaperUpdate


def _validate_session_assignment(
    db: Session,
    *,
    session_id: int | None,
    status: str,
    track: Track,
) -> ConfSession | None:
    if session_id is None:
        return None

    session = db.scalar(select(ConfSession).where(ConfSession.session_id == session_id))
    if not session:
        raise NotFoundError("Session not found.")

    if status != "accepted":
        raise ValueError("Only accepted papers can be assigned to a session.")

    if track.conference_id != session.conference_id:
        raise ValueError(
            "Paper's track conference must match the session's conference."
        )

    return session


def _check_authors_not_reviewing(
    db: Session, paper_id: int, author_ids: list[int]
) -> None:
    if not author_ids:
        return
    conflicting_reviewer_id = db.scalar(
        select(Review.reviewer_id).where(
            Review.paper_id == paper_id,
            Review.reviewer_id.in_(author_ids),
        )
    )
    if conflicting_reviewer_id is not None:
        raise ValueError(
            f"Reviewer {conflicting_reviewer_id} has already reviewed this paper and cannot be listed as an author."
        )


def _sync_paper_keywords(db: Session, paper_id: int, keywords: list[str]) -> None:
    unique_keywords = list(dict.fromkeys(keywords))
    db.execute(delete(Keyword).where(Keyword.paper_id == paper_id))
    for kw in unique_keywords:
        db.add(Keyword(paper_id=paper_id, keyword=kw))


def _sync_paper_authors(db: Session, paper_id: int, authors_data: list) -> None:
    author_ids = list(dict.fromkeys(a.author_id for a in authors_data))
    found_author_ids = set(
        db.scalars(
            select(Author.author_id).where(Author.author_id.in_(author_ids))
        ).all()
    )
    missing_authors = [aid for aid in author_ids if aid not in found_author_ids]
    if missing_authors:
        raise NotFoundError(f"Authors not found: {missing_authors}")

    _check_authors_not_reviewing(db, paper_id=paper_id, author_ids=author_ids)

    db.execute(delete(AuthorHasPaper).where(AuthorHasPaper.paper_id == paper_id))
    seen_authors: set[int] = set()
    for a in authors_data:
        if a.author_id in seen_authors:
            continue
        seen_authors.add(a.author_id)
        db.add(
            AuthorHasPaper(
                paper_id=paper_id,
                author_id=a.author_id,
                author_order=a.author_order,
                is_corresponding=a.is_corresponding,
            )
        )


def add_new_paper_to_db(db: Session, data: PaperCreate) -> Paper:
    track = db.scalar(select(Track).where(Track.track_id == data.track_id))
    if not track:
        raise NotFoundError("Track not found.")

    _validate_session_assignment(
        db,
        session_id=data.session_id,
        status=data.status,
        track=track,
    )

    author_ids = list(dict.fromkeys(a.author_id for a in data.authors))
    found_author_ids = set(
        db.scalars(
            select(Author.author_id).where(Author.author_id.in_(author_ids))
        ).all()
    )
    missing_authors = [aid for aid in author_ids if aid not in found_author_ids]
    if missing_authors:
        raise NotFoundError(f"Authors not found: {missing_authors}")

    paper = Paper(
        title=data.title,
        abstract=data.abstract,
        status=data.status,
        submission_date=data.submission_date,
        track_id=data.track_id,
        session_id=data.session_id,
    )
    db.add(paper)

    try:
        db.flush()

        for kw in dict.fromkeys(data.keywords):
            db.add(Keyword(paper_id=paper.paper_id, keyword=kw))

        seen_authors: set[int] = set()
        for a in data.authors:
            if a.author_id in seen_authors:
                continue
            seen_authors.add(a.author_id)
            db.add(
                AuthorHasPaper(
                    paper_id=paper.paper_id,
                    author_id=a.author_id,
                    author_order=a.author_order,
                    is_corresponding=a.is_corresponding,
                )
            )

        db.add(
            PaperVersion(
                paper_id=paper.paper_id,
                version_number=data.version.version_number,
                file_location=data.version.file_location,
                upload_datetime=data.version.upload_datetime,
                note=data.version.note,
            )
        )

        db.commit()
    except IntegrityError:
        db.rollback()
        raise

    db.refresh(paper)
    return paper


def get_all_papers_from_db(db: Session, skip: int = 0, limit: int = 100) -> list[Paper]:
    query = select(Paper).order_by(Paper.paper_id).offset(skip).limit(limit)
    return list(db.scalars(query).all())


def get_paper_by_id_from_db(db: Session, paper_id: int) -> Paper:
    paper = db.get(Paper, paper_id)
    if not paper:
        raise NotFoundError("Paper not found.")
    return paper


def update_paper_in_db(db: Session, paper_id: int, data: PaperUpdate) -> Paper:
    paper = db.scalar(select(Paper).where(Paper.paper_id == paper_id))
    if not paper:
        raise NotFoundError("Paper not found.")

    updates = data.model_dump(exclude_unset=True)
    if not updates:
        return paper

    keywords = updates.pop("keywords", None)
    authors_data = data.authors if "authors" in updates else None
    updates.pop("authors", None)
    version_data = data.version if "version" in updates else None
    updates.pop("version", None)

    target_track_id = updates.get("track_id", paper.track_id)
    target_track = db.scalar(select(Track).where(Track.track_id == target_track_id))
    if not target_track:
        raise NotFoundError("Track not found.")

    target_status = updates.get("status", paper.status)
    target_session_id = updates.get("session_id", paper.session_id)

    _validate_session_assignment(
        db,
        session_id=target_session_id,
        status=target_status,
        track=target_track,
    )

    for field, value in updates.items():
        setattr(paper, field, value)

    try:
        if keywords is not None:
            _sync_paper_keywords(db, paper_id=paper_id, keywords=keywords)

        if authors_data is not None:
            _sync_paper_authors(db, paper_id=paper_id, authors_data=authors_data)

        if version_data is not None:
            db.add(
                PaperVersion(
                    paper_id=paper_id,
                    version_number=version_data.version_number,
                    file_location=version_data.file_location,
                    upload_datetime=version_data.upload_datetime,
                    note=version_data.note,
                )
            )

        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("Invalid paper update or constraint violation.") from None

    db.refresh(paper)
    return paper


def delete_paper_from_db(db: Session, paper_id: int) -> None:
    paper = db.scalar(select(Paper).where(Paper.paper_id == paper_id))
    if not paper:
        raise NotFoundError("Paper not found.")

    db.delete(paper)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError(
            "Cannot delete paper due to active references or constraint violation."
        ) from None
