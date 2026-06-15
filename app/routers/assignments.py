import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.db.connection import get_db
from app.db.models import Assignment, User
from app.schemas.assignment import (
    AssignmentCreate,
    AssignmentRead,
    AssignmentUpdate,
)
from app.security import get_current_user, verify_assignment, verify_course

router = APIRouter(prefix="/courses", tags=["Assignments"])


@router.post("/{course_id}/assignments", response_model=AssignmentRead, status_code=201)
def create_assignment(
    course_id: uuid.UUID,
    assignment: AssignmentCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    verify_course(course_id, user, db)
    new_assignment = Assignment(
        course_id=course_id,
        number=assignment.number,
        total_marks=assignment.total_marks,
        obtained_marks=assignment.obtained_marks,
        note=assignment.note,
    )
    try:
        db.add(new_assignment)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Failed to add assignment: assignment with this number already exists",
        )

    db.refresh(new_assignment)
    return new_assignment


@router.get("/{course_id}/assignments", response_model=list[AssignmentRead])
def get_assignments(
    course_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    verify_course(course_id, user, db)
    stmt = select(Assignment).where(Assignment.course_id == course_id)
    return db.exec(stmt).all()


@router.get("/{course_id}/assignments/{assignment_id}", response_model=AssignmentRead)
def get_assignment(
    course_id: uuid.UUID,
    assignment_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    assignment = verify_assignment(assignment_id, user, db)
    return assignment


@router.patch("/{course_id}/assignments/{assignment_id}", response_model=AssignmentRead)
def update_assignment(
    course_id: uuid.UUID,
    assignment_id: uuid.UUID,
    update: AssignmentUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    assignment = verify_assignment(assignment_id, user, db)
    if update.number is not None:
        assignment.number = update.number
    if update.total_marks is not None:
        assignment.total_marks = update.total_marks
    if update.obtained_marks is not None:
        assignment.obtained_marks = update.obtained_marks
    if update.note is not None:
        assignment.note = update.note

    if assignment.obtained_marks > assignment.total_marks:
        raise HTTPException(
            status_code=409, detail="Obtained Marks must be less than total marks."
        )

    try:
        db.add(assignment)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Failed to add assignment: assignment with this number already exists",
        )

    db.refresh(assignment)
    return assignment


@router.delete("/{course_id}/assignments/{assignment_id}", status_code=204)
def delete_assignment(
    course_id: uuid.UUID,
    assignment_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    assignment = verify_assignment(assignment_id, user, db)
    db.delete(assignment)
    db.commit()
