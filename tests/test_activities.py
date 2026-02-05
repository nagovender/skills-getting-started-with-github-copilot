import pytest


class TestActivities:
    """Tests for the /activities endpoint"""

    def test_get_activities(self, client, reset_activities):
        """Test getting activities list"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Basketball Team" in data
        assert "Tennis Club" in data
        assert len(data) == 9

    def test_activities_structure(self, client, reset_activities):
        """Test activities have correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        activity = data["Basketball Team"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)

    def test_initial_participants(self, client, reset_activities):
        """Test initial participants are loaded correctly"""
        response = client.get("/activities")
        data = response.json()
        
        assert "james@mergington.edu" in data["Basketball Team"]["participants"]
        assert "alex@mergington.edu" in data["Tennis Club"]["participants"]


class TestSignup:
    """Tests for the signup endpoint"""

    def test_signup_success(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Basketball%20Team/signup?email=newstudent@mergington.edu",
            params={}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]

    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup actually adds the participant"""
        client.post(
            "/activities/Basketball%20Team/signup?email=newstudent@mergington.edu",
            params={}
        )
        
        response = client.get("/activities")
        data = response.json()
        assert "newstudent@mergington.edu" in data["Basketball Team"]["participants"]

    def test_signup_duplicate_student(self, client, reset_activities):
        """Test that duplicate signups are rejected"""
        response = client.post(
            "/activities/Basketball%20Team/signup?email=james@mergington.edu",
            params={}
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=student@mergington.edu",
            params={}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_multiple_activities(self, client, reset_activities):
        """Test that same student can signup for multiple activities"""
        email = "multistudent@mergington.edu"
        
        response1 = client.post(
            f"/activities/Basketball%20Team/signup?email={email}",
            params={}
        )
        response2 = client.post(
            f"/activities/Tennis%20Club/signup?email={email}",
            params={}
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        activities = client.get("/activities").json()
        assert email in activities["Basketball Team"]["participants"]
        assert email in activities["Tennis Club"]["participants"]


class TestUnregister:
    """Tests for the unregister endpoint"""

    def test_unregister_success(self, client, reset_activities):
        """Test successful unregister from an activity"""
        response = client.post(
            "/activities/Basketball%20Team/unregister?email=james@mergington.edu",
            params={}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Removed" in data["message"]
        assert "james@mergington.edu" in data["message"]

    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes the participant"""
        client.post(
            "/activities/Basketball%20Team/unregister?email=james@mergington.edu",
            params={}
        )
        
        response = client.get("/activities")
        data = response.json()
        assert "james@mergington.edu" not in data["Basketball Team"]["participants"]

    def test_unregister_not_registered(self, client, reset_activities):
        """Test unregister for student not registered"""
        response = client.post(
            "/activities/Basketball%20Team/unregister?email=notregistered@mergington.edu",
            params={}
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]

    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test unregister from non-existent activity"""
        response = client.post(
            "/activities/Nonexistent%20Activity/unregister?email=student@mergington.edu",
            params={}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_then_unregister(self, client, reset_activities):
        """Test signup followed by unregister"""
        email = "tempstudent@mergington.edu"
        
        # Sign up
        response1 = client.post(
            f"/activities/Basketball%20Team/signup?email={email}",
            params={}
        )
        assert response1.status_code == 200
        
        # Verify signed up
        activities = client.get("/activities").json()
        assert email in activities["Basketball Team"]["participants"]
        
        # Unregister
        response2 = client.post(
            f"/activities/Basketball%20Team/unregister?email={email}",
            params={}
        )
        assert response2.status_code == 200
        
        # Verify unregistered
        activities = client.get("/activities").json()
        assert email not in activities["Basketball Team"]["participants"]


class TestRoot:
    """Tests for the root endpoint"""

    def test_root_redirect(self, client, reset_activities):
        """Test that root redirects to static files"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
