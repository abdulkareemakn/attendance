import uuid

from pydantic import BaseModel


class AssignmentBase(BaseModel):
    number: int
    total_marks: int
    obtained_marks: float
    note: str | None = None


class AssignmentCreate(AssignmentBase):
    pass


class AssignmentRead(AssignmentBase):
    id: uuid.UUID
    course_id: uuid.UUID


class AssignmentUpdate(AssignmentBase):
    number: int | None = None
    total_marks: int | None = None
    obtained_marks: float | None = None
    note: str | None = None
