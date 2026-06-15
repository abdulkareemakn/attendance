from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from sqlmodel import Session, SQLModel, select
from starlette.middleware.sessions import SessionMiddleware

from app.db.connection import engine, get_db
from app.routers import assignments, auth, courses, dashboard, quizzes, record
from app.settings import Settings, settings


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
app.include_router(assignments.router)
app.include_router(quizzes.router)


@app.get("/")
def root():
    return {"message": "Orbit API", "version": "1.1.0"}


@app.get("/health")
def health(response: Response, session: Session = Depends(get_db)):
    try:
        session.exec(select(1))
        return {"status": "ok"}
    except Exception as e:
        response.status_code = 503
        return {"status": "unavailable", "detail": str(e)}
