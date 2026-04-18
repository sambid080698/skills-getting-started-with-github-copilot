"""Tests for the signup endpoint."""

import pytest


def test_signup_success(client):
    """Test successful signup for an activity."""
    response = client.post(
        "/activities/Basketball Team/signup?email=newstudent@mergington.edu"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "newstudent@mergington.edu" in data["message"]
    assert "Basketball Team" in data["message"]


def test_signup_adds_participant(client):
    """Test that signup actually adds the participant to the activity."""
    # Verify Basketball Team is empty
    activities_before = client.get("/activities").json()
    assert len(activities_before["Basketball Team"]["participants"]) == 0
    
    # Sign up a student
    client.post("/activities/Basketball Team/signup?email=test@mergington.edu")
    
    # Verify participant was added
    activities_after = client.get("/activities").json()
    assert len(activities_after["Basketball Team"]["participants"]) == 1
    assert "test@mergington.edu" in activities_after["Basketball Team"]["participants"]


def test_signup_duplicate_rejected(client):
    """Test that duplicate signup is rejected."""
    # Try to sign up someone already registered
    response = client.post(
        "/activities/Chess Club/signup?email=michael@mergington.edu"
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"].lower()


def test_signup_nonexistent_activity(client):
    """Test that signup to nonexistent activity returns 404."""
    response = client.post(
        "/activities/Nonexistent Club/signup?email=test@mergington.edu"
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_signup_multiple_users(client):
    """Test signing up multiple users to the same activity."""
    activity = "Soccer Club"
    users = [
        "alice@mergington.edu",
        "bob@mergington.edu",
        "charlie@mergington.edu"
    ]
    
    # Sign up multiple users
    for user in users:
        response = client.post(f"/activities/{activity}/signup?email={user}")
        assert response.status_code == 200
    
    # Verify all were added
    activities = client.get("/activities").json()
    assert len(activities[activity]["participants"]) == 3
    for user in users:
        assert user in activities[activity]["participants"]


def test_signup_preserves_existing_participants(client):
    """Test that signup preserves existing participants."""
    # Chess Club has 2 existing participants
    response = client.post(
        "/activities/Chess Club/signup?email=newuser@mergington.edu"
    )
    
    assert response.status_code == 200
    
    # Verify all 3 participants exist
    activities = client.get("/activities").json()
    participants = activities["Chess Club"]["participants"]
    assert len(participants) == 3
    assert "michael@mergington.edu" in participants
    assert "daniel@mergington.edu" in participants
    assert "newuser@mergington.edu" in participants


def test_signup_responds_with_message(client):
    """Test that signup response contains helpful message."""
    email = "test@mergington.edu"
    activity = "Drama Club"
    
    response = client.post(f"/activities/{activity}/signup?email={email}")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    # Message should mention email and activity
    message = data["message"].lower()
    assert email.split("@")[0] in message or "signed up" in message
