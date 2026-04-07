import copy
import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)
DEFAULT_ACTIVITIES = copy.deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activity store before each test."""
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(DEFAULT_ACTIVITIES))
    yield
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(DEFAULT_ACTIVITIES))


def test_root_redirects_to_static_index():
    # Arrange
    url = "/"

    # Act
    response = client.get(url, follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activities():
    # Arrange
    url = "/activities"

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == 200
    assert response.json() == DEFAULT_ACTIVITIES


def test_signup_for_activity_adds_new_participant():
    # Arrange
    activity_name = "Chess Club"
    new_email = "newstudent@mergington.edu"
    url = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(url, params={"email": new_email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {new_email} for {activity_name}"}
    assert new_email in app_module.activities[activity_name]["participants"]


def test_signup_missing_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Club"
    url = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(url, params={"email": "student@mergington.edu"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_email_returns_400():
    # Arrange
    activity_name = "Chess Club"
    duplicate_email = DEFAULT_ACTIVITIES[activity_name]["participants"][0]
    url = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(url, params={"email": duplicate_email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_removes_existing_participant():
    # Arrange
    activity_name = "Chess Club"
    participant_email = DEFAULT_ACTIVITIES[activity_name]["participants"][0]
    url = f"/activities/{activity_name}/participants"

    # Act
    response = client.delete(url, params={"email": participant_email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {participant_email} from {activity_name}"}
    assert participant_email not in app_module.activities[activity_name]["participants"]


def test_remove_nonexistent_participant_returns_404():
    # Arrange
    activity_name = "Chess Club"
    url = f"/activities/{activity_name}/participants"

    # Act
    response = client.delete(url, params={"email": "unknown@mergington.edu"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_remove_from_missing_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Club"
    url = f"/activities/{activity_name}/participants"

    # Act
    response = client.delete(url, params={"email": "student@mergington.edu"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
