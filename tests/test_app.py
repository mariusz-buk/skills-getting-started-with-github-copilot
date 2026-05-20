from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module
from src.app import app


@pytest.fixture(autouse=True)
def reset_activity_state():
    """Reset the in-memory activity state before and after each test."""
    original_activities = deepcopy(app_module.activities)
    yield
    app_module.activities = deepcopy(original_activities)


@pytest.fixture
def client():
    return TestClient(app)


def test_root_redirects_to_index(client):
    # Arrange
    url = "/"

    # Act
    response = client.get(url, follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_payload(client):
    # Arrange
    url = "/activities"

    # Act
    response = client.get(url)
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert isinstance(payload, dict)
    assert "Chess Club" in payload
    assert "Programming Class" in payload


def test_signup_for_activity_adds_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    url = f"/activities/{activity_name}/signup"
    params = {"email": email}

    # Act
    response = client.post(url, params=params)
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert payload == {"message": f"Signed up {email} for {activity_name}"}
    assert email in app_module.activities[activity_name]["participants"]


def test_signup_returns_404_for_unknown_activity(client):
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"
    url = f"/activities/{activity_name}/signup"
    params = {"email": email}

    # Act
    response = client.post(url, params=params)
    payload = response.json()

    # Assert
    assert response.status_code == 404
    assert payload["detail"] == "Activity not found"


def test_signup_returns_400_for_duplicate_participant(client):
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"
    url = f"/activities/{activity_name}/signup"
    params = {"email": existing_email}

    # Act
    response = client.post(url, params=params)
    payload = response.json()

    # Assert
    assert response.status_code == 400
    assert payload["detail"] == "Student already signed up for this activity"


def test_remove_participant_from_activity(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    url = f"/activities/{activity_name}/participants"
    params = {"email": email}

    # Act
    response = client.delete(url, params=params)
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert payload == {"message": f"Removed {email} from {activity_name}"}
    assert email not in app_module.activities[activity_name]["participants"]


def test_remove_participant_returns_404_for_unknown_activity(client):
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"
    url = f"/activities/{activity_name}/participants"
    params = {"email": email}

    # Act
    response = client.delete(url, params=params)
    payload = response.json()

    # Assert
    assert response.status_code == 404
    assert payload["detail"] == "Activity not found"


def test_remove_participant_returns_400_for_missing_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "absentstudent@mergington.edu"
    url = f"/activities/{activity_name}/participants"
    params = {"email": email}

    # Act
    response = client.delete(url, params=params)
    payload = response.json()

    # Assert
    assert response.status_code == 400
    assert payload["detail"] == "Participant not found in this activity"
