from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

# Engine to work with DB using settings.DATABASE_URL
engine = create_engine(settings.DATABASE_URL)

# Session maker to make queries
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DBSession = Annotated[Session, Depends(get_db)]


# Base class for all tables
class Base(DeclarativeBase):
    pass
