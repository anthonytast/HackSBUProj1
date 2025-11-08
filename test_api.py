"""
Example script demonstrating how to use the Study Planner API
"""

import requests
import json
from datetime import datetime, timedelta

# API base URL
BASE_URL = "http://localhost:8000"


def test_health_check():
    """Test the health check endpoint"""
    print("\n=== Testing Health Check ===")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_canvas_auth():
    """Test Canvas authentication"""
    print("\n=== Testing Canvas Authentication ===")
    
    # Replace with your actual Canvas credentials
    data = {
        "canvas_url": "https://your-institution.instructure.com",
        "access_token": "your_canvas_token_here"
    }
    
    response = requests.post(f"{BASE_URL}/canvas/authenticate", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_fetch_assignments():
    """Test fetching Canvas assignments"""
    print("\n=== Testing Fetch Assignments ===")
    
    response = requests.get(f"{BASE_URL}/canvas/assignments")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Found {data['count']} assignments")
        if data['assignments']:
            print(f"\nFirst assignment:")
            print(json.dumps(data['assignments'][0], indent=2, default=str))
    else:
        print(f"Error: {response.json()}")
    
    return response.status_code == 200


def test_generate_study_plan():
    """Test generating a study plan with sample data"""
    print("\n=== Testing Study Plan Generation ===")
    
    # Sample assignment data
    sample_assignments = [
        {
            "id": 1,
            "title": "Math Problem Set 3",
            "description": "Complete problems 1-15 from Chapter 4",
            "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "course_name": "Calculus II",
            "course_id": 101,
            "assignment_type": "problem_set",
            "points": 100.0
        },
        {
            "id": 2,
            "title": "Physics Lab Report",
            "description": "Write up findings from projectile motion experiment",
            "due_date": (datetime.now() + timedelta(days=5)).isoformat(),
            "course_name": "Physics 101",
            "course_id": 102,
            "assignment_type": "paper",
            "points": 50.0
        }
    ]
    
    # User preferences
    preferences = {
        "study_session_length": 90,
        "break_frequency": 25,
        "daily_study_hours": 4,
        "preferred_study_times": ["09:00-12:00", "14:00-17:00"],
        "buffer_days": 1,
        "weekend_study": True
    }
    
    data = {
        "assignments": sample_assignments,
        "preferences": preferences
    }
    
    response = requests.post(f"{BASE_URL}/study-plan/generate", json=data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nGenerated {result['task_count']} tasks")
        print(f"Total study time: {result['study_plan']['total_study_time']} minutes")
        
        if result['study_plan']['tasks']:
            print(f"\nFirst task:")
            print(json.dumps(result['study_plan']['tasks'][0], indent=2))
    else:
        print(f"Error: {response.json()}")
    
    return response.status_code == 200


def test_complete_pipeline():
    """Test the complete study plan pipeline"""
    print("\n=== Testing Complete Pipeline ===")
    print("This will:")
    print("1. Fetch assignments from Canvas")
    print("2. Generate AI study plan")
    print("3. Create Google Calendar events")
    
    response = requests.post(f"{BASE_URL}/study-plan/complete")
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nResults:")
        print(f"- Assignments processed: {result['assignments_processed']}")
        print(f"- Tasks generated: {result['tasks_generated']}")
        print(f"- Events created: {result['events_created']}")
    else:
        print(f"Error: {response.json()}")
    
    return response.status_code == 200


def main():
    """Run all tests"""
    print("=" * 60)
    print("Study Planner API Test Suite")
    print("=" * 60)
    
    print("\nMake sure the API server is running on http://localhost:8000")
    print("You can start it with: python main.py")
    
    input("\nPress Enter to continue...")
    
    # Run tests
    results = {
        "Health Check": test_health_check(),
        "Canvas Auth": False,  # Skipping as it requires credentials
        "Fetch Assignments": False,  # Skipping as it requires auth
        "Generate Study Plan": test_generate_study_plan(),
        "Complete Pipeline": False  # Skipping as it requires full setup
    }
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ SKIPPED/FAILED"
        print(f"{test_name}: {status}")
    
    print("\n" + "=" * 60)
    print("\nTo test Canvas and Google Calendar integration:")
    print("1. Set up your .env file with credentials")
    print("2. Authenticate with Canvas: POST /canvas/authenticate")
    print("3. Authenticate with Google: POST /google/authenticate")
    print("4. Run complete pipeline: POST /study-plan/complete")
    print("\nVisit http://localhost:8000/docs for interactive API documentation")


if __name__ == "__main__":
    main()
