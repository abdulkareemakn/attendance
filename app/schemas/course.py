import uuid

from pydantic import BaseModel


class CourseBase(BaseModel):
    name: str
    instructor: str
    has_lab: bool


class CourseCreate(CourseBase):
    pass


class CourseRead(CourseBase):
    id: uuid.UUID
    is_archived: bool


class CourseUpdate(BaseModel):
    name: str | None = None
    instructor: str | None = None


class CourseSummary(CourseBase):
    id: uuid.UUID
    theory_percentage: float
    lab_percentage: float | None = None
