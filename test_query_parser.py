#!/usr/bin/env python3
"""
Test the Query Parser Module for Research Agent
Verifies sophisticated parsing of natural language queries
"""

import sys
import os
sys.path.append('backend')

from backend.app.agents.research_agent import ResearchAgent, PlanningIntent, SpatialFocus

def test_query_parser():
    print("🔍 Testing Enhanced Query Parser Module")
    print("=" * 60)
    
    # Initialize just the research agent (no full implementation needed yet)
    agent = ResearchAgent()
    
    # Comprehensive test cases covering various parsing scenarios
    test_cases = [
        {
            "query": "Add 50 affordable housing units near BART in Hayes Valley",
            "expected": {
                "neighborhood": "Hayes Valley",
                "intent": PlanningIntent.HOUSING_DEVELOPMENT,
                "spatial_focus": SpatialFocus.NEAR_TRANSIT,
                "units": 50,
                "has_affordability": True
            }
        },
        {
            "query": "Make the Marina more walkable while respecting flood risks",
            "expected": {
                "neighborhood": "Marina District", 
                "intent": PlanningIntent.WALKABILITY_IMPROVEMENT,
                "spatial_focus": SpatialFocus.WATERFRONT,
                "units": None,
                "has_affordability": False
            }
        },
        {
            "query": "Increase density in Mission without displacing existing residents",
            "expected": {
                "neighborhood": "Mission District",
                "intent": PlanningIntent.ANTI_DISPLACEMENT,
                "spatial_focus": SpatialFocus.CULTURAL_DISTRICT,
                "units": None,
                "has_affordability": True
            }
        },
        {
            "query": "Build 25% inclusionary housing with ground floor retail in Hayes Valley",
            "expected": {
                "neighborhood": "Hayes Valley",
                "intent": PlanningIntent.MIXED_USE_DEVELOPMENT,
                "spatial_focus": SpatialFocus.GENERAL,
                "affordability_pct": 0.25,
                "has_affordability": True
            }
        },
        {
            "query": "Create climate-resilient development near the waterfront in Marina District",
            "expected": {
                "neighborhood": "Marina District",
                "intent": PlanningIntent.CLIMATE_RESILIENCE,
                "spatial_focus": SpatialFocus.WATERFRONT,
                "has_affordability": False
            }
        },
        {
            "query": "Add transit-oriented development with 4 stories near BART",
            "expected": {
                "neighborhood": "Hayes Valley",  # Default
                "intent": PlanningIntent.TRANSIT_IMPROVEMENT,
                "spatial_focus": SpatialFocus.NEAR_TRANSIT,
                "height_ft": 48  # 4 stories * 12 ft
            }
        },
        {
            "query": "Build 30 units of affordable housing preserving Mission cultural district",
            "expected": {
                "neighborhood": "Mission District",
                "intent": PlanningIntent.HOUSING_DEVELOPMENT,
                "spatial_focus": SpatialFocus.CULTURAL_DISTRICT,
                "units": 30,
                "has_affordability": True
            }
        }
    ]
    
    passed_tests = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        query = test_case["query"]
        expected = test_case["expected"]
        
        print(f"\n🧪 Test {i}: {query}")
        print("-" * 50)
        
        try:
            # Test the parsing
            parsed = agent._parse_query(query)
            
            # Test the metrics extraction
            target_metrics = agent._extract_target_metrics(query, parsed["intent"])
            
            # Verify neighborhood
            neighborhood_match = parsed["neighborhood_name"] == expected["neighborhood"]
            print(f"  Neighborhood: {parsed['neighborhood_name']} {'✅' if neighborhood_match else '❌'}")
            
            # Verify intent
            intent_match = parsed["intent"] == expected["intent"]
            print(f"  Intent: {parsed['intent']} {'✅' if intent_match else '❌'}")
            
            # Verify spatial focus
            spatial_match = parsed["spatial_focus"] == expected["spatial_focus"]
            print(f"  Spatial Focus: {parsed['spatial_focus']} {'✅' if spatial_match else '❌'}")
            
            # Verify units if expected
            units_match = True
            if "units" in expected:
                if expected["units"] is None:
                    units_match = target_metrics.units is not None  # Should have default
                else:
                    units_match = target_metrics.units == expected["units"]
                print(f"  Units: {target_metrics.units} {'✅' if units_match else '❌'}")
            
            # Verify affordability
            affordability_match = True
            if "affordability_pct" in expected:
                affordability_match = target_metrics.affordability_pct == expected["affordability_pct"]
                print(f"  Affordability: {target_metrics.affordability_pct:.1%} {'✅' if affordability_match else '❌'}")
            elif expected.get("has_affordability"):
                affordability_match = target_metrics.affordability_pct is not None
                print(f"  Has Affordability: {target_metrics.affordability_pct is not None} {'✅' if affordability_match else '❌'}")
            
            # Verify height if expected  
            height_match = True
            if "height_ft" in expected:
                height_match = target_metrics.height_ft == expected["height_ft"]
                print(f"  Height: {target_metrics.height_ft}ft {'✅' if height_match else '❌'}")
            
            # Verify confidence score
            confidence_reasonable = parsed["confidence"] >= 0.1
            print(f"  Confidence: {parsed['confidence']:.2f} {'✅' if confidence_reasonable else '❌'}")
            
            # Overall test result
            test_passed = all([
                neighborhood_match,
                intent_match, 
                spatial_match,
                units_match,
                affordability_match,
                height_match,
                confidence_reasonable
            ])
            
            if test_passed:
                passed_tests += 1
                print(f"  🎉 Test {i} PASSED")
            else:
                print(f"  💥 Test {i} FAILED")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print(f"\n📊 QUERY PARSER TEST SUMMARY")
    print("=" * 60)
    print(f"Passed: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("🎯 ALL TESTS PASSED! Query Parser Module is working correctly.")
        print("✅ Ready to proceed with Neighborhood Research Module.")
    else:
        failed = total_tests - passed_tests
        print(f"⚠️  {failed} tests failed. Review parsing logic before proceeding.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    test_query_parser()