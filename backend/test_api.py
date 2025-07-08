#!/usr/bin/env python3
"""
Test script for the FastAPI endpoints
"""

import asyncio
import requests
import json
from datetime import datetime

# Test data
SAMPLE_POLICY = """
Data Collection and Usage

We collect personal information when you create an account, including your name, email address, and phone number. We also collect behavioral data such as your browsing history, search queries, and interaction patterns with our service. This information is used to personalize your experience, improve our services, and for marketing purposes.

Third-Party Sharing

Your data may be shared with third-party partners for advertising and analytics purposes. We may also share information with service providers who help us operate our platform.

User Rights

You have the right to access, modify, or delete your personal information at any time by contacting our support team. You can also opt out of marketing communications and request data portability.

Data Security

We implement industry-standard security measures to protect your data, including encryption and access controls. However, no method of transmission over the internet is 100% secure.

Cookies and Tracking

We use cookies and similar technologies to track your activity on our website and remember your preferences. You can control cookie settings through your browser.
"""

BASE_URL = "http://127.0.0.1:8000"

def test_health_endpoint():
    """Test the health check endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed")
            print(f"   Status: {data['status']}")
            print(f"   LLM Service: {data['llm_service']['status']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server. Is it running?")
        print("   Start with: python main.py")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_root_endpoint():
    """Test the root endpoint"""
    print("\n🔍 Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Root endpoint working")
            print(f"   Message: {data['message']}")
            return True
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
        return False

def test_models_endpoint():
    """Test the models endpoint"""
    print("\n🔍 Testing models endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/models")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Models endpoint working")
            print(f"   Primary Model: {data['primary_model']}")
            print(f"   Secondary Model: {data['secondary_model']}")
            return True
        else:
            print(f"❌ Models endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Models endpoint error: {e}")
        return False

def test_policy_processing():
    """Test the main policy processing endpoint"""
    print("\n🔍 Testing policy processing endpoint...")
    
    payload = {
        "company_name": "Test Company",
        "policy_title": "Test Privacy Policy",
        "policy_content": SAMPLE_POLICY,
        "version": "1.0",
        "max_chunk_size": 2000
    }
    
    print(f"📄 Sending policy content ({len(SAMPLE_POLICY)} characters)")
    
    try:
        response = requests.post(
            f"{BASE_URL}/analyze-policy",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=120  # Allow time for LLM processing
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Policy processing successful!")
            print(f"   Processing ID: {data['processing_id']}")
            print(f"   Processing Time: {data['processing_time']:.2f}s")
            print(f"   Sections Processed: {len(data['document']['sections'])}")
            print(f"   UI Components Generated: {len(data['ui_components'])}")
            print(f"   Overall Risk: {data['document']['overall_risk_level']}")
            print(f"   User Friendliness: {data['document']['user_friendliness_score']}/5")
            
            # Show component types
            component_types = [comp['type'] for comp in data['ui_components']]
            print(f"   Component Types: {', '.join(set(component_types))}")
            
            # Show first component details
            if data['ui_components']:
                first_comp = data['ui_components'][0]
                print(f"\n📋 First Component Preview:")
                print(f"   Type: {first_comp['type']}")
                print(f"   Priority: {first_comp['priority']}")
                print(f"   Title: {first_comp['content']['title']}")
                print(f"   Risk Level: {first_comp['content']['risk_level']}")
                
            return True
        else:
            print(f"❌ Policy processing failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timeout (LLM processing takes time)")
        return False
    except Exception as e:
        print(f"❌ Policy processing error: {e}")
        return False

def test_invalid_requests():
    """Test error handling with invalid requests"""
    print("\n🔍 Testing error handling...")
    
    # Test empty content
    try:
        payload = {
            "company_name": "Test Company",
            "policy_content": "Short"  # Too short
        }
        
        response = requests.post(
            f"{BASE_URL}/analyze-policy",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            print("✅ Error handling working (short content rejected)")
            return True
        else:
            print(f"❌ Expected 400 error, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def main():
    """Run all API tests"""
    print("🚀 Starting API Tests")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health_endpoint),
        ("Root Endpoint", test_root_endpoint), 
        ("Models Endpoint", test_models_endpoint),
        ("Error Handling", test_invalid_requests),
        ("Policy Processing", test_policy_processing),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔥 Running {test_name} Test...")
        try:
            result = test_func()
            results.append((test_name, result))
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status}")
        except Exception as e:
            print(f"❌ {test_name} Test: ERROR - {str(e)}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All API tests passed! The API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        print("\nTroubleshooting:")
        print("1. Make sure the API server is running: python main.py")
        print("2. Check your .env file has OPENAI_API_KEY set")
        print("3. Verify your LiteLLM proxy is accessible")

if __name__ == "__main__":
    main() 