from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities as activities_data


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = deepcopy(activities_data)
    yield
    activities_data.clear()
    activities_data.update(original_activities)


@pytest.fixture
def client():
    return TestClient(app)


def test_root_redirects_to_static_index(client):
    # Arrange
    url = "/"

    # Act
    response = client.get(url, follow_redirects=False)

    # Assert
    assert response.status_code in (307, 308)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activities(client):
    # Arrange
    url = "/activities"

    # Act
    response = client.get(url)
    result = response.json()

    # Assert
    assert response.status_code == 200
    assert isinstance(result, dict)
    assert "Chess Club" in result
    assert result["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"


def test_signup_for_activity_success(client):
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    url = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(url, params={"email": email})
    result = response.json()

    # Assert
    assert response.status_code == 200
    assert result["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities_data[activity_name]["participants"]


def test_signup_for_activity_duplicate_returns_400(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    url = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(url, params={"email": email})
    result = response.json()

    # Assert
    assert response.status_code == 400
    assert result["detail"] == "Student is already signed up for this activity"


def test_signup_for_activity_nonexistent_returns_404(client):
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"
    url = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(url, params={"email": email})
    result = response.json()

    # Assert
    assert response.status_code == 404
    assert result["detail"] == "Activity not found"


def test_unregister_from_activity_success(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    url = f"/activities/{activity_name}/signup"

    # Act
    response = client.delete(url, params={"email": email})
    result = response.json()

    # Assert
    assert response.status_code == 200
    assert result["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in activities_data[activity_name]["participants"]


def test_unregister_from_activity_not_signed_up_returns_400(client):
    # Arrange
    activity_name = "Chess Club"
    email = "notregistered@mergington.edu"
    url = f"/activities/{activity_name}/signup"

    # Act
    response = client.delete(url, params={"email": email})
    result = response.json()

    # Assert
    assert response.status_code == 400
    assert result["detail"] == "Student is not signed up for this activity"


def test_unregister_from_activity_nonexistent_returns_404(client):
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"
    url = f"/activities/{activity_name}/signup"

    # Act
    response = client.delete(url, params={"email": email})
    result = response.json()

    # Assert
    assert response.status_code == 404
    assert result["detail"] == "Activity not found"
