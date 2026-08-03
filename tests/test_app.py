import copy
import pytest
from fastapi.testclient import TestClient
from app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    # Snapshot state before each test and restore it afterward
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

def test_get_activities_returns_200_and_nonempty():
    # Arrange — no pre-conditions needed

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_get_activities_response_shape():
    # Arrange
    required_keys = {"description", "schedule", "max_participants", "participants"}

    # Act
    response = client.get("/activities")

    # Assert
    for activity in response.json().values():
        assert required_keys.issubset(activity.keys())


# ---------------------------------------------------------------------------
# POST /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_signup_valid():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert email in response.json()["message"]
    assert email in activities[activity_name]["participants"]


def test_signup_unknown_activity():
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate():
    # Arrange
    activity_name = "Chess Club"
    email = "duplicate@mergington.edu"
    activities[activity_name]["participants"].append(email)

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


# ---------------------------------------------------------------------------
# DELETE /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_unregister_valid():
    # Arrange
    activity_name = "Chess Club"
    email = "todelete@mergington.edu"
    activities[activity_name]["participants"].append(email)

    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert email not in activities[activity_name]["participants"]


def test_unregister_unknown_activity():
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_not_registered():
    # Arrange
    activity_name = "Chess Club"
    email = "notregistered@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not registered for this activity"
