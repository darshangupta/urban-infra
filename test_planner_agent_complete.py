#!/usr/bin/env python3
"""
Complete Integration Test for Agent 2 (Planner)
Tests the full Agent 1 → Agent 2 workflow with all modules integrated
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

def test_complete_planner_agent():
    print("🎯 Testing Complete Agent 2 (Planner) Integration")
    print("=" * 75)
    
    research_agent = ResearchAgent()
    planner_agent = PlannerAgent()
    
    # Comprehensive test cases covering different scenarios
    test_cases = [
        {
            "query": "Add 30 affordable housing units near BART in Hayes Valley",
            "expected": {
                "min_plans": 3,
                "has_recommended": True,
                "has_tradeoffs": True,
                "neighborhood": "Hayes Valley"
            }
        },
        {
            "query": "Make the Marina more walkable while respecting flood risks",
            "expected": {
                "min_plans": 3,
                "has_recommended": True,
                "has_tradeoffs": True,
                "neighborhood": "Marina District"
            }
        },
        {
            "query": "Increase density in Mission without displacing existing residents",
            "expected": {
                "min_plans": 3,
                "has_recommended": True,
                "has_tradeoffs": True,
                "neighborhood": "Mission District"
            }
        }
    ]
    
    passed_tests = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        query = test_case["query"]
        expected = test_case["expected"]
        
        print(f"\n🔬 Test {i}: {query}")
        print("-" * 75)
        
        try:
            # Step 1: Generate research brief from Agent 1
            print("📋 Step 1: Research Brief Generation")
            research_brief = research_agent.research_query(query)
            print(f"  ✅ Research Brief: {research_brief.neighborhood.display_name}, {research_brief.intent}")
            
            # Step 2: Generate planning alternatives with Agent 2
            print("🏗️ Step 2: Planning Alternatives Generation")
            planning_alternatives = planner_agent.generate_scenarios(research_brief)
            
            print(f"  📄 Generated Planning Alternatives:")
            print(f"    Scenario: {planning_alternatives.scenario_name}")
            print(f"    Plans: {len(planning_alternatives.plans)}")
            print(f"    Recommended: {planning_alternatives.recommended_plan_id}")
            print(f"    Confidence: {planning_alternatives.generation_confidence:.2f}")
            
            # Display plan details
            for j, plan in enumerate(planning_alternatives.plans[:3], 1):  # Show first 3
                print(f"    {j}. {plan.name} ({plan.plan_type.value})")
                print(f"       FAR: {plan.far}, Height: {plan.height_ft}ft, Units: {plan.total_units}")
                print(f"       Feasibility: {plan.feasibility.value}, Score: {plan.compliance_score:.2f}")
            
            print(f"  📊 Analysis:")
            print(f"    Feasibility: {planning_alternatives.feasibility_summary}")
            print(f"    Tradeoffs ({len(planning_alternatives.tradeoffs_analysis)}): {planning_alternatives.tradeoffs_analysis[:1]}")
            print(f"    Notes ({len(planning_alternatives.planning_notes)}): {planning_alternatives.planning_notes[:1]}")
            
            # Comprehensive validation checks
            checks = []
            
            # Basic structure validation
            has_plans = len(planning_alternatives.plans) >= expected["min_plans"]
            checks.append(("Minimum Plans Generated", has_plans))
            
            has_recommended = bool(planning_alternatives.recommended_plan_id) and planning_alternatives.recommended_plan_id != "none"
            checks.append(("Has Recommended Plan", has_recommended))
            
            correct_neighborhood = planning_alternatives.neighborhood == expected["neighborhood"]
            checks.append(("Correct Neighborhood", correct_neighborhood))
            
            has_scenario_name = bool(planning_alternatives.scenario_name)
            checks.append(("Has Scenario Name", has_scenario_name))
            
            # Data quality validation
            all_plans_valid = all(
                plan.plan_id and plan.name and plan.far > 0 and 
                plan.height_ft > 0 and plan.total_units > 0
                for plan in planning_alternatives.plans
            )
            checks.append(("All Plans Valid", all_plans_valid))
            
            # Optimization validation  
            plans_are_ranked = True
            if len(planning_alternatives.plans) > 1:
                # Check if plans are actually ranked (first should be recommended)
                recommended_is_first = planning_alternatives.plans[0].plan_id == planning_alternatives.recommended_plan_id
                plans_are_ranked = recommended_is_first
            checks.append(("Plans Are Ranked", plans_are_ranked))
            
            # Validation integration check
            all_plans_validated = all(
                hasattr(plan, 'violations') and isinstance(plan.violations, list)
                for plan in planning_alternatives.plans
            )
            checks.append(("All Plans Validated", all_plans_validated))
            
            # Analysis completeness
            has_tradeoffs = len(planning_alternatives.tradeoffs_analysis) > 0
            checks.append(("Has Tradeoffs Analysis", has_tradeoffs))
            
            has_planning_notes = len(planning_alternatives.planning_notes) > 0  
            checks.append(("Has Planning Notes", has_planning_notes))
            
            reasonable_confidence = 0.1 <= planning_alternatives.generation_confidence <= 1.0
            checks.append(("Reasonable Confidence", reasonable_confidence))
            
            # Context transfer validation
            has_opportunities = len(planning_alternatives.zoning_opportunities) > 0
            has_challenges = len(planning_alternatives.regulatory_challenges) > 0
            context_transferred = has_opportunities and has_challenges
            checks.append(("Context Transferred", context_transferred))
            
            # Display validation results
            print(f"\n  🔍 Validation Results:")
            all_passed = True
            for check_name, result in checks:
                status = "✅" if result else "❌"
                print(f"    {status} {check_name}")
                if not result:
                    all_passed = False
            
            if all_passed:
                passed_tests += 1
                print(f"  🎉 Test {i} PASSED")
            else:
                print(f"  💥 Test {i} FAILED")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Test plan optimization scoring
    print(f"\n⚖️ Testing Plan Optimization Scoring")
    print("-" * 75)
    
    try:
        research_brief = research_agent.research_query("Add housing in Hayes Valley")
        plans = planner_agent._generate_candidate_plans(research_brief)
        
        # Test scoring system
        scores = []
        for plan in plans:
            score = planner_agent._calculate_plan_score(plan, research_brief)
            scores.append((plan.plan_id, score))
        
        # Validate scoring
        all_scores_valid = all(0.0 <= score <= 1.0 for _, score in scores)
        scores_vary = len(set(score for _, score in scores)) > 1  # Different scores
        
        print(f"  📊 Plan Scores:")
        for plan_id, score in scores:
            print(f"    {plan_id}: {score:.3f}")
        
        print(f"  ✅ All Scores Valid (0-1): {all_scores_valid}")
        print(f"  ✅ Score Variety: {scores_vary}")
        
        if all_scores_valid and scores_vary:
            passed_tests += 1
        
        total_tests += 1
        
    except Exception as e:
        print(f"  ❌ Scoring Error: {e}")
        total_tests += 1
    
    print(f"\n📈 COMPLETE AGENT 2 TEST SUMMARY")
    print("=" * 75)
    print(f"Passed: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests >= total_tests * 0.85:  # 85% pass rate
        print("🏆 AGENT 2 (PLANNER) FULLY FUNCTIONAL!")
        print("✅ Complete Agent 1 → Agent 2 workflow working")
        print("✅ Scenario generation with live validation")
        print("✅ Plan optimization and ranking") 
        print("✅ Comprehensive analysis and recommendations")
        print("✅ Ready for Agent 3 (Evaluator) development")
        return True
    else:
        failed = total_tests - passed_tests
        print(f"⚠️  {failed} tests failed. Review complete integration.")
        return False

def demo_complete_agent2_workflow():
    """Demonstrate the complete Agent 2 workflow"""
    print(f"\n🎪 COMPLETE AGENT 2 WORKFLOW DEMO")
    print("=" * 75)
    
    research_agent = ResearchAgent()
    planner_agent = PlannerAgent()
    
    query = "Add affordable housing near BART in Hayes Valley"
    print(f"User Query: \"{query}\"")
    
    # Agent 1: Research
    print(f"\n1️⃣ Agent 1 (Research):")
    research_brief = research_agent.research_query(query)
    print(f"   Intent: {research_brief.intent}")
    print(f"   Neighborhood: {research_brief.neighborhood.display_name} ({research_brief.neighborhood.zoning.zone_type})")
    print(f"   Target Units: {research_brief.target_metrics.units}")
    print(f"   Constraints: {len(research_brief.major_constraints)}")
    
    # Agent 2: Planning
    print(f"\n2️⃣ Agent 2 (Planner):")
    planning_alternatives = planner_agent.generate_scenarios(research_brief)
    print(f"   Scenario: {planning_alternatives.scenario_name}")
    print(f"   Generated: {len(planning_alternatives.plans)} feasible plans")
    print(f"   Recommended: {planning_alternatives.recommended_plan_id}")
    print(f"   Confidence: {planning_alternatives.generation_confidence:.0%}")
    
    print(f"\n📋 Planning Alternatives Summary:")
    print(f"   Feasibility: {planning_alternatives.feasibility_summary}")
    
    recommended_plan = next(
        (p for p in planning_alternatives.plans if p.plan_id == planning_alternatives.recommended_plan_id), 
        planning_alternatives.plans[0] if planning_alternatives.plans else None
    )
    
    if recommended_plan:
        print(f"\n🎯 Recommended Plan: {recommended_plan.name}")
        print(f"   Type: {recommended_plan.plan_type.value}")
        print(f"   Specifications: FAR {recommended_plan.far}, {recommended_plan.height_ft}ft, {recommended_plan.total_units} units")
        print(f"   Affordability: {recommended_plan.affordable_units} units ({recommended_plan.affordable_percentage:.0%})")
        print(f"   Feasibility: {recommended_plan.feasibility.value}")
        print(f"   Compliance: {recommended_plan.compliance_score:.0%}")
        
        if recommended_plan.violations:
            print(f"   Violations: {recommended_plan.violations[0]}")
        
        print(f"   Rationale: {', '.join(recommended_plan.design_rationale[:2])}")
    
    print(f"\n🔄 Key Tradeoffs:")
    for tradeoff in planning_alternatives.tradeoffs_analysis[:3]:
        print(f"   • {tradeoff}")

if __name__ == "__main__":
    success = test_complete_planner_agent()
    if success:
        demo_complete_agent2_workflow()
    else:
        print("\n⚠️ Fix integration issues before proceeding")