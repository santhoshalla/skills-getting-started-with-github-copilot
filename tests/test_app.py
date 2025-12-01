from fastapi.testclient import TestClient
import pytest

from src import app as app_module

client = TestClient(app_module.app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # expect several known activities
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"], dict)


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    test_email = "testuser+ci@example.com"

    activities = app_module.activities
    # Snapshot original participants to restore later
    original = list(activities[activity]["participants"])

    # Ensure test email not present
    if test_email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(test_email)

    # Signup
    resp = client.post(f"/activities/{activity}/signup?email={test_email}")
    assert resp.status_code == 200
    j = resp.json()
    assert "Signed up" in j.get("message", "")

    # Confirm via GET that participant is present
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert test_email in data[activity]["participants"]

    # Unregister
    resp = client.delete(f"/activities/{activity}/participants?email={test_email}")
    assert resp.status_code == 200
    j = resp.json()
    assert "Unregistered" in j.get("message", "")

    # Confirm removed
    resp = client.get("/activities")
    data = resp.json()
    assert test_email not in data[activity]["participants"]

    # Restore original participants (defensive)
    activities[activity]["participants"] = original
