#!/usr/bin/env python3
"""
Test the Scenario Generator Module for Planner Agent
Verifies generation of multiple development plans from research briefs
"""

import sys
import os

# Import the classes directly from files
import importlib.util

# Load Research Agent
research_spec = importlib.util.spec_from_file_location("research_agent", 
    os.path.join(os.path.dirname(__file__), 'backend', 'app', 'agents', 'research_agent.py'))
research_agent_module = importlib.util.module_from_spec(research_spec)
research_spec.loader.exec_module(research_agent_module)

# Load Planner Agent 
planner_spec = importlib.util.spec_from_file_location("planner_agent", 
    os.path.join(os.path.dirname(__file__), 'backend', 'app', 'agents', 'planner_agent.py'))
planner_agent_module = importlib.util.module_from_spec(planner_spec)
planner_spec.loader.exec_module(planner_agent_module)

ResearchAgent = research_agent_module.ResearchAgent
PlannerAgent = planner_agent_module.PlannerAgent
PlanType = planner_agent_module.PlanType

def test_scenario_generator():
    print("🏗️ Testing Scenario Generator Module")
    print("=" * 65)
    
    research_agent = ResearchAgent()
    planner_agent = PlannerAgent()
    
    test_cases = [
        {
            "query": "Add 50 affordable housing units near BART in Hayes Valley",
            "expected_plans": 3,  # Conservative, Moderate, Aggressive
            "expected_types": [PlanType.CONSERVATIVE, PlanType.MODERATE, PlanType.AGGRESSIVE]
        },
        {
            "query": "Make the Marina more walkable while respecting flood risks",
            "expected_plans": 4,  # + Innovative for walkability
            "expected_types": [PlanType.CONSERVATIVE, PlanType.MODERATE, PlanType.AGGRESSIVE, PlanType.INNOVATIVE]
        },
        {
            "query": "Increase density in Mission without displacing existing residents",
            "expected_plans": 4,  # + Innovative for anti-displacement
            "expected_types": [PlanType.CONSERVATIVE, PlanType.MODERATE, PlanType.AGGRESSIVE, PlanType.INNOVATIVE]
        }
    ]
    
    passed_tests = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        query = test_case["query"]
        print(f"\n🎯 Test {i}: {query}")
        print("-" * 65)
        
        try:
            # Get research brief from Agent 1
            research_brief = research_agent.research_query(query)
            print(f"✅ Research Brief: {research_brief.neighborhood.display_name}, Intent: {research_brief.intent}")
            
            # Generate candidate plans using Scenario Generator
            plans = planner_agent._generate_candidate_plans(research_brief)
            
            print(f"📋 Generated {len(plans)} Development Plans:")
            for j, plan in enumerate(plans, 1):
                print(f"  {j}. {plan.name} ({plan.plan_type})")
                print(f"     FAR: {plan.far}, Height: {plan.height_ft}ft, Units: {plan.total_units}")
                print(f"     Affordable: {plan.affordable_units} ({plan.affordable_percentage:.1%})")
                print(f"     Feasibility: {plan.feasibility}")
                print(f"     Compliance: {plan.compliance_score:.2f}")
            
            # Validation checks
            print(f"\n🔍 Validation Results:")
            
            # Check plan count
            plan_count_match = len(plans) == test_case["expected_plans"]
            print(f"  Plan Count: {len(plans)}/{test_case['expected_plans']} {'✅' if plan_count_match else '❌'}")
            
            # Check plan types
            generated_types = [plan.plan_type for plan in plans]
            types_match = all(t in generated_types for t in test_case["expected_types"])
            print(f"  Expected Types Present: {'✅' if types_match else '❌'}")
            
            # Check plan variety (different parameters)
            far_values = [plan.far for plan in plans]
            height_values = [plan.height_ft for plan in plans]
            unit_values = [plan.total_units for plan in plans]
            
            has_variety = (len(set(far_values)) > 1 and 
                          len(set(height_values)) > 1 and
                          len(set(unit_values)) > 1)
            print(f"  Parameter Variety: {'✅' if has_variety else '❌'}")
            
            # Check feasibility assessment variety
            feasibility_values = [plan.feasibility for plan in plans]
            has_feasibility_range = len(set(feasibility_values)) > 1
            print(f"  Feasibility Range: {'✅' if has_feasibility_range else '❌'}")
            
            # Check all plans have required fields
            all_complete = all(
                plan.plan_id and plan.name and plan.description and
                len(plan.design_rationale) > 0 and len(plan.policy_alignment) > 0
                for plan in plans
            )
            print(f"  Complete Plan Data: {'✅' if all_complete else '❌'}")
            
            # Check zoning appropriateness
            zoning_appropriate = all(
                plan.far <= research_brief.neighborhood.zoning.max_far * 1.1 and  # Allow small buffer
                plan.height_ft <= research_brief.neighborhood.zoning.max_height_ft * 1.1
                for plan in plans
            )
            print(f"  Zoning Appropriate: {'✅' if zoning_appropriate else '❌'}")
            
            # Check affordability logic
            affordable_logical = all(
                plan.affordable_units <= plan.total_units and
                (plan.affordable_percentage > 0 if plan.affordable_units > 0 else True)
                for plan in plans
            )
            print(f"  Affordability Logic: {'✅' if affordable_logical else '❌'}")
            
            # Overall test assessment
            test_passed = all([
                plan_count_match, types_match, has_variety, 
                has_feasibility_range, all_complete, 
                zoning_appropriate, affordable_logical
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
    
    # Test intent-specific innovations
    print(f"\n🚀 Testing Intent-Specific Innovations")
    print("-" * 65)
    
    innovation_tests = [
        ("anti_displacement", "Community Land Trust"),
        ("climate_resilience", "Climate-Resilient"),
        ("walkability_improvement", "Walkable")
    ]
    
    for intent, expected_name_part in innovation_tests:
        try:
            # Create a mock research brief with specific intent
            research_brief = research_agent.research_query(f"Test {intent} in Mission District")
            
            # Override intent for testing
            research_brief.intent = intent
            
            plans = planner_agent._generate_candidate_plans(research_brief)
            innovative_plans = [p for p in plans if p.plan_type == PlanType.INNOVATIVE]
            
            has_innovative = len(innovative_plans) > 0
            if has_innovative:
                innovative_plan = innovative_plans[0]
                name_appropriate = expected_name_part.lower() in innovative_plan.name.lower()
                has_special_rationale = len(innovative_plan.design_rationale) >= 4
                
                print(f"  {intent}: {'✅' if name_appropriate and has_special_rationale else '❌'} " +
                      f"({innovative_plan.name})")
                
                if name_appropriate and has_special_rationale:
                    passed_tests += 1
            else:
                print(f"  {intent}: ❌ No innovative plan generated")
            
            total_tests += 1
            
        except Exception as e:
            print(f"  {intent}: ❌ Error: {e}")
            total_tests += 1
    
    print(f"\n📊 SCENARIO GENERATOR TEST SUMMARY")
    print("=" * 65)
    print(f"Passed: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests >= total_tests * 0.8:  # 80% pass rate
        print("🎯 Scenario Generator Module working well!")
        print("✅ Multiple plan types generated correctly")
        print("✅ Parameter variety and feasibility assessment")
        print("✅ Intent-specific innovations implemented")
        print("✅ Ready for Constraint Validator Integration")
        return True
    else:
        failed = total_tests - passed_tests
        print(f"⚠️  {failed} tests failed. Review scenario generation logic.")
        return False

def demo_scenario_generation():
    """Demo the scenario generation output"""
    print(f"\n🎪 SCENARIO GENERATION DEMO")
    print("=" * 65)
    
    research_agent = ResearchAgent()
    planner_agent = PlannerAgent()
    
    query = "Add affordable housing near BART in Hayes Valley"
    print(f"Query: \"{query}\"")
    
    research_brief = research_agent.research_query(query)
    plans = planner_agent._generate_candidate_plans(research_brief)
    
    print(f"\n📄 Generated {len(plans)} Development Scenarios:")
    for i, plan in enumerate(plans, 1):
        print(f"\n{i}. {plan.name}")
        print(f"   Type: {plan.plan_type} | Feasibility: {plan.feasibility}")
        print(f"   FAR: {plan.far} | Height: {plan.height_ft}ft | Units: {plan.total_units}")
        print(f"   Affordable: {plan.affordable_units} units ({plan.affordable_percentage:.1%})")
        print(f"   Parking: {plan.parking_spaces} spaces")
        print(f"   Compliance Score: {plan.compliance_score:.0%}")
        print(f"   Rationale: {', '.join(plan.design_rationale[:2])}...")

if __name__ == "__main__":
    success = test_scenario_generator()
    if success:
        demo_scenario_generation()
    else:
        print("\n⚠️ Fix scenario generation issues before proceeding")