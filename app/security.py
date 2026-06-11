from datetime import datetime, timedelta, timezone
from typing import Annotated
import uuid

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import EmailStr
from sqlmodel import Session, select
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

from app.db.connection import get_db
from app.db.models import AttendanceRecord, Course, User, Assignment, Quiz
from app.schemas.token import TokenData
from app.settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

config = Config(".env")
oauth = OAuth(config)
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


def get_user(email: EmailStr, db: Session) -> User | None:
    return db.exec(select(User).where(User.email == email)).first()


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(email=token_data.email, db=db)
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def verify_course(course_id: uuid.UUID, user: User, db: Session) -> Course:
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return course


def verify_record(record_id: uuid.UUID, user: User, db: Session) -> AttendanceRecord:
    record = db.get(AttendanceRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record Not Found")
    if record.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not Authorized")

    return record


def verify_assignment(assignment_id: uuid.UUID, user: User, db: Session) -> Assignment:
    assignment = db.get(Assignment, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    course = db.get(Course, assignment.course_id)
    if not course or course.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return assignment


def verify_quiz(quiz_id: uuid.UUID, user: User, db: Session) -> Quiz:
    quiz = db.get(Quiz, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    course = db.get(Course, quiz.course_id)
    if not course or course.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return quiz
