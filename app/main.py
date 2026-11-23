import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database.db import Base, engine

# Routers
from app.modules.admin.routers import router as admin_router
from app.modules.conferences.routers import router as conferences_router
from app.modules.sessions.routers import router as sessions_router
from app.modules.users.routers import router as users_router

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


app.include_router(admin_router)
app.include_router(users_router)
app.include_router(conferences_router)
app.include_router(sessions_router)
