from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.db.connection import get_db
from app.db.models import AttendanceRecord, Course, User
from app.schemas.course import CourseSummary
from app.schemas.dashboard import SummaryResponse
from app.schemas.enums import RecordType, Status
from app.security import get_current_user
from app.utils import calculate_percentage

router = APIRouter(prefix="/dashboard")


@router.get("/summary", response_model=SummaryResponse)
def summary(
    include_archived: bool = False,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    results: list[CourseSummary] = []
    stmt = select(Course).where(Course.user_id == user.id)
    if not include_archived:
        stmt = stmt.where(Course.is_archived == False)
    courses = db.exec(stmt).all()
    for course in courses:
        records = db.exec(
            select(AttendanceRecord).where(AttendanceRecord.course_id == course.id)
        ).all()
        results.append(
            CourseSummary(
                id=course.id,
                name=course.name,
                instructor=course.instructor,
                has_lab=course.has_lab,
                theory_percentage=calculate_percentage(records, RecordType.theory),
                lab_percentage=calculate_percentage(records, RecordType.lab)
                if course.has_lab
                else None,
            )
        )
    return {"courses": results}
