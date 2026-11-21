from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.models import User
from app.modules.users.schemas import UserCreate


def add_new_user_to_db(db: Session, data: UserCreate) -> User:
    user = User(**data.model_dump())
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(user)
    return user


def get_all_users_from_db(db: Session) -> list[User]:
    return list(db.scalars(select(User)).all())
