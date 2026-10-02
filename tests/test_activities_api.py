import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def api_client(monkeypatch):
    test_activities = {
        "Chess Club": {
            "description": "Learn chess",
            "schedule": "Fridays",
            "max_participants": 4,
            "participants": ["sam@example.com"],
        }
    }
    monkeypatch.setattr(app_module, "activities", test_activities)

    with TestClient(app_module.app) as client:
        yield client, test_activities


def test_get_activities_returns_activity_data(api_client):
    # Arrange
    client, expected_activities = api_client

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_adds_participant(api_client):
    # Arrange
    client, activities = api_client
    activity_name = "Chess Club"
    email = "alex@example.com"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_rejects_duplicate_participant(api_client):
    # Arrange
    client, activities = api_client
    activity_name = "Chess Club"
    email = "sam@example.com"
    original_participants = activities[activity_name]["participants"].copy()

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student is already signed up for this activity"
    }
    assert activities[activity_name]["participants"] == original_participants


def test_signup_rejects_unknown_activity(api_client):
    # Arrange
    client, _ = api_client

    # Act
    response = client.post(
        "/activities/Unknown%20Activity/signup",
        params={"email": "alex@example.com"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_participant(api_client):
    # Arrange
    client, activities = api_client
    activity_name = "Chess Club"
    email = "sam@example.com"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_unregister_rejects_missing_participant(api_client):
    # Arrange
    client, activities = api_client
    activity_name = "Chess Club"
    email = "missing@example.com"
    original_participants = activities[activity_name]["participants"].copy()

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }
    assert activities[activity_name]["participants"] == original_participants


def test_unregister_rejects_unknown_activity(api_client):
    # Arrange
    client, _ = api_client

    # Act
    response = client.delete(
        "/activities/Unknown%20Activity/signup",
        params={"email": "sam@example.com"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}