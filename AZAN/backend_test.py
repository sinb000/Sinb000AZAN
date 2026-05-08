#!/usr/bin/env python3
"""
Backend API Testing for Prayer App (تطبيق الأذان)
Tests all Prayer Settings API endpoints
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://salah-alert-9.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def test_root_endpoint():
    """Test GET /api/ - Root endpoint"""
    print("🔍 Testing Root Endpoint...")
    try:
        response = requests.get(f"{API_BASE}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            if "message" in data and "أذان" in data["message"]:
                print("✅ Root endpoint working correctly")
                return True
            else:
                print("❌ Root endpoint response format incorrect")
                return False
        else:
            print(f"❌ Root endpoint failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Root endpoint error: {str(e)}")
        return False

def test_save_prayer_settings():
    """Test POST /api/prayer-settings - Save prayer settings"""
    print("\n🔍 Testing Save Prayer Settings...")
    
    # Test data as specified in the review request
    test_data = {
        "user_id": "test_user_123",
        "location": {
            "latitude": 24.7136,
            "longitude": 46.6753,
            "city": "الرياض"
        },
        "useGPS": True,
        "adjustments": {
            "fajr": 0,
            "dhuhr": 2,
            "asr": -1,
            "maghrib": 0,
            "isha": 3
        },
        "silentMode": {
            "fajr": False,
            "dhuhr": True,
            "asr": False,
            "maghrib": False,
            "isha": False
        },
        "audioSource": "radio"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/prayer-settings",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            # Verify all required fields are present
            required_fields = ["user_id", "location", "useGPS", "adjustments", "silentMode", "audioSource", "updated_at"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                # Verify data integrity
                if (data["user_id"] == test_data["user_id"] and
                    data["location"]["city"] == test_data["location"]["city"] and
                    data["adjustments"]["dhuhr"] == test_data["adjustments"]["dhuhr"] and
                    data["silentMode"]["dhuhr"] == test_data["silentMode"]["dhuhr"]):
                    print("✅ Save prayer settings working correctly")
                    return True, data
                else:
                    print("❌ Saved data doesn't match input data")
                    return False, None
            else:
                print(f"❌ Missing fields in response: {missing_fields}")
                return False, None
        else:
            print(f"❌ Save prayer settings failed with status {response.status_code}")
            return False, None
    except Exception as e:
        print(f"❌ Save prayer settings error: {str(e)}")
        return False, None

def test_get_prayer_settings(user_id):
    """Test GET /api/prayer-settings/{user_id} - Get prayer settings"""
    print(f"\n🔍 Testing Get Prayer Settings for user: {user_id}...")
    
    try:
        response = requests.get(f"{API_BASE}/prayer-settings/{user_id}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            if data["user_id"] == user_id:
                print("✅ Get prayer settings working correctly")
                return True, data
            else:
                print("❌ Retrieved user_id doesn't match requested user_id")
                return False, None
        else:
            print(f"❌ Get prayer settings failed with status {response.status_code}")
            return False, None
    except Exception as e:
        print(f"❌ Get prayer settings error: {str(e)}")
        return False, None

def test_update_prayer_settings():
    """Test updating existing prayer settings"""
    print("\n🔍 Testing Update Prayer Settings...")
    
    # Updated test data
    updated_data = {
        "user_id": "test_user_123",
        "location": {
            "latitude": 21.4225,
            "longitude": 39.8262,
            "city": "مكة المكرمة"
        },
        "useGPS": False,
        "adjustments": {
            "fajr": 2,
            "dhuhr": 0,
            "asr": 1,
            "maghrib": -1,
            "isha": 0
        },
        "silentMode": {
            "fajr": True,
            "dhuhr": False,
            "asr": True,
            "maghrib": False,
            "isha": True
        },
        "audioSource": "local"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/prayer-settings",
            json=updated_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            # Verify the update worked
            if (data["location"]["city"] == "مكة المكرمة" and
                data["useGPS"] == False and
                data["audioSource"] == "local" and
                data["adjustments"]["fajr"] == 2):
                print("✅ Update prayer settings working correctly")
                return True, data
            else:
                print("❌ Update didn't apply correctly")
                return False, None
        else:
            print(f"❌ Update prayer settings failed with status {response.status_code}")
            return False, None
    except Exception as e:
        print(f"❌ Update prayer settings error: {str(e)}")
        return False, None

def test_get_nonexistent_user():
    """Test error handling for non-existent user"""
    print("\n🔍 Testing Error Handling - Non-existent User...")
    
    try:
        response = requests.get(f"{API_BASE}/prayer-settings/nonexistent_user_999")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 404:
            data = response.json()
            if "detail" in data:
                print("✅ Error handling for non-existent user working correctly")
                return True
            else:
                print("❌ Error response format incorrect")
                return False
        else:
            print(f"❌ Expected 404 status code, got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error handling test error: {str(e)}")
        return False

def main():
    """Run all backend API tests"""
    print("=" * 60)
    print("🕌 Prayer App Backend API Testing")
    print("=" * 60)
    
    test_results = []
    
    # Test 1: Root endpoint
    result1 = test_root_endpoint()
    test_results.append(("Root Endpoint", result1))
    
    # Test 2: Save prayer settings
    result2, saved_data = test_save_prayer_settings()
    test_results.append(("Save Prayer Settings", result2))
    
    # Test 3: Get prayer settings (only if save worked)
    if result2:
        result3, retrieved_data = test_get_prayer_settings("test_user_123")
        test_results.append(("Get Prayer Settings", result3))
        
        # Test 4: Update prayer settings (only if get worked)
        if result3:
            result4, updated_data = test_update_prayer_settings()
            test_results.append(("Update Prayer Settings", result4))
            
            # Verify the update by getting again
            if result4:
                result5, final_data = test_get_prayer_settings("test_user_123")
                test_results.append(("Verify Update", result5))
    
    # Test 5: Error handling
    result6 = test_get_nonexistent_user()
    test_results.append(("Error Handling", result6))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All backend API tests passed!")
        return True
    else:
        print("⚠️  Some backend API tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)