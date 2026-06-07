from app.schemas.enums import RecordType, Status
import datetime
import uuid
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True)
    full_name: str
    is_active: bool = True


class Course(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    instructor: str
    has_lab: bool
    is_archived: bool = False
    user_id: uuid.UUID = Field(foreign_key="user.id")


class AttendanceRecord(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    course_id: uuid.UUID = Field(foreign_key="course.id")
    user_id: uuid.UUID = Field(foreign_key="user.id")
    date: datetime.date
    record_type: RecordType
    status: Status = Status.present
    class_conducted: bool = True
    note: str | None = None
