import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database.db import Base, engine

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    print("Tables are created!")

    yield

    print("Shutting down...")


app = FastAPI(
    title="Matrix Research System",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
def health():
    return {"health": "ok"}
