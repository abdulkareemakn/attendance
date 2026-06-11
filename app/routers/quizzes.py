from sqlalchemy.exc import IntegrityError
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db.connection import get_db
from app.db.models import Quiz, User
from app.schemas.quiz import (
    QuizCreate,
    QuizRead,
    QuizUpdate,
)
from app.security import get_current_user, verify_course, verify_quiz

router = APIRouter(prefix="/courses", tags=["Quizzes"])


@router.post("/{course_id}/quizzes", response_model=QuizRead, status_code=201)
def create_quiz(
    course_id: uuid.UUID,
    quiz: QuizCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    verify_course(course_id, user, db)

    new_quiz = Quiz(
        course_id=course_id,
        number=quiz.number,
        total_marks=quiz.total_marks,
        obtained_marks=quiz.obtained_marks,
        note=quiz.note,
    )

    try:
        db.add(new_quiz)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Failed to add quiz: Quiz number already exists for this course",
        )

    db.refresh(new_quiz)
    return new_quiz


@router.get("/{course_id}/quizzes", response_model=list[QuizRead])
def get_quizzes(
    course_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    verify_course(course_id, user, db)
    stmt = select(Quiz).where(Quiz.course_id == course_id)
    return db.exec(stmt).all()


@router.get("/{course_id}/quizzes/{quiz_id}", response_model=QuizRead)
def get_quiz(
    course_id: uuid.UUID,
    quiz_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    quiz = verify_quiz(quiz_id, user, db)
    return quiz


@router.patch("/{course_id}/quizzes/{quiz_id}", response_model=QuizRead)
def update_quiz(
    course_id: uuid.UUID,
    quiz_id: uuid.UUID,
    update: QuizUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    quiz = verify_quiz(quiz_id, user, db)
    if update.number is not None:
        quiz.number = update.number
    if update.total_marks is not None:
        quiz.total_marks = update.total_marks
    if update.obtained_marks is not None:
        quiz.obtained_marks = update.obtained_marks
    if update.note is not None:
        quiz.note = update.note

    try:
        db.add(quiz)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Failed to update quiz: Quiz number already exists for this course",
        )

    db.refresh(quiz)
    return quiz


@router.delete("/{course_id}/quizzes/{quiz_id}", status_code=204)
def delete_quiz(
    course_id: uuid.UUID,
    quiz_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    quiz = verify_quiz(quiz_id, user, db)
    db.delete(quiz)
    db.commit()
