import uuid

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.db.connection import get_db
from app.db.models import Course, User
from app.schemas.course import CourseCreate, CourseRead, CourseUpdate
from app.security import get_current_user, verify_course

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.post("/", response_model=CourseRead, status_code=201)
def create_course(
    course: CourseCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    new_course = Course(
        name=course.name,
        instructor=course.instructor,
        has_lab=course.has_lab,
        user_id=user.id,
    )

    db.add(new_course)
    db.commit()
    db.refresh(new_course)

    return new_course


@router.get("/", response_model=list[CourseRead])
def get_courses(
    include_archived: bool = False,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stmt = select(Course).where(Course.user_id == user.id)
    if not include_archived:
        stmt = stmt.where(Course.is_archived == False)
    return db.exec(stmt).all()


@router.get("/{course_id}", response_model=CourseRead)
def get_course(
    course_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    course = verify_course(course_id, user, db)

    return course


@router.patch("/{course_id}", response_model=CourseRead)
def update_course(
    course_id: uuid.UUID,
    update: CourseUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    course = verify_course(course_id, user, db)

    if update.name is not None:
        course.name = update.name

    if update.instructor is not None:
        course.instructor = update.instructor

    db.add(course)
    db.commit()
    db.refresh(course)

    return course


@router.patch("/{course_id}/archive", response_model=CourseRead)
def archive_course(
    course_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    course = verify_course(course_id, user, db)

    course.is_archived = True

    db.add(course)
    db.commit()
    db.refresh(course)

    return course


@router.patch("/{course_id}/unarchive", response_model=CourseRead)
def unarchive_course(
    course_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    course = verify_course(course_id, user, db)

    course.is_archived = False

    db.add(course)
    db.commit()
    db.refresh(course)

    return course


@router.delete("/{course_id}", status_code=204)
def delete_course(
    course_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    course = verify_course(course_id, user, db)

    db.delete(course)
    db.commit()
