from app.schemas.course import CourseSummary
from pydantic import BaseModel


class SummaryResponse(BaseModel):
    courses: list[CourseSummary]
