from fastapi.testclient import TestClient
import src.app as app_module
from copy import deepcopy
import pytest


@pytest.fixture(autouse=True)
def client():
    # snapshot and restore the in-memory activities to avoid test interdependence
    original = deepcopy(app_module.activities)
    client = TestClient(app_module.app)
    yield client
    app_module.activities = original


def test_get_activities(client):
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Tennis Club" in data


def test_signup_and_unregister_flow(client):
    activity = "Tennis Club"
    email = "test_student@example.com"

    # Signup
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # Check participant present
    data = client.get("/activities").json()
    assert email in data[activity]["participants"]

    # Unregister
    resp = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert resp.status_code == 200
    assert "Unregistered" in resp.json().get("message", "")

    # Ensure removed
    data = client.get("/activities").json()
    assert email not in data[activity]["participants"]


def test_duplicate_signup_returns_400(client):
    activity = "Tennis Club"
    existing = "alex@mergington.edu"
    resp = client.post(f"/activities/{activity}/signup?email={existing}")
    assert resp.status_code == 400


def test_unregister_nonexistent_returns_404(client):
    activity = "Tennis Club"
    missing = "doesnotexist@example.com"
    resp = client.delete(f"/activities/{activity}/unregister?email={missing}")
    assert resp.status_code == 404
