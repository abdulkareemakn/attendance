from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import SQLModel
from starlette.middleware.sessions import SessionMiddleware

from app.db.connection import engine
from app.routers import auth, courses, dashboard, record
from app.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(
    title="Orbit",
    description="Track your attendance",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(SessionMiddleware, secret_key=settings.session_secret)

app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(record.router)
app.include_router(dashboard.router)
