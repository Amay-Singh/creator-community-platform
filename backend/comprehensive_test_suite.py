#!/usr/bin/env python3
"""
COMPREHENSIVE TEST SUITE - ALL 10 PHASES
Creator Community Platform - Production Readiness Validation
"""

import requests
import json
import sys
import time
from datetime import datetime
from typing import Dict, List, Any
import concurrent.futures
import threading

class CreatorPlatformTestSuite:
    def __init__(self):
        self.backend_url = "http://127.0.0.1:8000"
        self.frontend_url = "http://localhost:3001"
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "phases": {},
            "critical_failures": [],
            "performance_metrics": {}
        }
        self.session = requests.Session()
        self.session.timeout = 10

    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")

    def test_endpoint(self, method: str, endpoint: str, data=None, expected_status=200, description="") -> Dict:
        """Test a single API endpoint"""
        url = f"{self.backend_url}{endpoint}"
        
        try:
            start_time = time.time()
            
            if method == "GET":
                response = self.session.get(url)
            elif method == "POST":
                response = self.session.post(url, json=data, headers={'Content-Type': 'application/json'})
            elif method == "PUT":
                response = self.session.put(url, json=data, headers={'Content-Type': 'application/json'})
            elif method == "DELETE":
                response = self.session.delete(url)
            else:
                return {"error": f"Unsupported method: {method}", "success": False}
            
            response_time = (time.time() - start_time) * 1000  # ms
            
            success = response.status_code == expected_status
            
            try:
                response_data = response.json() if response.content else {}
            except:
                response_data = {"raw_response": response.text[:200]}
            
            return {
                "endpoint": endpoint,
                "method": method,
                "status": response.status_code,
                "expected": expected_status,
                "success": success,
                "description": description,
                "response_time": response_time,
                "data": response_data
            }
            
        except Exception as e:
            return {
                "endpoint": endpoint,
                "method": method,
                "status": "ERROR",
                "expected": expected_status,
                "success": False,
                "description": description,
                "error": str(e),
                "response_time": 0
            }

    def phase_1_authentication_tests(self) -> Dict:
        """Phase 1: Authentication & User Management"""
        self.log("Testing Phase 1: Authentication & User Management")
        
        tests = [
            ("GET", "/api/auth/health/", None, 200, "Auth service health check"),
            ("POST", "/api/auth/register/", {
                "username": "testuser",
                "email": "test@example.com",
                "password": "TestPass123!",
                "password_confirm": "TestPass123!"
            }, 201, "User registration"),
            ("POST", "/api/auth/login/", {
                "email": "test@example.com",
                "password": "TestPass123!"
            }, 200, "User login"),
            ("GET", "/api/auth/profile/", None, 401, "Profile access (no auth)"),
        ]
        
        results = []
        for method, endpoint, data, expected, desc in tests:
            result = self.test_endpoint(method, endpoint, data, expected, desc)
            results.append(result)
            self.results["total_tests"] += 1
            if result["success"]:
                self.results["passed"] += 1
            else:
                self.results["failed"] += 1
                if "auth" in endpoint:
                    self.results["critical_failures"].append(f"Phase 1: {desc}")
        
        return {"phase": 1, "name": "Authentication", "tests": results}

    def phase_2_profiles_tests(self) -> Dict:
        """Phase 2: Creator Profiles & Portfolio Management"""
        self.log("Testing Phase 2: Creator Profiles & Portfolio Management")
        
        tests = [
            ("GET", "/api/accounts/profiles/", None, 200, "List creator profiles"),
            ("GET", "/api/accounts/profile/health/", None, 200, "Profile service health"),
            ("POST", "/api/accounts/profiles/", {
                "bio": "Test creator profile",
                "skills": ["Python", "Django"],
                "portfolio_url": "https://example.com"
            }, 401, "Create profile (no auth)"),
        ]
        
        results = []
        for method, endpoint, data, expected, desc in tests:
            result = self.test_endpoint(method, endpoint, data, expected, desc)
            results.append(result)
            self.results["total_tests"] += 1
            if result["success"]:
                self.results["passed"] += 1
            else:
                self.results["failed"] += 1
        
        return {"phase": 2, "name": "Creator Profiles", "tests": results}

    def phase_3_notifications_tests(self) -> Dict:
        """Phase 3: Notifications & Activity Feed"""
        self.log("Testing Phase 3: Notifications & Activity Feed")
        
        tests = [
            ("GET", "/api/notifications/", None, 401, "List notifications (no auth)"),
            ("GET", "/api/notifications/health/", None, 200, "Notifications health check"),
            ("GET", "/api/activity/feed/", None, 401, "Activity feed (no auth)"),
        ]
        
        results = []
        for method, endpoint, data, expected, desc in tests:
            result = self.test_endpoint(method, endpoint, data, expected, desc)
            results.append(result)
            self.results["total_tests"] += 1
            if result["success"]:
                self.results["passed"] += 1
            else:
                self.results["failed"] += 1
        
        return {"phase": 3, "name": "Notifications", "tests": results}

    def phase_4_ui_tests(self) -> Dict:
        """Phase 4: UI/UX Enhancement"""
        self.log("Testing Phase 4: UI/UX Enhancement")
        
        # Test if frontend is accessible
        try:
            response = requests.get(self.frontend_url, timeout=5)
            frontend_accessible = response.status_code == 200
        except:
            frontend_accessible = False
        
        tests = [
            {
                "endpoint": self.frontend_url,
                "method": "GET",
                "status": 200 if frontend_accessible else "ERROR",
                "expected": 200,
                "success": frontend_accessible,
                "description": "Frontend accessibility",
                "response_time": 0
            }
        ]
        
        self.results["total_tests"] += 1
        if frontend_accessible:
            self.results["passed"] += 1
        else:
            self.results["failed"] += 1
            self.results["critical_failures"].append("Phase 4: Frontend not accessible")
        
        return {"phase": 4, "name": "UI/UX Enhancement", "tests": tests}

    def phase_5_ai_collaboration_tests(self) -> Dict:
        """Phase 5: AI-Powered Matching & Collaboration"""
        self.log("Testing Phase 5: AI-Powered Matching & Collaboration")
        
        tests = [
            ("GET", "/api/ai_services/health/", None, 200, "AI services health check"),
            ("GET", "/api/collaborations/invites/health/", None, 200, "Collaboration invites health"),
            ("GET", "/api/collaborations/invites/sent/", None, 401, "Sent invites (no auth)"),
            ("GET", "/api/collaborations/invites/received/", None, 401, "Received invites (no auth)"),
        ]
        
        results = []
        for method, endpoint, data, expected, desc in tests:
            result = self.test_endpoint(method, endpoint, data, expected, desc)
            results.append(result)
            self.results["total_tests"] += 1
            if result["success"]:
                self.results["passed"] += 1
            else:
                self.results["failed"] += 1
        
        return {"phase": 5, "name": "AI Collaboration", "tests": results}

    def phase_6_messaging_tests(self) -> Dict:
        """Phase 6: Real-time Messaging"""
        self.log("Testing Phase 6: Real-time Messaging")
        
        tests = [
            ("GET", "/api/chat/health/", None, 200, "Chat service health check"),
            ("GET", "/api/chat/conversations/", None, 401, "List conversations (no auth)"),
        ]
        
        results = []
        for method, endpoint, data, expected, desc in tests:
            result = self.test_endpoint(method, endpoint, data, expected, desc)
            results.append(result)
            self.results["total_tests"] += 1
            if result["success"]:
                self.results["passed"] += 1
            else:
                self.results["failed"] += 1
        
        return {"phase": 6, "name": "Real-time Messaging", "tests": results}

    def phase_7_project_management_tests(self) -> Dict:
        """Phase 7: Project Management Tools"""
        self.log("Testing Phase 7: Project Management Tools")
        
        tests = [
            ("GET", "/api/collaborations/projects/", None, 401, "List projects (no auth)"),
            ("GET", "/api/video_collaboration/health/", None, 200, "Video collaboration health"),
        ]
        
        results = []
        for method, endpoint, data, expected, desc in tests:
            result = self.test_endpoint(method, endpoint, data, expected, desc)
            results.append(result)
            self.results["total_tests"] += 1
            if result["success"]:
                self.results["passed"] += 1
            else:
                self.results["failed"] += 1
        
        return {"phase": 7, "name": "Project Management", "tests": results}

    def phase_8_monetization_tests(self) -> Dict:
        """Phase 8: Monetization & Subscriptions"""
        self.log("Testing Phase 8: Monetization & Subscriptions")
        
        tests = [
            ("GET", "/api/subscriptions/health/", None, 200, "Subscription service health"),
            ("GET", "/api/subscriptions/plans/", None, 200, "List subscription plans"),
        ]
        
        results = []
        for method, endpoint, data, expected, desc in tests:
            result = self.test_endpoint(method, endpoint, data, expected, desc)
            results.append(result)
            self.results["total_tests"] += 1
            if result["success"]:
                self.results["passed"] += 1
            else:
                self.results["failed"] += 1
        
        return {"phase": 8, "name": "Monetization", "tests": results}

    def phase_9_analytics_tests(self) -> Dict:
        """Phase 9: Analytics & Insights"""
        self.log("Testing Phase 9: Analytics & Insights")
        
        tests = [
            ("GET", "/api/analytics/health/", None, 200, "Analytics service health"),
            ("GET", "/api/analytics/dashboard/", None, 401, "Analytics dashboard (no auth)"),
        ]
        
        results = []
        for method, endpoint, data, expected, desc in tests:
            result = self.test_endpoint(method, endpoint, data, expected, desc)
            results.append(result)
            self.results["total_tests"] += 1
            if result["success"]:
                self.results["passed"] += 1
            else:
                self.results["failed"] += 1
        
        return {"phase": 9, "name": "Analytics", "tests": results}

    def phase_10_globalization_tests(self) -> Dict:
        """Phase 10: Platform Maturity & Global Scale"""
        self.log("Testing Phase 10: Platform Maturity & Global Scale")
        
        tests = [
            ("GET", "/api/globalization/health/", None, 200, "Globalization health check"),
            ("GET", "/api/globalization/languages/", None, 200, "List languages"),
            ("GET", "/api/globalization/languages/popular/", None, 200, "Popular languages"),
            ("GET", "/api/globalization/currencies/", None, 200, "List currencies"),
            ("GET", "/api/globalization/currencies/rates/", None, 200, "Exchange rates"),
            ("POST", "/api/globalization/currencies/convert/", {
                "amount": 100, "from": "USD", "to": "EUR"
            }, 200, "Currency conversion"),
            ("GET", "/api/globalization/translations/", None, 200, "List translations"),
            ("GET", "/api/globalization/translations/bulk/?keys=hello,world&language=en", None, 200, "Bulk translations"),
            ("POST", "/api/globalization/translations/auto_translate/", {
                "text": "Hello", "target_language": "es"
            }, 200, "Auto translation"),
        ]
        
        results = []
        for method, endpoint, data, expected, desc in tests:
            result = self.test_endpoint(method, endpoint, data, expected, desc)
            results.append(result)
            self.results["total_tests"] += 1
            if result["success"]:
                self.results["passed"] += 1
            else:
                self.results["failed"] += 1
        
        return {"phase": 10, "name": "Globalization", "tests": results}

    def run_comprehensive_tests(self):
        """Run all phase tests"""
        self.log("=" * 80)
        self.log("CREATOR COMMUNITY PLATFORM - COMPREHENSIVE TEST SUITE")
        self.log("=" * 80)
        
        start_time = time.time()
        
        # Run all phase tests
        phase_tests = [
            self.phase_1_authentication_tests,
            self.phase_2_profiles_tests,
            self.phase_3_notifications_tests,
            self.phase_4_ui_tests,
            self.phase_5_ai_collaboration_tests,
            self.phase_6_messaging_tests,
            self.phase_7_project_management_tests,
            self.phase_8_monetization_tests,
            self.phase_9_analytics_tests,
            self.phase_10_globalization_tests,
        ]
        
        for test_func in phase_tests:
            phase_result = test_func()
            self.results["phases"][phase_result["phase"]] = phase_result
        
        total_time = time.time() - start_time
        self.results["performance_metrics"]["total_execution_time"] = total_time
        
        self.generate_report()
        return self.results["failed"] == 0

    def generate_report(self):
        """Generate comprehensive test report"""
        self.log("=" * 80)
        self.log("COMPREHENSIVE TEST RESULTS")
        self.log("=" * 80)
        
        success_rate = (self.results["passed"] / self.results["total_tests"] * 100) if self.results["total_tests"] > 0 else 0
        
        self.log(f"Total Tests: {self.results['total_tests']}")
        self.log(f"Passed: {self.results['passed']}")
        self.log(f"Failed: {self.results['failed']}")
        self.log(f"Success Rate: {success_rate:.1f}%")
        self.log(f"Execution Time: {self.results['performance_metrics']['total_execution_time']:.2f}s")
        
        self.log("\nPHASE BREAKDOWN:")
        for phase_num, phase_data in self.results["phases"].items():
            phase_passed = sum(1 for test in phase_data["tests"] if test["success"])
            phase_total = len(phase_data["tests"])
            phase_rate = (phase_passed / phase_total * 100) if phase_total > 0 else 0
            
            status = "✅ PASS" if phase_passed == phase_total else "❌ FAIL"
            self.log(f"  Phase {phase_num} ({phase_data['name']}): {phase_passed}/{phase_total} ({phase_rate:.1f}%) {status}")
        
        if self.results["critical_failures"]:
            self.log("\nCRITICAL FAILURES:")
            for failure in self.results["critical_failures"]:
                self.log(f"  ❌ {failure}")
        
        self.log("\nDETAILED RESULTS:")
        for phase_num, phase_data in self.results["phases"].items():
            self.log(f"\n--- Phase {phase_num}: {phase_data['name']} ---")
            for test in phase_data["tests"]:
                status = "✅" if test["success"] else "❌"
                self.log(f"  {status} {test['method']} {test.get('endpoint', 'N/A')} - {test['description']}")
                if not test["success"]:
                    self.log(f"      Expected: {test['expected']}, Got: {test['status']}")
                    if "error" in test:
                        self.log(f"      Error: {test['error']}")

def main():
    """Main execution function"""
    test_suite = CreatorPlatformTestSuite()
    
    try:
        success = test_suite.run_comprehensive_tests()
        
        # Save results to file
        with open('/Users/amays/Desktop/Work/Colab/test_results.json', 'w') as f:
            json.dump(test_suite.results, f, indent=2, default=str)
        
        test_suite.log(f"\nTest results saved to: test_results.json")
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        test_suite.log("Test execution interrupted by user")
        return 1
    except Exception as e:
        test_suite.log(f"Test execution failed: {str(e)}", "ERROR")
        return 1

if __name__ == "__main__":
    sys.exit(main())
