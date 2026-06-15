from pydantic import BaseModel

from app.schemas.course import CourseSummary


class SummaryResponse(BaseModel):
    courses: list[CourseSummary]
