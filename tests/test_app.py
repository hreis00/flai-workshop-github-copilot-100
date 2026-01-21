"""
Test cases for the High School Management System API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI application"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    # Store the original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"],
        },
        "Basketball Team": {
            "description": "Competitive basketball training and inter-school matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu", "lucas@mergington.edu"],
        },
        "Swimming Club": {
            "description": "Swimming lessons and competitive training for all skill levels",
            "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["ava@mergington.edu", "noah@mergington.edu"],
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and mixed media techniques",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["mia@mergington.edu", "lily@mergington.edu"],
        },
        "Drama Club": {
            "description": "Acting, theater production, and performance arts",
            "schedule": "Thursdays, 3:30 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["ethan@mergington.edu", "charlotte@mergington.edu"],
        },
        "Debate Team": {
            "description": "Develop critical thinking and public speaking through competitive debates",
            "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["william@mergington.edu", "amelia@mergington.edu"],
        },
        "Science Olympiad": {
            "description": "Compete in science challenges and experiments across various disciplines",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["benjamin@mergington.edu", "isabella@mergington.edu"],
        },
    }

    # Reset to original state before each test
    activities.clear()
    activities.update(original_activities)
    yield


class TestRootEndpoint:
    """Test cases for the root endpoint"""

    def test_root_redirects_to_static_index(self, client):
        """Test that root path redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Test cases for the GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_activities_have_required_fields(self, client):
        """Test that each activity has the required fields"""
        response = client.get("/activities")
        data = response.json()

        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_chess_club_initial_participants(self, client):
        """Test Chess Club has correct initial participants"""
        response = client.get("/activities")
        data = response.json()
        chess_club = data["Chess Club"]
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupForActivity:
    """Test cases for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_for_existing_activity(self, client):
        """Test successful signup for an existing activity"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Signed up newstudent@mergington.edu for Chess Club"

        # Verify the student was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert (
            "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
        )

    def test_signup_for_nonexistent_activity(self, client):
        """Test signup for an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "student@mergington.edu"},
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_for_activity_already_signed_up(self, client):
        """Test that a student cannot sign up twice for the same activity"""
        # First signup
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"},
        )
        assert response1.status_code == 200

        # Second signup (should fail)
        response2 = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"},
        )
        assert response2.status_code == 400
        assert (
            response2.json()["detail"] == "Student already signed up for this activity"
        )

    def test_signup_with_existing_student(self, client):
        """Test that existing student cannot sign up again"""
        response = client.post(
            "/activities/Chess Club/signup", params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 400
        assert (
            response.json()["detail"] == "Student already signed up for this activity"
        )

    def test_signup_for_multiple_activities(self, client):
        """Test that a student can sign up for multiple activities"""
        email = "multisport@mergington.edu"

        # Sign up for Chess Club
        response1 = client.post(
            "/activities/Chess Club/signup", params={"email": email}
        )
        assert response1.status_code == 200

        # Sign up for Programming Class
        response2 = client.post(
            "/activities/Programming Class/signup", params={"email": email}
        )
        assert response2.status_code == 200

        # Verify student is in both
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Chess Club"]["participants"]
        assert email in activities_data["Programming Class"]["participants"]


class TestUnregisterFromActivity:
    """Test cases for the DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_from_activity(self, client):
        """Test successful unregistration from an activity"""
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Removed michael@mergington.edu from Chess Club"

        # Verify the student was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert (
            "michael@mergington.edu"
            not in activities_data["Chess Club"]["participants"]
        )

    def test_unregister_from_nonexistent_activity(self, client):
        """Test unregistration from an activity that doesn't exist"""
        response = client.delete(
            "/activities/Nonexistent Club/unregister",
            params={"email": "student@mergington.edu"},
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_student_not_signed_up(self, client):
        """Test unregistration of a student who is not signed up"""
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "notsignedup@mergington.edu"},
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is not signed up for this activity"

    def test_unregister_and_resign_up(self, client):
        """Test that a student can re-sign up after unregistering"""
        email = "michael@mergington.edu"

        # Unregister
        response1 = client.delete(
            "/activities/Chess Club/unregister", params={"email": email}
        )
        assert response1.status_code == 200

        # Sign up again
        response2 = client.post(
            "/activities/Chess Club/signup", params={"email": email}
        )
        assert response2.status_code == 200

        # Verify student is signed up again
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Chess Club"]["participants"]


class TestActivityWorkflow:
    """Integration tests for complete workflows"""

    def test_complete_signup_workflow(self, client):
        """Test a complete workflow: get activities, signup, verify, unregister"""
        # Get initial activities
        response1 = client.get("/activities")
        assert response1.status_code == 200
        initial_count = len(response1.json()["Drama Club"]["participants"])

        # Sign up new student
        email = "newactor@mergington.edu"
        response2 = client.post(
            "/activities/Drama Club/signup", params={"email": email}
        )
        assert response2.status_code == 200

        # Verify signup
        response3 = client.get("/activities")
        assert response3.status_code == 200
        drama_club = response3.json()["Drama Club"]
        assert len(drama_club["participants"]) == initial_count + 1
        assert email in drama_club["participants"]

        # Unregister
        response4 = client.delete(
            "/activities/Drama Club/unregister", params={"email": email}
        )
        assert response4.status_code == 200

        # Verify unregistration
        response5 = client.get("/activities")
        assert response5.status_code == 200
        drama_club_final = response5.json()["Drama Club"]
        assert len(drama_club_final["participants"]) == initial_count
        assert email not in drama_club_final["participants"]

    def test_multiple_students_multiple_activities(self, client):
        """Test multiple students signing up for multiple activities"""
        students = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu",
        ]
        activities_list = ["Chess Club", "Programming Class", "Art Studio"]

        # Sign up all students for all activities
        for student in students:
            for activity in activities_list:
                response = client.post(
                    f"/activities/{activity}/signup", params={"email": student}
                )
                assert response.status_code == 200

        # Verify all signups
        response = client.get("/activities")
        activities_data = response.json()

        for activity in activities_list:
            for student in students:
                assert student in activities_data[activity]["participants"]
