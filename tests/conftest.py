"""
Pytest configuration and fixtures for FastAPI activity management system tests.

Provides:
- client: TestClient fixture for making HTTP requests to the app
- reset_activities: Fixture that resets the in-memory activities database to initial state
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


# Store the initial state of activities when the test module is loaded
INITIAL_ACTIVITIES = {
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
        "description": "Practice and compete in basketball games",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
        "max_participants": 15,
        "participants": ["alex@mergington.edu"]
    },
    "Soccer Club": {
        "description": "Train and play soccer matches",
        "schedule": "Wednesdays and Saturdays, 3:00 PM - 5:00 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "ava@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore painting, drawing, and other visual arts",
        "schedule": "Mondays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": ["isabella@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act in plays and learn theater skills",
        "schedule": "Thursdays, 4:00 PM - 6:00 PM",
        "max_participants": 20,
        "participants": ["mason@mergington.edu", "charlotte@mergington.edu"]
    },
    "Debate Club": {
        "description": "Develop argumentation and public speaking skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 16,
        "participants": ["ethan@mergington.edu"]
    },
    "Science Club": {
        "description": "Conduct experiments and explore scientific concepts",
        "schedule": "Tuesdays, 3:00 PM - 4:30 PM",
        "max_participants": 25,
        "participants": ["harper@mergington.edu", "logan@mergington.edu"]
    }
}


@pytest.fixture
def reset_activities():
    """
    Fixture that resets the activities database to its initial state.
    
    Runs before each test to ensure a clean state and no test interference.
    """
    # Clear and repopulate with initial data
    activities.clear()
    activities.update({
        key: {
            'description': value['description'],
            'schedule': value['schedule'],
            'max_participants': value['max_participants'],
            'participants': value['participants'].copy()
        }
        for key, value in INITIAL_ACTIVITIES.items()
    })
    yield
    # Cleanup after test (optional, but good practice)
    activities.clear()
    activities.update({
        key: {
            'description': value['description'],
            'schedule': value['schedule'],
            'max_participants': value['max_participants'],
            'participants': value['participants'].copy()
        }
        for key, value in INITIAL_ACTIVITIES.items()
    })


@pytest.fixture
def client(reset_activities):
    """
    Fixture that provides a TestClient for making HTTP requests to the FastAPI app.
    
    Depends on reset_activities fixture to ensure app state is fresh for each test.
    """
    return TestClient(app)
