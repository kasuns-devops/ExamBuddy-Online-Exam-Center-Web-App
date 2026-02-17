"""
Test the exam API endpoints
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_api():
    print("=" * 60)
    print("Testing ExamBuddy API Endpoints")
    print("=" * 60)
    
    # Test 1: Health check
    print("\n1️⃣ Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    assert response.status_code == 200, "Health check failed"
    print("   ✅ Health check passed")
    
    # Test 2: Start exam (without auth for now)
    print("\n2️⃣ Testing start exam endpoint...")
    exam_data = {
        "project_id": "demo-project-id",
        "mode": "test",  # Use test mode for immediate feedback
        "difficulty": "easy",
        "question_count": 5
    }
    
    # Note: This will fail without proper auth, but let's see the error
    try:
        response = requests.post(f"{BASE_URL}/api/exams/start", json=exam_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 401:
            print(f"   ⚠️  Authentication required (expected)")
            print(f"   Response: {response.json()}")
        elif response.status_code == 200:
            data = response.json()
            print(f"   ✅ Exam started successfully!")
            print(f"   Session ID: {data.get('session_id')}")
            print(f"   First question: {data.get('question', {}).get('question_text', 'N/A')[:50]}")
            return data.get('session_id')
        else:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("API Test Summary:")
    print("=" * 60)
    print("✅ Backend is running on http://localhost:8000")
    print("✅ Health endpoint works")
    print("⚠️  Exam endpoints require authentication")
    print("\nNext steps:")
    print("  1. Test frontend UI at http://localhost:5173")
    print("  2. Mock login and try starting an exam")
    print("=" * 60)

if __name__ == "__main__":
    test_api()
