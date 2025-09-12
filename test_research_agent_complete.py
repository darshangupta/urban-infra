#!/usr/bin/env python3
"""
Comprehensive Integration Test for Research Agent
Tests the complete end-to-end research_query workflow
"""

import sys
import os
import json

# Import the classes directly from the file to avoid __init__.py issues
import importlib.util
spec = importlib.util.spec_from_file_location("research_agent", 
    os.path.join(os.path.dirname(__file__), 'backend', 'app', 'agents', 'research_agent.py'))
research_agent_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(research_agent_module)

ResearchAgent = research_agent_module.ResearchAgent
PlanningIntent = research_agent_module.PlanningIntent
SpatialFocus = research_agent_module.SpatialFocus

def test_complete_research_agent():
    print("🔬 Testing Complete Research Agent Integration")
    print("=" * 70)
    
    agent = ResearchAgent()
    
    # Comprehensive test cases matching our CLAUDE.md examples
    test_cases = [
        {
            "query": "Add 50 affordable housing units near BART in Hayes Valley",
            "expected": {
                "intent": PlanningIntent.HOUSING_DEVELOPMENT,
                "spatial_focus": SpatialFocus.NEAR_TRANSIT,
                "neighborhood": "Hayes Valley",
                "units": 50,
                "affordability": True
            }
        },
        {
            "query": "Make the Marina more walkable while respecting flood risks",
            "expected": {
                "intent": PlanningIntent.WALKABILITY_IMPROVEMENT,
                "spatial_focus": SpatialFocus.WATERFRONT,
                "neighborhood": "Marina District", 
                "flood_awareness": True
            }
        },
        {
            "query": "Increase density in Mission without displacing existing residents",
            "expected": {
                "intent": PlanningIntent.ANTI_DISPLACEMENT,
                "spatial_focus": SpatialFocus.CULTURAL_DISTRICT,
                "neighborhood": "Mission District",
                "displacement_focus": True
            }
        }
    ]
    
    passed_tests = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        query = test_case["query"]
        expected = test_case["expected"]
        
        print(f"\n🎯 Test {i}: {query}")
        print("-" * 60)
        
        try:
            # Execute complete research workflow
            research_brief = agent.research_query(query)
            
            print(f"📋 Research Brief Generated:")
            print(f"  Intent: {research_brief.intent}")
            print(f"  Spatial Focus: {research_brief.spatial_focus}") 
            print(f"  Neighborhood: {research_brief.neighborhood.display_name}")
            print(f"  Target Units: {research_brief.target_metrics.units}")
            print(f"  Affordability: {research_brief.target_metrics.affordability_pct}")
            print(f"  Confidence: {research_brief.confidence_score:.2f}")
            
            print(f"  Opportunities ({len(research_brief.key_opportunities)}): {research_brief.key_opportunities[:2]}...")
            print(f"  Constraints ({len(research_brief.major_constraints)}): {research_brief.major_constraints[:2]}...")
            print(f"  Policies ({len(research_brief.policy_considerations)}): {research_brief.policy_considerations[:2]}...")
            print(f"  Notes ({len(research_brief.research_notes)}): {research_brief.research_notes[:1]}...")
            
            # Validation checks
            checks = []
            
            # Intent matching
            intent_match = research_brief.intent == expected["intent"]
            checks.append(("Intent", intent_match))
            
            # Spatial focus matching
            spatial_match = research_brief.spatial_focus == expected["spatial_focus"]
            checks.append(("Spatial Focus", spatial_match))
            
            # Neighborhood matching
            neighborhood_match = research_brief.neighborhood.display_name == expected["neighborhood"]
            checks.append(("Neighborhood", neighborhood_match))
            
            # Target metrics validation
            if "units" in expected:
                units_match = research_brief.target_metrics.units == expected["units"]
                checks.append(("Units", units_match))
            
            if expected.get("affordability"):
                has_affordability = research_brief.target_metrics.affordability_pct is not None
                checks.append(("Has Affordability", has_affordability))
            
            # Comprehensive data structure validation
            has_opportunities = len(research_brief.key_opportunities) >= 2
            has_constraints = len(research_brief.major_constraints) >= 1
            has_policies = len(research_brief.policy_considerations) >= 2
            has_notes = len(research_brief.research_notes) >= 1
            good_confidence = research_brief.confidence_score >= 0.5
            
            checks.extend([
                ("Has Opportunities", has_opportunities),
                ("Has Constraints", has_constraints), 
                ("Has Policies", has_policies),
                ("Has Notes", has_notes),
                ("Good Confidence", good_confidence)
            ])
            
            # Query-specific validations
            if expected.get("flood_awareness"):
                flood_mentioned = any("flood" in constraint.lower() for constraint in research_brief.major_constraints)
                checks.append(("Flood Awareness", flood_mentioned))
            
            if expected.get("displacement_focus"):
                intent_has_displacement = "displacement" in str(research_brief.intent).lower()
                constraints_have_displacement = any("displacement" in constraint.lower() for constraint in research_brief.major_constraints)
                displacement_mentioned = intent_has_displacement or constraints_have_displacement
                checks.append(("Displacement Focus", displacement_mentioned))
            
            # Display validation results
            print(f"\n  📊 Validation Results:")
            all_passed = True
            for check_name, result in checks:
                status = "✅" if result else "❌"
                print(f"    {status} {check_name}")
                if not result:
                    all_passed = False
            
            if all_passed:
                passed_tests += 1
                print(f"  🎉 Test {i} PASSED - Complete research workflow successful!")
            else:
                print(f"  💥 Test {i} FAILED - Some validations failed")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n📈 COMPLETE RESEARCH AGENT TEST SUMMARY")
    print("=" * 70)
    print(f"Passed: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("🏆 ALL TESTS PASSED! Research Agent is fully functional!")
        print("✅ Query Parser: Working")
        print("✅ Neighborhood Research: Working") 
        print("✅ Spatial Analysis: Working")
        print("✅ Complete Integration: Working")
        print("✅ Ready for Agent 2 (Planner) integration")
        return True
    else:
        failed = total_tests - passed_tests
        print(f"⚠️  {failed} tests failed. Review complete workflow.")
        return False

def demo_research_brief():
    """Demo the research brief output for documentation"""
    print(f"\n🎪 RESEARCH BRIEF DEMO")
    print("=" * 70)
    
    agent = ResearchAgent()
    query = "Add affordable housing near BART in Hayes Valley"
    
    print(f"Query: \"{query}\"")
    brief = agent.research_query(query)
    
    # Pretty print the complete research brief
    print(f"\n📄 Complete Research Brief:")
    print(f"Original Query: {brief.original_query}")
    print(f"Intent: {brief.intent}")
    print(f"Spatial Focus: {brief.spatial_focus}")
    print(f"Confidence: {brief.confidence_score:.1%}")
    
    print(f"\nNeighborhood Profile:")
    print(f"  Name: {brief.neighborhood.display_name}")
    print(f"  Area Type: {brief.neighborhood.area_type}")
    print(f"  Zone: {brief.neighborhood.zoning.zone_type}")
    print(f"  Max FAR: {brief.neighborhood.zoning.max_far}")
    print(f"  Max Height: {brief.neighborhood.zoning.max_height_ft}ft")
    print(f"  Transit: {brief.neighborhood.spatial.transit_access}")
    
    print(f"\nTarget Metrics:")
    print(f"  Units: {brief.target_metrics.units}")
    print(f"  Affordability: {brief.target_metrics.affordability_pct:.1%}")
    
    print(f"\nKey Opportunities ({len(brief.key_opportunities)}):")
    for opp in brief.key_opportunities:
        print(f"  • {opp}")
    
    print(f"\nMajor Constraints ({len(brief.major_constraints)}):")
    for constraint in brief.major_constraints:
        print(f"  • {constraint}")
    
    print(f"\nPolicy Considerations ({len(brief.policy_considerations)}):")
    for policy in brief.policy_considerations:
        print(f"  • {policy}")
    
    print(f"\nResearch Notes ({len(brief.research_notes)}):")
    for note in brief.research_notes:
        print(f"  • {note}")

if __name__ == "__main__":
    success = test_complete_research_agent()
    if success:
        demo_research_brief()
    else:
        print("\n⚠️  Fix issues before running demo")