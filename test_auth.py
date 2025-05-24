#!/usr/bin/env python3
"""
Quick test script to verify authentication endpoints work
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_register():
    """Test user registration"""
    print("🧪 Testing user registration...")
    
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=user_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 201
    except Exception as e:
        print(f"❌ Registration failed: {e}")
        return False

def test_login():
    """Test user login"""
    print("\n🧪 Testing user login...")
    
    login_data = {
        "username": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/token",
            data=login_data,  # Form data, not JSON
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {result}")
        
        if response.status_code == 200 and "access_token" in result:
            print("✅ Login successful!")
            return result["access_token"]
        else:
            print("❌ Login failed")
            return None
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return None

def test_protected_endpoint(token):
    """Test protected endpoint with token"""
    print("\n🧪 Testing protected endpoint...")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/v1/bots", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Protected endpoint test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting authentication tests...\n")
    
    # Test registration
    if test_register():
        print("✅ Registration passed")
        
        # Test login
        token = test_login()
        if token:
            print("✅ Login passed")
            
            # Test protected endpoint
            if test_protected_endpoint(token):
                print("✅ Protected endpoint passed")
                print("\n🎉 All authentication tests passed!")
            else:
                print("❌ Protected endpoint failed")
        else:
            print("❌ Login failed")
    else:
        print("❌ Registration failed")