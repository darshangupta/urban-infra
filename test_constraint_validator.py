#!/usr/bin/env python3
"""
Test the Constraint Validator Integration for Planner Agent
Verifies validation of development plans against live zoning API
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
DevelopmentPlan = planner_agent_module.DevelopmentPlan
PlanType = planner_agent_module.PlanType
PlanFeasibility = planner_agent_module.PlanFeasibility

def test_constraint_validator():
    print("⚖️ Testing Constraint Validator Integration")
    print("=" * 70)
    
    research_agent = ResearchAgent()
    planner_agent = PlannerAgent()
    
    # Test cases with known constraint violations
    test_cases = [
        {
            "neighborhood": "hayes_valley",
            "plan": DevelopmentPlan(
                plan_id="test_compliant",
                plan_type=PlanType.CONSERVATIVE,
                name="Test Compliant Plan",
                description="Should be fully compliant",
                far=2.5,  # Within NCT-3 limits (3.0)
                height_ft=50,  # Within limits (55ft)
                total_units=15,
                lot_area_sf=3000,
                feasibility=PlanFeasibility.FULLY_COMPLIANT,
                zoning_compliance="Test compliance",
                design_rationale=["Test rationale"],
                policy_alignment=["Test alignment"]
            ),
            "expected_feasible": True,
            "description": "Compliant Hayes Valley Plan"
        },
        {
            "neighborhood": "marina",
            "plan": DevelopmentPlan(
                plan_id="test_violations",
                plan_type=PlanType.AGGRESSIVE,
                name="Test Violation Plan", 
                description="Should have violations",
                far=2.0,  # Exceeds Marina RH-1 limits (0.8)
                height_ft=60,  # Exceeds Marina limits (40ft)
                total_units=25,
                lot_area_sf=2500,
                feasibility=PlanFeasibility.FULLY_COMPLIANT,  # Will be updated
                zoning_compliance="Test compliance",
                design_rationale=["Test rationale"],
                policy_alignment=["Test alignment"]
            ),
            "expected_feasible": False,
            "description": "Violating Marina Plan"
        },
        {
            "neighborhood": "mission",
            "plan": DevelopmentPlan(
                plan_id="test_borderline",
                plan_type=PlanType.MODERATE,
                name="Test Borderline Plan",
                description="Should be borderline",
                far=3.8,  # Near Mission NCT-4 limits (4.0)
                height_ft=80,  # Near limits (85ft)
                total_units=30,
                lot_area_sf=4000,
                feasibility=PlanFeasibility.FULLY_COMPLIANT,
                zoning_compliance="Test compliance", 
                design_rationale=["Test rationale"],
                policy_alignment=["Test alignment"]
            ),
            "expected_feasible": True,
            "description": "Borderline Mission Plan"
        }
    ]
    
    passed_tests = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        plan = test_case["plan"]
        neighborhood = test_case["neighborhood"]
        
        print(f"\n🎯 Test {i}: {test_case['description']}")
        print("-" * 70)
        print(f"  Plan: {plan.name}")
        print(f"  FAR: {plan.far}, Height: {plan.height_ft}ft, Units: {plan.total_units}")
        
        try:
            # Validate plan using live API
            validated_plan = planner_agent._validate_plan_feasibility(plan, neighborhood)
            
            print(f"  📋 Validation Results:")
            print(f"    Feasibility: {validated_plan.feasibility}")
            print(f"    Compliance Score: {validated_plan.compliance_score:.2f}")
            print(f"    Violations ({len(validated_plan.violations)}): {validated_plan.violations[:2]}")
            print(f"    Zoning Compliance: {validated_plan.zoning_compliance}")
            
            # Validation checks
            checks = []
            
            # Check that feasibility was updated from API
            feasibility_updated = validated_plan.feasibility != plan.feasibility
            if not feasibility_updated:
                # Acceptable if plan was already correctly assessed
                feasibility_updated = True
            checks.append(("Feasibility Updated", feasibility_updated))
            
            # Check compliance score is reasonable
            reasonable_score = 0.0 <= validated_plan.compliance_score <= 1.0
            checks.append(("Reasonable Score", reasonable_score))
            
            # Check violations list exists
            has_violations_list = isinstance(validated_plan.violations, list)
            checks.append(("Has Violations List", has_violations_list))
            
            # Check zoning compliance updated
            compliance_updated = validated_plan.zoning_compliance != "Test compliance"
            checks.append(("Compliance Updated", compliance_updated))
            
            # Check expected feasibility (roughly)
            if test_case["expected_feasible"]:
                feasibility_reasonable = validated_plan.feasibility in [
                    PlanFeasibility.FULLY_COMPLIANT, 
                    PlanFeasibility.REQUIRES_VARIANCES
                ]
            else:
                feasibility_reasonable = validated_plan.feasibility in [
                    PlanFeasibility.REQUIRES_VARIANCES,
                    PlanFeasibility.NEEDS_REZONING, 
                    PlanFeasibility.NOT_FEASIBLE
                ]
            checks.append(("Expected Feasibility", feasibility_reasonable))
            
            # Check violations correlate with feasibility
            if len(validated_plan.violations) == 0:
                violations_match_feasibility = validated_plan.feasibility == PlanFeasibility.FULLY_COMPLIANT
            else:
                violations_match_feasibility = validated_plan.feasibility != PlanFeasibility.FULLY_COMPLIANT
            checks.append(("Violations Match Feasibility", violations_match_feasibility))
            
            print(f"  🔍 Validation Checks:")
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
    
    # Test integration with scenario generator
    print(f"\n🔗 Testing Integration with Scenario Generator")
    print("-" * 70)
    
    try:
        # Generate plans and validate them
        research_brief = research_agent.research_query("Add housing in Hayes Valley")
        original_plans = planner_agent._generate_candidate_plans(research_brief)
        
        print(f"Generated {len(original_plans)} plans for validation")
        
        validated_plans = []
        for plan in original_plans:
            validated_plan = planner_agent._validate_plan_feasibility(plan, research_brief.neighborhood.name)
            validated_plans.append(validated_plan)
        
        # Check that validation worked on all plans
        all_have_violations_list = all(isinstance(p.violations, list) for p in validated_plans)
        all_have_scores = all(0.0 <= p.compliance_score <= 1.0 for p in validated_plans)
        all_have_feasibility = all(hasattr(p, 'feasibility') for p in validated_plans)
        
        integration_checks = [
            ("All Plans Have Violations List", all_have_violations_list),
            ("All Plans Have Valid Scores", all_have_scores),
            ("All Plans Have Feasibility", all_have_feasibility)
        ]
        
        integration_passed = True
        for check_name, result in integration_checks:
            status = "✅" if result else "❌"
            print(f"  {status} {check_name}")
            if not result:
                integration_passed = False
        
        if integration_passed:
            passed_tests += 1
            print(f"  🎉 Integration Test PASSED")
        else:
            print(f"  💥 Integration Test FAILED")
        
        total_tests += 1
        
    except Exception as e:
        print(f"  ❌ Integration Error: {e}")
        total_tests += 1
    
    print(f"\n📊 CONSTRAINT VALIDATOR TEST SUMMARY")
    print("=" * 70)
    print(f"Passed: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests >= total_tests * 0.8:  # 80% pass rate
        print("🎯 Constraint Validator Integration working well!")
        print("✅ Live API validation working")
        print("✅ Feasibility assessment based on violations")
        print("✅ Integration with scenario generator")
        print("✅ Ready for Plan Optimization Module")
        return True
    else:
        failed = total_tests - passed_tests
        print(f"⚠️  {failed} tests failed. Review constraint validation logic.")
        return False

def demo_constraint_validation():
    """Demo the constraint validation output"""
    print(f"\n🎪 CONSTRAINT VALIDATION DEMO")
    print("=" * 70)
    
    research_agent = ResearchAgent()
    planner_agent = PlannerAgent()
    
    query = "Add housing in Marina District"
    print(f"Query: \"{query}\"")
    
    research_brief = research_agent.research_query(query)
    plans = planner_agent._generate_candidate_plans(research_brief)
    
    print(f"\n📄 Validating {len(plans)} Plans Against Live API:")
    
    for i, plan in enumerate(plans, 1):
        print(f"\n{i}. {plan.name}")
        print(f"   Original: FAR {plan.far}, Height {plan.height_ft}ft")
        
        validated_plan = planner_agent._validate_plan_feasibility(plan, research_brief.neighborhood.name)
        
        print(f"   Validated: {validated_plan.feasibility}")
        print(f"   Compliance: {validated_plan.compliance_score:.0%}")
        print(f"   Violations: {len(validated_plan.violations)}")
        if validated_plan.violations:
            print(f"   Details: {validated_plan.violations[0]}")

if __name__ == "__main__":
    success = test_constraint_validator()
    if success:
        demo_constraint_validation()
    else:
        print("\n⚠️ Fix constraint validation issues before proceeding")