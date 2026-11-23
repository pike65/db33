from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.database.models import (
    Author,
    AuthorHasPaper,
    Keyword,
    Paper,
    PaperVersion,
    Track,
)
from app.database.models import (
    Session as ConfSession,
)
from app.modules.papers.schemas import PaperCreate


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


# For update endpoint
# def _check_authors_not_reviewing(
#     db: Session, paper_id: int, author_ids: list[int]
# ) -> None:
#     conflicting_reviewer_id = db.scalar(
#         select(Review.reviewer_id).where(
#             Review.paper_id == paper_id,
#             Review.reviewer_id.in_(author_ids),
#         )
#     )
#     if conflicting_reviewer_id is not None:
#         raise ValueError(
#             f"Reviewer {conflicting_reviewer_id} has already reviewed this paper and cannot be listed as an author."
#         )


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
    paper = db.scalar(select(Paper).where(Paper.paper_id == paper_id))
    if not paper:
        raise NotFoundError("Paper not found.")
    return paper
