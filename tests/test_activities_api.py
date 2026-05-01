"""
FastAPI Integration Tests for Activity Management System

Tests follow the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up the test data/state
- Act: Call the API endpoint
- Assert: Verify the response and behavior
"""

import pytest
from fastapi.testclient import TestClient


class TestRootEndpoint:
    """Tests for GET / endpoint (redirect to static files)"""

    def test_root_redirects_to_static_index(self, client):
        """
        Arrange: No setup needed, testing root endpoint
        Act: Make GET request to /
        Assert: Should redirect (307 or 308) to /static/index.html
        """
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code in [307, 308]
        assert "static/index.html" in response.headers.get("location", "")


class TestGetActivitiesEndpoint:
    """Tests for GET /activities endpoint"""

    def test_get_all_activities_returns_200(self, client):
        """
        Arrange: TestClient is ready with default activities
        Act: Make GET request to /activities
        Assert: Should return 200 OK with all activities
        """
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)

    def test_get_all_activities_contains_all_nine_activities(self, client):
        """
        Arrange: TestClient is ready with default activities
        Act: Make GET request to /activities
        Assert: Should return all 9 activities
        """
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class", "Basketball Team",
            "Soccer Club", "Art Club", "Drama Club", "Debate Club", "Science Club"
        ]
        assert len(activities) == 9
        for activity_name in expected_activities:
            assert activity_name in activities

    def test_get_all_activities_has_correct_structure(self, client):
        """
        Arrange: TestClient is ready with default activities
        Act: Make GET request to /activities
        Assert: Each activity should have expected fields
        """
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data, dict)
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_get_all_activities_includes_initial_participants(self, client):
        """
        Arrange: TestClient is ready with default activities
        Act: Make GET request to /activities
        Assert: Activities should have initial participant data
        """
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        chess_club = activities["Chess Club"]
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success_adds_participant(self, client):
        """
        Arrange: Prepare email and activity name
        Act: Make POST request to signup endpoint
        Assert: Should return 200 and participant should be added
        """
        # Arrange
        activity_name = "Chess Club"
        new_email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert new_email in activities[activity_name]["participants"]

    def test_signup_missing_email_returns_400(self, client):
        """
        Arrange: Prepare activity name without email parameter
        Act: Make POST request to signup endpoint without email
        Assert: Should return 422 (FastAPI validation error)
        """
        # Arrange
        activity_name = "Chess Club"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup")
        
        # Assert
        assert response.status_code == 422

    def test_signup_invalid_activity_returns_404(self, client):
        """
        Arrange: Prepare non-existent activity name and valid email
        Act: Make POST request to signup for non-existent activity
        Assert: Should return 404 not found
        """
        # Arrange
        invalid_activity = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_duplicate_returns_400(self, client):
        """
        Arrange: Pick existing participant from an activity
        Act: Try to sign up same email twice
        Assert: Should return 400 - already signed up
        """
        # Arrange
        activity_name = "Chess Club"
        duplicate_email = "michael@mergington.edu"  # Already in Chess Club
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": duplicate_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_allows_same_email_different_activities(self, client):
        """
        Arrange: Prepare email and two different activities
        Act: Sign up same email for different activities
        Assert: Should allow it (same student can be in multiple activities)
        """
        # Arrange
        email = "versatile@mergington.edu"
        activity1 = "Chess Club"
        activity2 = "Programming Class"
        
        # Act: Sign up for first activity
        response1 = client.post(
            f"/activities/{activity1}/signup",
            params={"email": email}
        )
        # Sign up for second activity
        response2 = client.post(
            f"/activities/{activity2}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify in both activities
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity1]["participants"]
        assert email in activities[activity2]["participants"]


class TestRemoveParticipantEndpoint:
    """Tests for DELETE /activities/{activity_name}/participants endpoint"""

    def test_remove_participant_success(self, client):
        """
        Arrange: First add a participant, then remove them
        Act: Make DELETE request to remove endpoint
        Assert: Should return 200 and participant should be removed
        """
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email_to_remove}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email_to_remove not in activities[activity_name]["participants"]

    def test_remove_participant_missing_email_returns_422(self, client):
        """
        Arrange: Prepare activity name without email parameter
        Act: Make DELETE request without email
        Assert: Should return 422 (FastAPI validation error)
        """
        # Arrange
        activity_name = "Chess Club"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/participants")
        
        # Assert
        assert response.status_code == 422

    def test_remove_participant_invalid_activity_returns_404(self, client):
        """
        Arrange: Prepare non-existent activity and valid email
        Act: Make DELETE request for non-existent activity
        Assert: Should return 404 not found
        """
        # Arrange
        invalid_activity = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{invalid_activity}/participants",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_remove_nonexistent_participant_returns_400(self, client):
        """
        Arrange: Try to remove email that's not in the activity
        Act: Make DELETE request for non-registered participant
        Assert: Should return 400 - not registered
        """
        # Arrange
        activity_name = "Chess Club"
        non_registered_email = "notregistered@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": non_registered_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_remove_participant_then_readd(self, client):
        """
        Arrange: Remove a participant, then sign them up again
        Act: DELETE then POST
        Assert: Both operations should succeed
        """
        # Arrange
        activity_name = "Basketball Team"
        email = "alex@mergington.edu"
        
        # Act: Remove participant
        remove_response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Act: Sign them back up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert remove_response.status_code == 200
        assert signup_response.status_code == 200
        
        # Verify participant is in activity
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]


class TestIntegrationScenarios:
    """Integration tests with complex multi-step scenarios"""

    def test_complete_user_journey(self, client):
        """
        Arrange: Set up initial state
        Act: User flow - view activities, sign up, remove self
        Assert: State changes correctly at each step
        """
        # Arrange & Act: Get initial activities
        initial_response = client.get("/activities")
        assert initial_response.status_code == 200
        initial_activities = initial_response.json()
        initial_soccer_count = len(initial_activities["Soccer Club"]["participants"])
        
        # Act: User signs up for Soccer Club
        email = "newuser@mergington.edu"
        signup_response = client.post(
            "/activities/Soccer Club/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        # Assert: Verify signup worked
        check_response = client.get("/activities")
        activities = check_response.json()
        assert email in activities["Soccer Club"]["participants"]
        assert len(activities["Soccer Club"]["participants"]) == initial_soccer_count + 1
        
        # Act: User removes themselves
        remove_response = client.delete(
            "/activities/Soccer Club/participants",
            params={"email": email}
        )
        assert remove_response.status_code == 200
        
        # Assert: Verify removal worked
        final_response = client.get("/activities")
        final_activities = final_response.json()
        assert email not in final_activities["Soccer Club"]["participants"]
        assert len(final_activities["Soccer Club"]["participants"]) == initial_soccer_count

    def test_multiple_users_different_activities(self, client):
        """
        Arrange: Two users with different activities
        Act: Both users sign up for different activities
        Assert: Both should succeed and not interfere with each other
        """
        # Arrange
        user1_email = "user1@mergington.edu"
        user2_email = "user2@mergington.edu"
        
        # Act: User 1 signs up for Art Club
        response1 = client.post(
            "/activities/Art Club/signup",
            params={"email": user1_email}
        )
        
        # Act: User 2 signs up for Drama Club
        response2 = client.post(
            "/activities/Drama Club/signup",
            params={"email": user2_email}
        )
        
        # Assert: Both succeeded
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Assert: Verify correct assignments
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert user1_email in activities["Art Club"]["participants"]
        assert user1_email not in activities["Drama Club"]["participants"]
        assert user2_email in activities["Drama Club"]["participants"]
        assert user2_email not in activities["Art Club"]["participants"]
