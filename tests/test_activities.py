"""Tests for the activities endpoints."""

import pytest


def test_root_redirect(client):
    """Test that root path redirects to static index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_success(client):
    """Test successful retrieval of all activities."""
    response = client.get("/activities")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response is a dict of activities
    assert isinstance(data, dict)
    assert len(data) > 0
    
    # Verify Chess Club is in the response with correct structure
    assert "Chess Club" in data
    chess = data["Chess Club"]
    assert chess["description"] == "Learn strategies and compete in chess tournaments"
    assert chess["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
    assert chess["max_participants"] == 12
    assert isinstance(chess["participants"], list)


def test_activities_structure(client):
    """Test that all activities have required fields."""
    response = client.get("/activities")
    activities = response.json()
    
    required_fields = {"description", "schedule", "max_participants", "participants"}
    
    for activity_name, activity_data in activities.items():
        assert isinstance(activity_name, str), f"Activity name should be string: {activity_name}"
        assert isinstance(activity_data, dict), f"Activity data should be dict: {activity_data}"
        
        # Check all required fields exist
        actual_fields = set(activity_data.keys())
        assert required_fields.issubset(actual_fields), \
            f"Activity {activity_name} missing fields. Expected {required_fields}, got {actual_fields}"
        
        # Validate field types
        assert isinstance(activity_data["description"], str)
        assert isinstance(activity_data["schedule"], str)
        assert isinstance(activity_data["max_participants"], int)
        assert isinstance(activity_data["participants"], list)
        
        # Validate participants are emails (contain @)
        for participant in activity_data["participants"]:
            assert isinstance(participant, str)
            assert "@" in participant, f"Invalid email format: {participant}"


def test_activities_availability(client):
    """Test that availability calculation is correct."""
    response = client.get("/activities")
    activities = response.json()
    
    # Chess Club has 12 max, 2 participants, should have 10 spots left
    chess = activities["Chess Club"]
    spots_left = chess["max_participants"] - len(chess["participants"])
    assert spots_left == 10
    
    # Basketball Team has 15 max, 0 participants, should have 15 spots left
    basketball = activities["Basketball Team"]
    spots_left = basketball["max_participants"] - len(basketball["participants"])
    assert spots_left == 15


def test_activities_initial_participants(client):
    """Test that activities have correct initial participants."""
    response = client.get("/activities")
    activities = response.json()
    
    # Chess Club should have 2 participants
    assert len(activities["Chess Club"]["participants"]) == 2
    assert "michael@mergington.edu" in activities["Chess Club"]["participants"]
    assert "daniel@mergington.edu" in activities["Chess Club"]["participants"]
    
    # Basketball Team should have 0 participants
    assert len(activities["Basketball Team"]["participants"]) == 0
