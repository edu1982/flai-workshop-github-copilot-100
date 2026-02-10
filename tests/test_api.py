"""
Test cases for the Mergington High School Activities API
"""
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    # Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball training and inter-school matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu", "liam@mergington.edu"]
        },
        "Swimming Club": {
            "description": "Swimming techniques and competitive training",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["ava@mergington.edu", "noah@mergington.edu"]
        },
        "Drama Club": {
            "description": "Acting, theater production, and performing arts",
            "schedule": "Wednesdays, 3:30 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["isabella@mergington.edu", "ethan@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and mixed media art projects",
            "schedule": "Thursdays, 3:00 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["mia@mergington.edu", "lucas@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop critical thinking and public speaking through debates",
            "schedule": "Fridays, 4:00 PM - 6:00 PM",
            "max_participants": 16,
            "participants": ["charlotte@mergington.edu", "william@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "Competitive science events and hands-on experiments",
            "schedule": "Tuesdays, 3:30 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["amelia@mergington.edu", "benjamin@mergington.edu"]
        }
    }
    
    # Reset to original state
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


class TestRootEndpoint:
    """Test cases for the root endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root path redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Test cases for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that all activities are returned"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Swimming Club" in data
    
    def test_get_activities_structure(self, client):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)


class TestSignupForActivity:
    """Test cases for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_successful(self, client):
        """Test successful signup for an activity"""
        response = client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "test@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "test@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_activity_not_found(self, client):
        """Test signup for non-existent activity"""
        response = client.post("/activities/Fake%20Activity/signup?email=test@mergington.edu")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]
    
    def test_signup_already_registered(self, client):
        """Test signing up when already registered"""
        # michael@mergington.edu is already in Chess Club
        response = client.post("/activities/Chess%20Club/signup?email=michael@mergington.edu")
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"]
    
    def test_signup_multiple_students(self, client):
        """Test signing up multiple students"""
        client.post("/activities/Drama%20Club/signup?email=student1@mergington.edu")
        client.post("/activities/Drama%20Club/signup?email=student2@mergington.edu")
        
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        participants = activities_data["Drama Club"]["participants"]
        
        assert "student1@mergington.edu" in participants
        assert "student2@mergington.edu" in participants


class TestUnregisterFromActivity:
    """Test cases for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_successful(self, client):
        """Test successful unregistration from an activity"""
        # michael@mergington.edu is in Chess Club
        response = client.delete("/activities/Chess%20Club/unregister?email=michael@mergington.edu")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "michael@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]
    
    def test_unregister_activity_not_found(self, client):
        """Test unregister from non-existent activity"""
        response = client.delete("/activities/Fake%20Activity/unregister?email=test@mergington.edu")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]
    
    def test_unregister_not_signed_up(self, client):
        """Test unregistering when not signed up"""
        response = client.delete("/activities/Chess%20Club/unregister?email=notregistered@mergington.edu")
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "not signed up" in data["detail"]
    
    def test_unregister_and_signup_again(self, client):
        """Test unregistering and then signing up again"""
        # Unregister
        response = client.delete("/activities/Programming%20Class/unregister?email=emma@mergington.edu")
        assert response.status_code == 200
        
        # Verify removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "emma@mergington.edu" not in activities_data["Programming Class"]["participants"]
        
        # Sign up again
        response = client.post("/activities/Programming%20Class/signup?email=emma@mergington.edu")
        assert response.status_code == 200
        
        # Verify added back
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "emma@mergington.edu" in activities_data["Programming Class"]["participants"]


class TestIntegrationScenarios:
    """Integration test scenarios"""
    
    def test_full_participant_lifecycle(self, client):
        """Test complete participant lifecycle: signup, verify, unregister"""
        email = "lifecycle@mergington.edu"
        activity = "Art Studio"
        
        # Initial state - not registered
        activities_response = client.get("/activities")
        initial_participants = activities_response.json()[activity]["participants"]
        assert email not in initial_participants
        
        # Sign up
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Verify signup
        activities_response = client.get("/activities")
        after_signup = activities_response.json()[activity]["participants"]
        assert email in after_signup
        assert len(after_signup) == len(initial_participants) + 1
        
        # Unregister
        unregister_response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert unregister_response.status_code == 200
        
        # Verify unregistration
        activities_response = client.get("/activities")
        after_unregister = activities_response.json()[activity]["participants"]
        assert email not in after_unregister
        assert len(after_unregister) == len(initial_participants)
