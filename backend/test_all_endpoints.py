#!/usr/bin/env python3
"""
Comprehensive Phase 10 Globalization Endpoint Testing Script
Tests ALL endpoints and reports detailed status
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(method, endpoint, data=None, expected_status=200, description=""):
    """Test a single endpoint and return results"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            return {"error": f"Unsupported method: {method}"}
        
        status = response.status_code
        success = status == expected_status
        
        # Try to parse JSON response
        try:
            content = response.json()
        except:
            content = response.text[:200] + "..." if len(response.text) > 200 else response.text
        
        return {
            "endpoint": endpoint,
            "method": method,
            "status": status,
            "expected": expected_status,
            "success": success,
            "description": description,
            "content": content
        }
    
    except Exception as e:
        return {
            "endpoint": endpoint,
            "method": method,
            "status": "ERROR",
            "expected": expected_status,
            "success": False,
            "description": description,
            "error": str(e)
        }

def main():
    """Run comprehensive endpoint tests"""
    print("=" * 80)
    print("PHASE 10 GLOBALIZATION - COMPREHENSIVE ENDPOINT TESTING")
    print("=" * 80)
    print(f"Testing at: {datetime.now()}")
    print(f"Base URL: {BASE_URL}")
    print()
    
    # Define all endpoints to test
    tests = [
        # Languages endpoints
        ("GET", "/api/globalization/languages/", None, 200, "List all languages"),
        ("GET", "/api/globalization/languages/popular/", None, 200, "Get popular languages"),
        
        # Currency endpoints
        ("GET", "/api/globalization/currencies/", None, 200, "List all currencies"),
        ("GET", "/api/globalization/currencies/rates/", None, 200, "Get exchange rates"),
        ("POST", "/api/globalization/currencies/convert/", 
         {"amount": 100, "from": "USD", "to": "EUR"}, 200, "Convert currency"),
        
        # Translation endpoints
        ("GET", "/api/globalization/translations/", None, 200, "List translations"),
        ("GET", "/api/globalization/translations/bulk/?keys=hello,world&language=en", None, 200, "Bulk translations"),
        ("POST", "/api/globalization/translations/auto_translate/", 
         {"text": "Hello", "target_language": "es"}, 200, "Auto-translate text"),
        
        # User localization (requires auth - expect 401)
        ("GET", "/api/globalization/user-localization/", None, 401, "User localization (auth required)"),
        
        # Localized content
        ("GET", "/api/globalization/localized-content/?content_type=test&content_id=1", None, 200, "Localized content"),
        
        # Analytics (requires auth - expect 401)
        ("GET", "/api/globalization/analytics/", None, 401, "Analytics (auth required)"),
        
        # Health check
        ("GET", "/api/globalization/health/", None, 200, "Health check"),
    ]
    
    results = []
    passed = 0
    failed = 0
    
    for method, endpoint, data, expected, description in tests:
        print(f"Testing: {method} {endpoint}")
        result = test_endpoint(method, endpoint, data, expected, description)
        results.append(result)
        
        if result["success"]:
            print(f"  ✅ PASS - {result['status']} (expected {result['expected']})")
            passed += 1
        else:
            print(f"  ❌ FAIL - {result['status']} (expected {result['expected']})")
            if 'error' in result:
                print(f"     Error: {result['error']}")
            failed += 1
        print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/len(tests)*100):.1f}%")
    print()
    
    if failed > 0:
        print("FAILED ENDPOINTS:")
        for result in results:
            if not result["success"]:
                print(f"  ❌ {result['method']} {result['endpoint']} - {result['status']}")
                print(f"     {result['description']}")
        print()
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
