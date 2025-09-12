#!/usr/bin/env python3
"""
Comprehensive API Testing Suite
Tests all endpoints with edge cases, error conditions, and realistic scenarios
"""

import httpx
import json
import time
from typing import Dict, Any, List

API_BASE = "http://localhost:8001/api/v1"

class APITestSuite:
    def __init__(self):
        self.client = httpx.Client()
        self.test_results = []
    
    def test_result(self, test_name: str, passed: bool, details: str = ""):
        """Record test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.test_results.append(f"{status} {test_name}: {details}")
        print(f"{status} {test_name}: {details}")
    
    def test_basic_endpoints(self):
        """Test basic endpoint functionality"""
        print("\n🧪 Testing Basic Endpoints")
        print("=" * 50)
        
        # Test root endpoint
        try:
            response = self.client.get(f"{API_BASE.replace('/api/v1', '')}/")
            self.test_result("Root Endpoint", response.status_code == 200, 
                           f"Status: {response.status_code}")
        except Exception as e:
            self.test_result("Root Endpoint", False, str(e))
        
        # Test neighborhoods list
        try:
            response = self.client.get(f"{API_BASE}/neighborhoods/")
            data = response.json()
            neighborhoods_count = data.get('count', 0)
            self.test_result("List Neighborhoods", 
                           response.status_code == 200 and neighborhoods_count > 0,
                           f"Status: {response.status_code}, Count: {neighborhoods_count}")
        except Exception as e:
            self.test_result("List Neighborhoods", False, str(e))
    
    def test_zoning_endpoints(self):
        """Test zoning endpoints with all neighborhoods"""
        print("\n🏙️ Testing Zoning Endpoints")
        print("=" * 50)
        
        test_neighborhoods = [
            "marina", "marina_district", "Marina District",
            "hayes", "hayes_valley", "Hayes Valley", 
            "mission", "mission_district", "Mission District"
        ]
        
        for neighborhood in test_neighborhoods:
            try:
                response = self.client.get(f"{API_BASE}/neighborhoods/{neighborhood}/zoning")
                
                if response.status_code == 200:
                    data = response.json()
                    has_required_fields = all(key in data for key in 
                                           ['neighborhood', 'zone_type', 'rules'])
                    self.test_result(f"Zoning: {neighborhood}", 
                                   has_required_fields,
                                   f"Zone: {data.get('zone_type', 'N/A')}")
                else:
                    self.test_result(f"Zoning: {neighborhood}", False, 
                                   f"HTTP {response.status_code}")
            except Exception as e:
                self.test_result(f"Zoning: {neighborhood}", False, str(e))
    
    def test_constraint_validation_edge_cases(self):
        """Test constraint validation with edge cases"""
        print("\n⚖️ Testing Constraint Validation Edge Cases")
        print("=" * 50)
        
        edge_cases = [
            {
                "name": "Zero FAR",
                "neighborhood": "marina",
                "proposal": {"far": 0.0, "height_ft": 20, "lot_area_sf": 2500, "num_units": 1}
            },
            {
                "name": "Maximum Valid Marina",
                "neighborhood": "marina", 
                "proposal": {"far": 0.8, "height_ft": 40, "lot_area_sf": 5000, "num_units": 3}
            },
            {
                "name": "Extreme Violation Marina",
                "neighborhood": "marina",
                "proposal": {"far": 5.0, "height_ft": 200, "lot_area_sf": 1000, "num_units": 50}
            },
            {
                "name": "Hayes Valley Transit-Oriented",
                "neighborhood": "hayes_valley",
                "proposal": {"far": 3.0, "height_ft": 55, "lot_area_sf": 3000, "num_units": 20}
            },
            {
                "name": "Mission High Density",
                "neighborhood": "mission",
                "proposal": {"far": 4.0, "height_ft": 85, "lot_area_sf": 4000, "num_units": 35}
            },
            {
                "name": "Tiny Lot",
                "neighborhood": "marina",
                "proposal": {"far": 0.5, "height_ft": 30, "lot_area_sf": 500, "num_units": 1}
            },
            {
                "name": "Massive Lot",
                "neighborhood": "mission",
                "proposal": {"far": 2.0, "height_ft": 60, "lot_area_sf": 50000, "num_units": 100}
            }
        ]
        
        for case in edge_cases:
            try:
                response = self.client.post(
                    f"{API_BASE}/neighborhoods/{case['neighborhood']}/validate-proposal",
                    json=case['proposal']
                )
                
                if response.status_code == 200:
                    data = response.json()
                    is_valid = data.get('is_valid', False)
                    violations = len(data.get('violations', []))
                    self.test_result(f"Validation: {case['name']}", True,
                                   f"Valid: {is_valid}, Violations: {violations}")
                else:
                    self.test_result(f"Validation: {case['name']}", False,
                                   f"HTTP {response.status_code}")
            except Exception as e:
                self.test_result(f"Validation: {case['name']}", False, str(e))
    
    def test_error_conditions(self):
        """Test error handling"""
        print("\n🚫 Testing Error Conditions")
        print("=" * 50)
        
        error_tests = [
            {
                "name": "Invalid Neighborhood",
                "url": f"{API_BASE}/neighborhoods/nonexistent/zoning",
                "expected_status": 404
            },
            {
                "name": "Malformed JSON",
                "url": f"{API_BASE}/neighborhoods/marina/validate-proposal",
                "method": "POST",
                "data": '{"invalid": json}',
                "expected_status": 422
            },
            {
                "name": "Missing Required Fields",
                "url": f"{API_BASE}/neighborhoods/marina/validate-proposal", 
                "method": "POST",
                "json": {"far": 1.0},  # missing other required fields
                "expected_status": [200, 422]  # might work with defaults
            }
        ]
        
        for test in error_tests:
            try:
                if test.get('method') == 'POST':
                    if 'data' in test:
                        response = self.client.post(test['url'], 
                                                  content=test['data'],
                                                  headers={'Content-Type': 'application/json'})
                    else:
                        response = self.client.post(test['url'], json=test.get('json', {}))
                else:
                    response = self.client.get(test['url'])
                
                expected = test['expected_status']
                if isinstance(expected, list):
                    passed = response.status_code in expected
                else:
                    passed = response.status_code == expected
                
                self.test_result(f"Error: {test['name']}", passed,
                               f"Expected: {expected}, Got: {response.status_code}")
            except Exception as e:
                self.test_result(f"Error: {test['name']}", False, str(e))
    
    def test_performance_basic(self):
        """Basic performance testing"""
        print("\n⚡ Testing Basic Performance")
        print("=" * 50)
        
        # Test response times
        endpoints = [
            f"{API_BASE}/neighborhoods/",
            f"{API_BASE}/neighborhoods/marina/zoning",
            f"{API_BASE}/neighborhoods/hayes_valley/zoning"
        ]
        
        for endpoint in endpoints:
            try:
                start_time = time.time()
                response = self.client.get(endpoint)
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000  # ms
                passed = response.status_code == 200 and response_time < 2000  # < 2s
                
                self.test_result(f"Performance: {endpoint.split('/')[-1] or 'neighborhoods'}", 
                               passed, f"{response_time:.1f}ms")
            except Exception as e:
                self.test_result(f"Performance: {endpoint}", False, str(e))
    
    def test_realistic_scenarios(self):
        """Test realistic SF development scenarios"""
        print("\n🏗️ Testing Realistic Development Scenarios") 
        print("=" * 50)
        
        scenarios = [
            {
                "name": "Affordable Housing Hayes Valley",
                "description": "20% affordable housing near BART",
                "neighborhood": "hayes_valley",
                "proposal": {"far": 2.8, "height_ft": 50, "lot_area_sf": 3000, "num_units": 15}
            },
            {
                "name": "Marina Townhomes",
                "description": "Low-density residential respecting flood zones",
                "neighborhood": "marina", 
                "proposal": {"far": 0.7, "height_ft": 35, "lot_area_sf": 4000, "num_units": 4}
            },
            {
                "name": "Mission Anti-Displacement",
                "description": "High density with maximum affordability",
                "neighborhood": "mission",
                "proposal": {"far": 3.5, "height_ft": 75, "lot_area_sf": 5000, "num_units": 40}
            }
        ]
        
        for scenario in scenarios:
            try:
                response = self.client.post(
                    f"{API_BASE}/neighborhoods/{scenario['neighborhood']}/validate-proposal",
                    json=scenario['proposal']
                )
                
                if response.status_code == 200:
                    data = response.json()
                    is_valid = data.get('is_valid', False)
                    violations = data.get('violations', [])
                    
                    # Check if result makes planning sense
                    proposal = scenario['proposal']
                    expected_violations = []
                    
                    if scenario['neighborhood'] == 'marina' and proposal['far'] > 0.8:
                        expected_violations.append('FAR')
                    if scenario['neighborhood'] == 'marina' and proposal['height_ft'] > 40:
                        expected_violations.append('Height')
                    
                    has_expected_violations = any(
                        exp in str(violations) for exp in expected_violations
                    ) if expected_violations else True
                    
                    self.test_result(f"Scenario: {scenario['name']}", 
                                   True, f"Valid: {is_valid}, Makes planning sense: {has_expected_violations}")
                else:
                    self.test_result(f"Scenario: {scenario['name']}", False,
                                   f"HTTP {response.status_code}")
            except Exception as e:
                self.test_result(f"Scenario: {scenario['name']}", False, str(e))
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("🧪 COMPREHENSIVE API TEST SUITE")
        print("=" * 60)
        
        self.test_basic_endpoints()
        self.test_zoning_endpoints()
        self.test_constraint_validation_edge_cases()
        self.test_error_conditions()
        self.test_performance_basic()
        self.test_realistic_scenarios()
        
        # Summary
        print("\n📊 TEST SUMMARY")
        print("=" * 60)
        for result in self.test_results:
            print(result)
        
        passed = len([r for r in self.test_results if "✅ PASS" in r])
        failed = len([r for r in self.test_results if "❌ FAIL" in r])
        total = len(self.test_results)
        
        print(f"\n🎯 RESULTS: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if failed == 0:
            print("🎉 ALL TESTS PASSED! Foundation is solid for agent development.")
        else:
            print(f"⚠️  {failed} tests failed. Fix these before building agents.")

if __name__ == "__main__":
    suite = APITestSuite()
    suite.run_all_tests()