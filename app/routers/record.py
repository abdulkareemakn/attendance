import uuid

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.db.connection import get_db
from app.db.models import AttendanceRecord, User
from app.schemas.attendance_record import (
    AttendanceRecordCreate,
    AttendanceRecordRead,
    AttendanceRecordUpdate,
)
from app.security import get_current_user, verify_record, verify_course


router = APIRouter(prefix="/courses", tags=["attendance"])


@router.post(
    "/{course_id}/attendance", response_model=AttendanceRecordRead, status_code=201
)
async def add_record(
    course_id: uuid.UUID,
    record: AttendanceRecordCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    course = verify_course(course_id, user, db)

    new_record = AttendanceRecord(
        course_id=course_id,
        user_id=user.id,
        date=record.date,
        record_type=record.record_type,
        status=record.status,
        class_conducted=record.class_conducted,
        note=record.note,
    )

    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    return new_record


@router.get("/{course_id}/attendance", response_model=list[AttendanceRecordRead])
async def get_attendance_records(
    course_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stmt = select(AttendanceRecord).where(
        AttendanceRecord.user_id == user.id, AttendanceRecord.course_id == course_id
    )
    return db.exec(stmt).all()


@router.patch(
    "/{course_id}/attendance/{record_id}", response_model=AttendanceRecordRead
)
async def update_attendance_record(
    course_id: uuid.UUID,
    record_id: uuid.UUID,
    update: AttendanceRecordUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = verify_record(record_id, user, db)

    if update.date is not None:
        record.date = update.date

    if update.record_type is not None:
        record.record_type = update.record_type

    if update.status is not None:
        record.status = update.status

    if update.class_conducted is not None:
        record.class_conducted = update.class_conducted

    if update.note is not None:
        record.note = update.note

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


@router.delete("/{course_id}/attendance/{record_id}", status_code=204)
async def delete_attendance_record(
    course_id: uuid.UUID,
    record_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = verify_record(record_id, user, db)

    db.delete(record)
    db.commit()
