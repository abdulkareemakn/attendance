import pytest
import httpx

BASE_URL = "http://localhost:8000"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmYTI0LWJzZS0xMjNAY3VpbGFob3JlLmVkdS5wayIsImV4cCI6MTc4MDg0OTc0Mn0.v7YQCeTnCkZh6a_ySC6FDlDe_1_vuDqzlovX1zjAR1w"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

state = {
    "course_id": None,
    "course_with_lab_id": None,
    "theory_record_id": None,
    "lab_record_id": None,
}


class TestCourses:
    def test_create_course_no_lab(self):
        r = httpx.post(
            f"{BASE_URL}/courses/",
            json={
                "name": "Data Structures",
                "instructor": "Dr. Khan",
                "has_lab": False,
            },
            headers=HEADERS,
        )
        assert r.status_code == 201
        data = r.json()
        assert data["name"] == "Data Structures"
        assert data["instructor"] == "Dr. Khan"
        assert data["has_lab"] is False
        assert "id" in data
        state["course_id"] = data["id"]

    def test_create_course_with_lab(self):
        r = httpx.post(
            f"{BASE_URL}/courses/",
            json={"name": "OOP", "instructor": "Dr. Ahmed", "has_lab": True},
            headers=HEADERS,
        )
        assert r.status_code == 201
        data = r.json()
        assert data["has_lab"] is True
        state["course_with_lab_id"] = data["id"]

    def test_create_course_missing_fields(self):
        r = httpx.post(
            f"{BASE_URL}/courses/",
            json={"name": "Incomplete Course"},
            headers=HEADERS,
        )
        assert r.status_code == 422

    def test_create_course_unauthorized(self):
        r = httpx.post(
            f"{BASE_URL}/courses/",
            json={"name": "OOP", "instructor": "Dr. Ahmed", "has_lab": False},
        )
        assert r.status_code == 401

    def test_get_courses(self):
        r = httpx.get(f"{BASE_URL}/courses/", headers=HEADERS)
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) >= 2

    def test_get_courses_unauthorized(self):
        r = httpx.get(f"{BASE_URL}/courses/")
        assert r.status_code == 401

    def test_get_single_course(self):
        r = httpx.get(f"{BASE_URL}/courses/{state['course_id']}", headers=HEADERS)
        assert r.status_code == 200
        assert r.json()["id"] == state["course_id"]

    def test_get_course_not_found(self):
        r = httpx.get(
            f"{BASE_URL}/courses/00000000-0000-0000-0000-000000000000",
            headers=HEADERS,
        )
        assert r.status_code == 404

    def test_update_course_name(self):
        r = httpx.patch(
            f"{BASE_URL}/courses/{state['course_id']}",
            json={"name": "DSA"},
            headers=HEADERS,
        )
        assert r.status_code == 200
        assert r.json()["name"] == "DSA"

    def test_update_course_instructor(self):
        r = httpx.patch(
            f"{BASE_URL}/courses/{state['course_id']}",
            json={"instructor": "Dr. Ali"},
            headers=HEADERS,
        )
        assert r.status_code == 200
        assert r.json()["instructor"] == "Dr. Ali"

    def test_update_course_not_found(self):
        r = httpx.patch(
            f"{BASE_URL}/courses/00000000-0000-0000-0000-000000000000",
            json={"name": "Ghost"},
            headers=HEADERS,
        )
        assert r.status_code == 404


