from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import SQLModel
from starlette.middleware.sessions import SessionMiddleware

from app.db.connection import engine
from app.routers import auth, courses, dashboard, record
from app.settings import settings, Settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(
    title="Orbit",
    description="Track your attendance",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.deployment_type == "dev" else None,
    redoc_url="/redoc" if settings.deployment_type == "dev" else None,
    openapi_url="/openapi.json" if settings.deployment_type == "dev" else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key=settings.session_secret)

app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(record.router)
app.include_router(dashboard.router)
