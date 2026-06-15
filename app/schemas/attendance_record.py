import datetime
import uuid

from pydantic import BaseModel

from app.schemas.course import CourseBase
from app.schemas.enums import RecordType, Status


class AttendanceRecordBase(BaseModel):
    date: datetime.date
    record_type: RecordType
    status: Status = Status.present
    class_conducted: bool = True
    # TODO: If false, adapt status accordingly
    note: str | None = None


class AttendanceRecordCreate(AttendanceRecordBase):
    pass


class AttendanceRecordRead(AttendanceRecordBase):
    id: uuid.UUID


class AttendanceRecordUpdate(BaseModel):
    date: datetime.date | None = None
    record_type: RecordType | None = None
    status: Status | None = None
    class_conducted: bool | None = None
    note: str | None = None
