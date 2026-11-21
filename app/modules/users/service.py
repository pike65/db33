from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.models import (
    Author,
    AuthorResearchArea,
    ExpertiseArea,
    ResearchArea,
    Reviewer,
    ReviewerExpertiseArea,
    User,
)
from app.modules.users.schemas import UserCreate


class InvalidAreaError(Exception):
    pass


def _validate_area_ids(
    db: Session, model: type[ResearchArea | ExpertiseArea], id_col, ids: list[int]
) -> None:
    if not ids:
        return
    unique_ids = set(ids)
    found_ids = set(db.scalars(select(id_col).where(id_col.in_(unique_ids))).all())
    missing = unique_ids - found_ids
    if missing:
        raise InvalidAreaError(
            f"Unknown area IDs for {model.__tablename__}: {sorted(missing)}"
        )


def create_user_with_specializations(db: Session, data: UserCreate) -> User:
    if data.author is not None:
        _validate_area_ids(
            db,
            ResearchArea,
            ResearchArea.research_area_id,
            data.author.research_area_ids,
        )
    if data.reviewer is not None:
        _validate_area_ids(
            db,
            ExpertiseArea,
            ExpertiseArea.expertise_area_id,
            data.reviewer.expertise_area_ids,
        )

    user_data = data.model_dump(exclude={"author", "reviewer"})
    user = User(**user_data)
    db.add(user)

    try:
        db.flush()

        if data.author is not None:
            author = Author(author_id=user.user_id, orcid=data.author.orcid)
            db.add(author)
            for area_id in set(data.author.research_area_ids):
                db.add(
                    AuthorResearchArea(
                        author_id=user.user_id,
                        research_area_id=area_id,
                    )
                )

        if data.reviewer is not None:
            reviewer = Reviewer(
                reviewer_id=user.user_id,
                years_of_experience=data.reviewer.years_of_experience,
            )
            db.add(reviewer)
            for area_id in set(data.reviewer.expertise_area_ids):
                db.add(
                    ReviewerExpertiseArea(
                        reviewer_id=user.user_id,
                        expertise_area_id=area_id,
                    )
                )

        db.commit()
    except IntegrityError:
        db.rollback()
        raise

    db.refresh(user)
    return user


def get_all_users_from_db(db: Session) -> list[User]:
    return list(db.scalars(select(User)).all())
