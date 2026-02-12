#!/usr/bin/env python3
"""
TalentDog API Test Suite
Run this script to verify all backend endpoints are working correctly
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def color_print(color, message):
    colors = {
        'green': '\033[92m',
        'red': '\033[91m',
        'blue': '\033[94m',
        'yellow': '\033[93m',
        'end': '\033[0m'
    }
    print(f"{colors[color]}{message}{colors['end']}")

def test_endpoint(name, method, endpoint, data=None):
    """Test a single API endpoint"""
    print(f"\n🧪 Testing: {name}")
    try:
        url = f"{BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        if response.status_code in [200, 201]:
            color_print('green', f"✅ PASS - Status: {response.status_code}")
            if response.text:
                try:
                    result = response.json()
                    if isinstance(result, list):
                        print(f"   Response: {len(result)} items returned")
                    elif isinstance(result, dict):
                        print(f"   Response: {json.dumps(result, indent=2)[:200]}...")
                except:
                    print(f"   Response: {response.text[:100]}...")
            return True
        else:
            color_print('red', f"❌ FAIL - Status: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        color_print('red', "❌ FAIL - Cannot connect to backend")
        print(f"   Make sure backend is running on {BASE_URL}")
        return False
    except Exception as e:
        color_print('red', f"❌ FAIL - {str(e)}")
        return False

def run_tests():
    """Run all API tests"""
    color_print('blue', "=" * 60)
    color_print('blue', "🚀 TalentDog API Test Suite")
    color_print('blue', "=" * 60)
    
    tests = [
        {
            'name': 'Health Check',
            'method': 'GET',
            'endpoint': '/',
        },
        {
            'name': 'Get Talent Pool',
            'method': 'GET',
            'endpoint': '/api/talent-pool?limit=10',
        },
        {
            'name': 'Get Vacancies',
            'method': 'GET',
            'endpoint': '/api/vacancies',
        },
        {
            'name': 'Add Talent Profile',
            'method': 'POST',
            'endpoint': '/api/talent/add',
            'data': {
                'name': 'Test User',
                'role': 'Senior Developer',
                'currentCompany': 'Test Corp',
                'location': 'Amsterdam, NL',
                'sector': 'Technology',
                'email': 'test@example.com',
                'startDate': '2022-01-15'
            }
        },
        {
            'name': 'Run Signal Monitor',
            'method': 'POST',
            'endpoint': '/api/monitor/run',
        },
    ]
    
    results = []
    for test in tests:
        result = test_endpoint(
            test['name'],
            test['method'],
            test['endpoint'],
            test.get('data')
        )
        results.append(result)
    
    # Summary
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        color_print('green', f"✅ All tests passed! ({passed}/{total})")
        color_print('green', "\n🎉 TalentDog API is fully operational!")
        return 0
    else:
        color_print('yellow', f"⚠️  {passed}/{total} tests passed")
        color_print('yellow', f"   {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())
