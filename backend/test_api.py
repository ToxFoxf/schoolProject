#!/usr/bin/env python
"""
Test script for Save Food FastAPI Backend
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000/api"

def test_health():
    """Test health endpoint"""
    print("\n🏥 Testing health endpoint...")
    response = requests.get("http://127.0.0.1:5000/health")
    if response.status_code == 200:
        print(f"✓ Health check: {response.json()['status']}")
        return True
    return False

def test_registration():
    """Test user registration"""
    print("\n👤 Testing user registration...")
    payload = {
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "testpass123",
        "role": "Donor"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=payload)
    if response.status_code == 200:
        data = response.json()
        print(f"✓ User registered: {data['user']['email']}")
        return data['token']
    else:
        print(f"✗ Registration failed: {response.text}")
        return None

def test_login():
    """Test user login"""
    print("\n🔑 Testing login...")
    payload = {
        "email": "donor@example.com",
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=payload)
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Login successful: {data['user']['name']}")
        print(f"✓ Token: {data['token'][:20]}...")
        return data['token']
    else:
        print(f"✗ Login failed: {response.text}")
        return None

def test_get_profile(token):
    """Test getting user profile"""
    print("\n👤 Testing get profile...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    if response.status_code == 200:
        user = response.json()
        print(f"✓ Profile retrieved: {user['name']} ({user['role']})")
        return True
    else:
        print(f"✗ Get profile failed: {response.text}")
        return False

def test_get_projects(token):
    """Test getting projects"""
    print("\n📋 Testing get projects...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/projects", headers=headers)
    if response.status_code == 200:
        projects = response.json()
        print(f"✓ Projects retrieved: {len(projects)} projects found")
        if projects:
            print(f"  - First project: {projects[0]['name']}")
        return True
    else:
        print(f"✗ Get projects failed: {response.text}")
        return False

def test_get_issues(token):
    """Test getting issues"""
    print("\n🐛 Testing get issues...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/issues", headers=headers)
    if response.status_code == 200:
        issues = response.json()
        print(f"✓ Issues retrieved: {len(issues)} issues found")
        if issues:
            print(f"  - First issue: {issues[0]['title']}")
        return True
    else:
        print(f"✗ Get issues failed: {response.text}")
        return False

def test_get_notifications(token):
    """Test getting notifications"""
    print("\n🔔 Testing get notifications...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/notifications", headers=headers)
    if response.status_code == 200:
        notifications = response.json()
        print(f"✓ Notifications retrieved: {len(notifications)} notifications found")
        return True
    else:
        print(f"✗ Get notifications failed: {response.text}")
        return False

def main():
    print("=" * 60)
    print("🍗 Save Food API - Backend Test Suite")
    print("=" * 60)
    
    try:
        # Test health
        if not test_health():
            print("\n✗ Server is not running. Start it first.")
            return
        
        # Give server a moment
        time.sleep(1)
        
        # Test login
        token = test_login()
        if not token:
            print("\n✗ Could not get authentication token")
            return
        
        # Test endpoints
        test_get_profile(token)
        test_get_projects(token)
        test_get_issues(token)
        test_get_notifications(token)
        
        # Test registration
        test_registration()
        
        print("\n" + "=" * 60)
        print("✓ All tests completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("Make sure the FastAPI server is running on http://127.0.0.1:5000")

if __name__ == "__main__":
    main()
