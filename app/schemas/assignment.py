import uuid

from pydantic import BaseModel, Field


class AssignmentBase(BaseModel):
    number: int
    total_marks: int = Field(ge=1)
    obtained_marks: float
    note: str | None = None


class AssignmentCreate(AssignmentBase):
    pass


class AssignmentRead(AssignmentBase):
    id: uuid.UUID
    course_id: uuid.UUID


class AssignmentUpdate(AssignmentBase):
    number: int | None = None
    total_marks: int | None = Field(default=None, ge=1)
    obtained_marks: float | None = None
    note: str | None = None
