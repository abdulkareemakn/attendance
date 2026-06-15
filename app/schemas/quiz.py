import uuid
from email.policy import default

from pydantic import BaseModel, Field, model_validator


class QuizBase(BaseModel):
    number: int
    total_marks: int = Field(ge=1)
    obtained_marks: float = Field(ge=1)
    note: str | None = None

    @model_validator(mode="after")
    def validate_marks(self):
        if self.obtained_marks is not None and self.total_marks is not None:
            if self.obtained_marks > self.total_marks:
                raise ValueError(
                    "Obtained Marks must be less than or equal to total marks."
                )
        return self


class QuizCreate(QuizBase):
    pass


class QuizRead(QuizBase):
    id: uuid.UUID
    course_id: uuid.UUID


class QuizUpdate(QuizBase):
    number: int | None = None
    total_marks: int | None = Field(default=None, ge=1)
    obtained_marks: float | None = Field(default=None, ge=1)
    note: str | None = None