class TestAttendance:
    def test_add_theory_record_present(self):
        r = httpx.post(
            f"{BASE_URL}/courses/{state['course_id']}/attendance",
            json={
                "date": "2025-01-15",
                "record_type": "theory",
                "status": "present",
                "class_conducted": True,
            },
            headers=HEADERS,
        )
        assert r.status_code == 201
        data = r.json()
        assert data["record_type"] == "theory"
        assert data["status"] == "present"
        state["theory_record_id"] = data["id"]

    def test_add_theory_record_absent(self):
        r = httpx.post(
            f"{BASE_URL}/courses/{state['course_id']}/attendance",
            json={
                "date": "2025-01-16",
                "record_type": "theory",
                "status": "absent",
                "class_conducted": True,
            },
            headers=HEADERS,
        )
        assert r.status_code == 201
        assert r.json()["status"] == "absent"

    def test_add_record_class_not_conducted(self):
        r = httpx.post(
            f"{BASE_URL}/courses/{state['course_id']}/attendance",
            json={
                "date": "2025-01-17",
                "record_type": "theory",
                "class_conducted": False,
            },
            headers=HEADERS,
        )
        assert r.status_code == 201
        assert r.json()["class_conducted"] is False

    def test_add_record_with_note(self):
        r = httpx.post(
            f"{BASE_URL}/courses/{state['course_id']}/attendance",
            json={
                "date": "2025-01-18",
                "record_type": "theory",
                "status": "absent",
                "class_conducted": True,
                "note": "Was sick",
            },
            headers=HEADERS,
        )
        assert r.status_code == 201
        assert r.json()["note"] == "Was sick"

    def test_add_lab_record(self):
        r = httpx.post(
            f"{BASE_URL}/courses/{state['course_with_lab_id']}/attendance",
            json={
                "date": "2025-01-15",
                "record_type": "lab",
                "status": "present",
                "class_conducted": True,
            },
            headers=HEADERS,
        )
        assert r.status_code == 201
        assert r.json()["record_type"] == "lab"
        state["lab_record_id"] = r.json()["id"]

    def test_add_record_missing_fields(self):
        r = httpx.post(
            f"{BASE_URL}/courses/{state['course_id']}/attendance",
            json={"date": "2025-01-19"},
            headers=HEADERS,
        )
        assert r.status_code == 422

    def test_add_record_invalid_record_type(self):
        r = httpx.post(
            f"{BASE_URL}/courses/{state['course_id']}/attendance",
            json={
                "date": "2025-01-20",
                "record_type": "seminar",
                "status": "present",
            },
            headers=HEADERS,
        )
        assert r.status_code == 422

    def test_add_record_invalid_status(self):
        r = httpx.post(
            f"{BASE_URL}/courses/{state['course_id']}/attendance",
            json={
                "date": "2025-01-20",
                "record_type": "theory",
                "status": "maybe",
            },
            headers=HEADERS,
        )
        assert r.status_code == 422

    def test_add_record_course_not_found(self):
        r = httpx.post(
            f"{BASE_URL}/courses/00000000-0000-0000-0000-000000000000/attendance",
            json={"date": "2025-01-20", "record_type": "theory", "status": "present"},
            headers=HEADERS,
        )
        assert r.status_code == 404

    def test_get_attendance_records(self):
        r = httpx.get(
            f"{BASE_URL}/courses/{state['course_id']}/attendance",
            headers=HEADERS,
        )
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) >= 4

    def test_get_attendance_records_unauthorized(self):
        r = httpx.get(f"{BASE_URL}/courses/{state['course_id']}/attendance")
        assert r.status_code == 401

    def test_update_attendance_record(self):
        r = httpx.patch(
            f"{BASE_URL}/courses/{state['course_id']}/attendance/{state['theory_record_id']}",
            json={"status": "absent", "note": "Updated note"},
            headers=HEADERS,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "absent"
        assert data["note"] == "Updated note"

    def test_update_attendance_record_not_found(self):
        r = httpx.patch(
            f"{BASE_URL}/courses/{state['course_id']}/attendance/00000000-0000-0000-0000-000000000000",
            json={"status": "present"},
            headers=HEADERS,
        )
        assert r.status_code == 404


class TestSummary:
    def test_summary_returns_courses(self):
        r = httpx.get(f"{BASE_URL}/dashboard/summary", headers=HEADERS)
        assert r.status_code == 200
        data = r.json()
        assert "courses" in data
        assert isinstance(data["courses"], list)

    def test_summary_has_percentages(self):
        r = httpx.get(f"{BASE_URL}/dashboard/summary", headers=HEADERS)
        data = r.json()
        for course in data["courses"]:
            assert "theory_percentage" in course
            assert isinstance(course["theory_percentage"], float)

    def test_summary_lab_percentage_none_for_no_lab(self):
        r = httpx.get(f"{BASE_URL}/dashboard/summary", headers=HEADERS)
        data = r.json()
        no_lab = [c for c in data["courses"] if not c["has_lab"]]
        for course in no_lab:
            assert course.get("lab_percentage") is None

    def test_summary_lab_percentage_present_for_lab_course(self):
        r = httpx.get(f"{BASE_URL}/dashboard/summary", headers=HEADERS)
        data = r.json()
        with_lab = [c for c in data["courses"] if c["has_lab"]]
        for course in with_lab:
            assert course.get("lab_percentage") is not None

    def test_summary_unauthorized(self):
        r = httpx.get(f"{BASE_URL}/dashboard/summary")
        assert r.status_code == 401

    def test_summary_percentage_range(self):
        r = httpx.get(f"{BASE_URL}/dashboard/summary", headers=HEADERS)
        data = r.json()
        for course in data["courses"]:
            assert 0.0 <= course["theory_percentage"] <= 100.0
            if course["lab_percentage"] is not None:
                assert 0.0 <= course["lab_percentage"] <= 100.0


class TestCleanup:
    def test_delete_theory_record(self):
        r = httpx.delete(
            f"{BASE_URL}/courses/{state['course_id']}/attendance/{state['theory_record_id']}",
            headers=HEADERS,
        )
        assert r.status_code == 204

    def test_delete_lab_record(self):
        r = httpx.delete(
            f"{BASE_URL}/courses/{state['course_with_lab_id']}/attendance/{state['lab_record_id']}",
            headers=HEADERS,
        )
        assert r.status_code == 204

    def test_delete_course(self):
        r = httpx.delete(
            f"{BASE_URL}/courses/{state['course_id']}",
            headers=HEADERS,
        )
        assert r.status_code == 204

    def test_delete_course_with_lab(self):
        r = httpx.delete(
            f"{BASE_URL}/courses/{state['course_with_lab_id']}",
            headers=HEADERS,
        )
        assert r.status_code == 204

    def test_delete_course_not_found(self):
        r = httpx.delete(
            f"{BASE_URL}/courses/00000000-0000-0000-0000-000000000000",
            headers=HEADERS,
        )
        assert r.status_code == 404
