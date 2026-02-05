#!/usr/bin/env python
"""
Test the complete authentication flow
Run this AFTER the backend is running to verify everything works
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "Test@123456"
TEST_FULL_NAME = "Test User"
TEST_COMPANY = "Test Company"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def test_health():
    """Test if backend is running"""
    print_section("1. Testing Backend Health")
    try:
        res = requests.get(f"{BASE_URL}/health", timeout=5)
        if res.status_code == 200:
            print(f"✓ Backend is running")
            print(f"  Response: {res.json()}")
            return True
        else:
            print(f"✗ Backend returned status {res.status_code}")
            return False
    except Exception as e:
        print(f"✗ Cannot connect to backend: {e}")
        print(f"  Make sure backend is running on {BASE_URL}")
        return False

def test_signup():
    """Test user registration"""
    print_section("2. Testing User Registration")
    
    payload = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "full_name": TEST_FULL_NAME,
        "company_name": TEST_COMPANY
    }
    
    try:
        res = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=payload,
            timeout=30,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {res.status_code}")
        data = res.json()
        
        if res.status_code == 200:
            print(f"✓ Registration successful")
            print(f"  User ID: {data['user']['id']}")
            print(f"  Email: {data['user']['email']}")
            print(f"  Token: {data['access_token'][:20]}...")
            return data['access_token']
        else:
            print(f"✗ Registration failed")
            print(f"  Error: {data.get('detail', 'Unknown error')}")
            return None
    except Exception as e:
        print(f"✗ Request failed: {e}")
        return None

def test_login():
    """Test user login"""
    print_section("3. Testing User Login")
    
    payload = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        res = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=payload,
            timeout=30,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {res.status_code}")
        data = res.json()
        
        if res.status_code == 200:
            print(f"✓ Login successful")
            print(f"  User ID: {data['user']['id']}")
            print(f"  Email: {data['user']['email']}")
            print(f"  Token: {data['access_token'][:20]}...")
            return data['access_token']
        else:
            print(f"✗ Login failed")
            print(f"  Error: {data.get('detail', 'Unknown error')}")
            return None
    except Exception as e:
        print(f"✗ Request failed: {e}")
        return None

def test_get_profile(token):
    """Test getting user profile"""
    print_section("4. Testing Get Profile")
    
    try:
        res = requests.get(
            f"{BASE_URL}/api/auth/me",
            timeout=30,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        print(f"Status: {res.status_code}")
        data = res.json()
        
        if res.status_code == 200:
            print(f"✓ Profile retrieved successfully")
            print(f"  User: {data['user']['full_name']}")
            print(f"  Email: {data['user']['email']}")
            return True
        else:
            print(f"✗ Failed to get profile")
            print(f"  Error: {data.get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"✗ Request failed: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("  FINANCIAL HEALTH PLATFORM - AUTH FLOW TEST")
    print("="*60)
    
    # Test health
    if not test_health():
        print("\n✗ Backend is not running!")
        print("Start backend with: python -m uvicorn app.main:app --reload")
        return
    
    # Test signup
    token = test_signup()
    if not token:
        print("\n✗ Signup failed!")
        return
    
    # Wait a moment
    time.sleep(1)
    
    # Test login
    login_token = test_login()
    if not login_token:
        print("\n✗ Login failed!")
        return
    
    # Test profile
    if not test_get_profile(login_token):
        print("\n✗ Profile retrieval failed!")
        return
    
    # Success
    print_section("✓✓✓ ALL TESTS PASSED ✓✓✓")
    print("\nThe authentication system is working correctly!")
    print("You can now use the frontend to login/signup.")

if __name__ == "__main__":
    main()
