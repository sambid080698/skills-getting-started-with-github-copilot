"""Tests for the unsubscribe endpoint."""

import pytest


def test_unsubscribe_success(client):
    """Test successful unsubscribe from an activity."""
    # Sign up first
    client.post("/activities/Basketball Team/signup?email=test@mergington.edu")
    
    # Then unsubscribe
    response = client.post(
        "/activities/Basketball Team/unsubscribe?email=test@mergington.edu"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Unregistered" in data["message"]


def test_unsubscribe_removes_participant(client):
    """Test that unsubscribe actually removes the participant."""
    email = "test@mergington.edu"
    
    # Sign up
    client.post(f"/activities/Basketball Team/signup?email={email}")
    activities = client.get("/activities").json()
    assert email in activities["Basketball Team"]["participants"]
    
    # Unsubscribe
    client.post(f"/activities/Basketball Team/unsubscribe?email={email}")
    
    # Verify removed
    activities = client.get("/activities").json()
    assert email not in activities["Basketball Team"]["participants"]


def test_unsubscribe_nonregistered_user(client):
    """Test that unsubscribe for non-registered user returns 400."""
    response = client.post(
        "/activities/Basketball Team/unsubscribe?email=notregistered@mergington.edu"
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "not registered" in data["detail"].lower()


def test_unsubscribe_nonexistent_activity(client):
    """Test that unsubscribe for nonexistent activity returns 404."""
    response = client.post(
        "/activities/Nonexistent Club/unsubscribe?email=test@mergington.edu"
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_unsubscribe_preserves_other_participants(client):
    """Test that unsubscribe only removes specified participant."""
    # Chess Club has michael and daniel
    response = client.post(
        "/activities/Chess Club/unsubscribe?email=michael@mergington.edu"
    )
    
    assert response.status_code == 200
    
    # Verify only michael was removed
    activities = client.get("/activities").json()
    participants = activities["Chess Club"]["participants"]
    assert "michael@mergington.edu" not in participants
    assert "daniel@mergington.edu" in participants
    assert len(participants) == 1


def test_signup_then_unsubscribe_cycle(client):
    """Test sign up, unsubscribe, then sign up again cycle."""
    email = "cycle@mergington.edu"
    activity = "Art Club"
    
    # Sign up
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    
    activities = client.get("/activities").json()
    assert email in activities[activity]["participants"]
    
    # Unsubscribe
    response = client.post(f"/activities/{activity}/unsubscribe?email={email}")
    assert response.status_code == 200
    
    activities = client.get("/activities").json()
    assert email not in activities[activity]["participants"]
    
    # Sign up again
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    
    activities = client.get("/activities").json()
    assert email in activities[activity]["participants"]


def test_unsubscribe_then_signup_works(client):
    """Test that unsubscribing then subscribing to same activity works."""
    email = "bounce@mergington.edu"
    activity = "Drama Club"
    
    # Sign up
    client.post(f"/activities/{activity}/signup?email={email}")
    activities_1 = client.get("/activities").json()
    assert email in activities_1[activity]["participants"]
    
    # Unsubscribe
    client.post(f"/activities/{activity}/unsubscribe?email={email}")
    activities_2 = client.get("/activities").json()
    assert email not in activities_2[activity]["participants"]
    
    # Sign up again - should succeed
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    
    activities_3 = client.get("/activities").json()
    assert email in activities_3[activity]["participants"]


def test_unsubscribe_multiple_users(client):
    """Test unsubscribing multiple users from same activity."""
    activity = "Soccer Club"
    users = ["user1@mergington.edu", "user2@mergington.edu", "user3@mergington.edu"]
    
    # Sign up all users
    for user in users:
        client.post(f"/activities/{activity}/signup?email={user}")
    
    activities = client.get("/activities").json()
    assert len(activities[activity]["participants"]) == 3
    
    # Unsubscribe first two users
    for user in users[:2]:
        response = client.post(f"/activities/{activity}/unsubscribe?email={user}")
        assert response.status_code == 200
    
    # Verify only third user remains
    activities = client.get("/activities").json()
    assert len(activities[activity]["participants"]) == 1
    assert users[2] in activities[activity]["participants"]
