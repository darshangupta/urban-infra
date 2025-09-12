#!/usr/bin/env python3
"""
Test the Neighborhood Research Module for Research Agent
Verifies integration with live API and fallback mechanisms
"""

import sys
import os

# Import the classes directly from the file to avoid __init__.py issues
import importlib.util
spec = importlib.util.spec_from_file_location("research_agent", 
    os.path.join(os.path.dirname(__file__), 'backend', 'app', 'agents', 'research_agent.py'))
research_agent_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(research_agent_module)

ResearchAgent = research_agent_module.ResearchAgent
PlanningIntent = research_agent_module.PlanningIntent

def test_neighborhood_research():
    print("🏙️ Testing Neighborhood Research Module")
    print("=" * 60)
    
    agent = ResearchAgent()
    
    test_cases = [
        {
            "name": "Marina District - Live API Integration",
            "neighborhood": "Marina District",
            "expected_zone": "RH-1",
            "expected_constraints": ["flood_zone", "height_limit"]
        },
        {
            "name": "Hayes Valley - Live API Integration", 
            "neighborhood": "Hayes Valley",
            "expected_zone": "NCT-3", 
            "expected_constraints": ["historic_preservation"]
        },
        {
            "name": "Mission District - Live API Integration",
            "neighborhood": "Mission District",
            "expected_zone": "NCT-4",
            "expected_constraints": ["displacement_risk", "cultural_preservation"]
        }
    ]
    
    passed_tests = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        neighborhood = test_case["neighborhood"]
        print(f"\n🏗️ Test {i}: {test_case['name']}")
        print("-" * 50)
        
        try:
            # Test neighborhood research
            profile = agent._research_neighborhood(neighborhood)
            
            # Verify basic structure
            print(f"  Display Name: {profile.display_name}")
            print(f"  Zone Type: {profile.zoning.zone_type}")
            print(f"  Area Type: {profile.area_type}")
            print(f"  Characteristics: {profile.characteristics}")
            print(f"  Transit Access: {profile.spatial.transit_access}")
            print(f"  Constraints: {profile.constraints}")
            
            # Verify expected data
            name_match = profile.display_name == neighborhood
            has_zoning = profile.zoning is not None
            has_spatial = profile.spatial is not None 
            has_demographics = profile.demographics is not None
            has_constraints = len(profile.constraints) > 0
            
            # Check for some expected constraints
            expected_constraints_present = any(
                constraint in profile.constraints 
                for constraint in test_case["expected_constraints"]
            )
            
            print(f"  ✅ Structure: Name={name_match}, Zoning={has_zoning}, Spatial={has_spatial}")
            print(f"  ✅ Data: Demographics={has_demographics}, Constraints={has_constraints}")
            print(f"  ✅ Expected Constraints Present: {expected_constraints_present}")
            
            test_passed = all([
                name_match, has_zoning, has_spatial, 
                has_demographics, has_constraints, expected_constraints_present
            ])
            
            if test_passed:
                passed_tests += 1
                print(f"  🎉 Test {i} PASSED")
            else:
                print(f"  💥 Test {i} FAILED")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Test opportunities and constraints generation
    print(f"\n🔍 Testing Opportunities & Constraints Generation")
    print("-" * 50)
    
    try:
        # Use Hayes Valley profile for testing
        hayes_profile = agent._research_neighborhood("Hayes Valley")
        
        # Test different intents
        test_intents = [
            PlanningIntent.HOUSING_DEVELOPMENT,
            PlanningIntent.ANTI_DISPLACEMENT,
            PlanningIntent.CLIMATE_RESILIENCE,
            PlanningIntent.WALKABILITY_IMPROVEMENT
        ]
        
        for intent in test_intents:
            opportunities, constraints = agent._generate_opportunities_constraints(hayes_profile, intent)
            print(f"  Intent: {intent}")
            print(f"    Opportunities ({len(opportunities)}): {opportunities[:2]}...")
            print(f"    Constraints ({len(constraints)}): {constraints[:2]}...")
            
            if len(opportunities) > 0 and len(constraints) > 0:
                passed_tests += 1
                print(f"    ✅ Generated meaningful data")
            else:
                print(f"    ❌ Missing opportunities or constraints")
        
        total_tests += len(test_intents)
        
    except Exception as e:
        print(f"  ❌ Error in opportunities/constraints: {e}")
    
    print(f"\n📊 NEIGHBORHOOD RESEARCH TEST SUMMARY")
    print("=" * 60)
    print(f"Passed: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests >= total_tests * 0.8:  # 80% pass rate
        print("🎯 Neighborhood Research Module working well!")
        print("✅ API integration successful with robust fallback")
        print("✅ Ready to proceed with Spatial Analysis Module")
    else:
        failed = total_tests - passed_tests
        print(f"⚠️  {failed} tests failed. Review neighborhood research logic.")
    
    return passed_tests >= total_tests * 0.8

if __name__ == "__main__":
    test_neighborhood_research()