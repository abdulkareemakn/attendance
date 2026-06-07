from collections.abc import Sequence
from app.schemas.enums import RecordType, Status
from app.db.models import AttendanceRecord


def calculate_percentage(
    records: Sequence[AttendanceRecord], record_type: RecordType
) -> float:
    filtered = [r for r in records if r.record_type == record_type]
    conducted = [r for r in filtered if r.class_conducted]
    attended = [r for r in conducted if r.status == Status.present]
    return round((len(attended) / len(conducted) * 100), 1) if conducted else 0.0
