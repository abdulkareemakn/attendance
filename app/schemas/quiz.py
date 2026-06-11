import uuid

from pydantic import BaseModel, Field


class QuizBase(BaseModel):
    number: int
    total_marks: int = Field(ge=1)
    obtained_marks: float
    note: str | None = None


class QuizCreate(QuizBase):
    pass


class QuizRead(QuizBase):
    id: uuid.UUID
    course_id: uuid.UUID


class QuizUpdate(QuizBase):
    number: int | None = None
    total_marks: int | None = Field(default=None, ge=1)
    obtained_marks: float | None = None
    note: str | None = None
