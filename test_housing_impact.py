#!/usr/bin/env python3
"""
Test the Housing Impact Module for Evaluator Agent
Verifies calculation of before/after housing impacts and demographic effects
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

# Load Evaluator Agent
evaluator_spec = importlib.util.spec_from_file_location("evaluator_agent", 
    os.path.join(os.path.dirname(__file__), 'backend', 'app', 'agents', 'evaluator_agent.py'))
evaluator_agent_module = importlib.util.module_from_spec(evaluator_spec)
evaluator_spec.loader.exec_module(evaluator_agent_module)

ResearchAgent = research_agent_module.ResearchAgent
PlannerAgent = planner_agent_module.PlannerAgent
EvaluatorAgent = evaluator_agent_module.EvaluatorAgent
HousingImpact = evaluator_agent_module.HousingImpact

def test_housing_impact_module():
    print("🏠 Testing Housing Impact Module")
    print("=" * 65)
    
    research_agent = ResearchAgent()
    planner_agent = PlannerAgent()
    evaluator_agent = EvaluatorAgent()
    
    # Test cases covering different housing scenarios
    test_cases = [
        {
            "query": "Add 50 affordable housing units near BART in Hayes Valley",
            "neighborhood": "Hayes Valley",
            "expected_housing_focus": True,
            "description": "High-Density Affordable Development"
        },
        {
            "query": "Add small-scale housing in Marina while respecting character",
            "neighborhood": "Marina District", 
            "expected_housing_focus": True,
            "description": "Low-Density Character Preservation"
        },
        {
            "query": "Increase density in Mission without displacing residents",
            "neighborhood": "Mission District",
            "expected_housing_focus": True,
            "description": "Anti-Displacement Dense Development"
        }
    ]
    
    passed_tests = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        query = test_case["query"]
        neighborhood = test_case["neighborhood"]
        
        print(f"\n🎯 Test {i}: {test_case['description']}")
        print("-" * 65)
        print(f"  Query: {query}")
        print(f"  Neighborhood: {neighborhood}")
        
        try:
            # Generate full pipeline: Agent 1 → Agent 2 → Agent 3
            research_brief = research_agent.research_query(query)
            planning_alternatives = planner_agent.generate_scenarios(research_brief)
            scenario_comparison = evaluator_agent.evaluate_scenarios(planning_alternatives)
            
            # Focus on housing impact analysis
            print(f"\n  🏠 Housing Impact Analysis:")
            
            housing_impacts = [impact.housing_impact for impact in scenario_comparison.plan_impacts]
            
            for j, housing_impact in enumerate(housing_impacts[:3], 1):  # Show first 3
                print(f"    {j}. Current: {housing_impact.current_units}, " +
                      f"Projected: {housing_impact.projected_units} " +
                      f"(+{housing_impact.net_new_units})")
                print(f"       Affordable: +{housing_impact.affordable_units_added}, " +
                      f"Market Rate: +{housing_impact.market_rate_units_added}")
                print(f"       Displacement Risk: {housing_impact.displacement_risk_score:.1%}, " +
                      f"Affordability: {housing_impact.affordability_improvement:.1f}%")
                print(f"       Population: +{housing_impact.population_capacity_change} residents")
            
            # Validation checks
            print(f"\n  🔍 Housing Impact Validation:")
            
            validation_checks = []
            
            # Check that housing numbers are reasonable
            all_positive_units = all(h.net_new_units > 0 for h in housing_impacts)
            validation_checks.append(("All Plans Add Housing Units", all_positive_units))
            
            # Check that current < projected always
            proper_before_after = all(h.current_units < h.projected_units for h in housing_impacts)
            validation_checks.append(("Proper Before/After Logic", proper_before_after))
            
            # Check that affordable + market rate = total
            proper_unit_breakdown = all(
                abs((h.affordable_units_added + h.market_rate_units_added) - h.net_new_units) <= 1
                for h in housing_impacts
            )
            validation_checks.append(("Unit Breakdown Correct", proper_unit_breakdown))
            
            # Check displacement risk is reasonable (0-100%)
            reasonable_displacement = all(0 <= h.displacement_risk_score <= 1 for h in housing_impacts)
            validation_checks.append(("Displacement Risk Reasonable", reasonable_displacement))
            
            # Check affordability improvement logic
            affordability_logical = all(
                (h.affordability_improvement > 0) == (h.affordable_units_added > 0)
                for h in housing_impacts
            )
            validation_checks.append(("Affordability Logic Correct", affordability_logical))
            
            # Check population estimate is reasonable
            reasonable_population = all(
                h.population_capacity_change == h.net_new_units * 2  # 2 people per unit
                for h in housing_impacts
            )
            validation_checks.append(("Population Estimates Reasonable", reasonable_population))
            
            # Check neighborhood-specific logic
            neighborhood_appropriate = True
            if neighborhood == "Marina District":
                # Marina should have lower displacement risk due to affluent area
                avg_displacement = sum(h.displacement_risk_score for h in housing_impacts) / len(housing_impacts)
                neighborhood_appropriate = avg_displacement < 0.6
            elif neighborhood == "Mission District":
                # Mission should show sensitivity to displacement
                has_anti_displacement_measures = any(h.displacement_risk_score < 0.4 for h in housing_impacts)
                neighborhood_appropriate = has_anti_displacement_measures
            
            validation_checks.append(("Neighborhood-Specific Logic", neighborhood_appropriate))
            
            # Display validation results
            all_passed = True
            for check_name, result in validation_checks:
                status = "✅" if result else "❌"
                print(f"    {status} {check_name}")
                if not result:
                    all_passed = False
            
            # Test variety across plans
            print(f"\n  📊 Housing Impact Variety:")
            
            # Check that different plan types show different impacts
            displacement_scores = [h.displacement_risk_score for h in housing_impacts]
            affordability_scores = [h.affordability_improvement for h in housing_impacts]
            unit_counts = [h.net_new_units for h in housing_impacts]
            
            variety_checks = [
                ("Displacement Risk Varies", len(set(f"{s:.2f}" for s in displacement_scores)) > 1),
                ("Unit Counts Vary", len(set(unit_counts)) > 1),
                ("Affordability Varies", len(set(f"{s:.1f}" for s in affordability_scores)) > 1)
            ]
            
            for check_name, result in variety_checks:
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
    
    # Test housing impact calculation methodology
    print(f"\n🧮 Testing Housing Impact Calculation Methodology")
    print("-" * 65)
    
    try:
        # Test specific calculation components
        research_brief = research_agent.research_query("Test housing calculation in Hayes Valley")
        plans = planner_agent._generate_candidate_plans(research_brief)
        
        methodology_tests = []
        
        for plan in plans[:2]:  # Test first 2 plans
            housing_impact = evaluator_agent._calculate_housing_impact(plan, research_brief.neighborhood.name)
            
            # Test API baseline integration
            has_baseline = housing_impact.current_units > 0
            methodology_tests.append(("API Baseline Integration", has_baseline))
            
            # Test displacement risk factors
            risk_factors_reasonable = True
            if hasattr(plan, 'plan_type'):
                if plan.plan_type.value == "aggressive":
                    risk_factors_reasonable = housing_impact.displacement_risk_score > 0.2
                elif plan.plan_type.value == "conservative":
                    risk_factors_reasonable = housing_impact.displacement_risk_score < 0.7
            methodology_tests.append(("Displacement Risk Factors", risk_factors_reasonable))
            
            # Test affordability calculation
            if hasattr(plan, 'affordable_percentage') and plan.affordable_percentage:
                expected_improvement = plan.affordable_percentage * 100
                affordability_correct = abs(housing_impact.affordability_improvement - expected_improvement) < 5
            else:
                affordability_correct = housing_impact.affordability_improvement >= 0
            methodology_tests.append(("Affordability Calculation", affordability_correct))
        
        print(f"  📊 Methodology Validation:")
        methodology_passed = True
        for check_name, result in methodology_tests:
            status = "✅" if result else "❌"
            print(f"    {status} {check_name}")
            if not result:
                methodology_passed = False
        
        if methodology_passed:
            passed_tests += 1
        
        total_tests += 1
        
    except Exception as e:
        print(f"  ❌ Methodology Error: {e}")
        total_tests += 1
    
    print(f"\n📊 HOUSING IMPACT MODULE TEST SUMMARY")
    print("=" * 65)
    print(f"Passed: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests >= total_tests * 0.8:  # 80% pass rate
        print("🎯 Housing Impact Module working well!")
        print("✅ Before/after housing impact calculations")
        print("✅ Displacement risk assessment methodology")
        print("✅ Affordability impact tracking") 
        print("✅ Neighborhood-specific housing logic")
        print("✅ Ready for Accessibility Analysis Module")
        return True
    else:
        failed = total_tests - passed_tests
        print(f"⚠️  {failed} tests failed. Review housing impact calculations.")
        return False

def demo_housing_impact_analysis():
    """Demo the housing impact analysis output"""
    print(f"\n🎪 HOUSING IMPACT ANALYSIS DEMO")
    print("=" * 65)
    
    research_agent = ResearchAgent()
    planner_agent = PlannerAgent()
    evaluator_agent = EvaluatorAgent()
    
    query = "Add 30 affordable housing units in Hayes Valley"
    print(f"Query: \"{query}\"")
    
    research_brief = research_agent.research_query(query)
    planning_alternatives = planner_agent.generate_scenarios(research_brief)
    scenario_comparison = evaluator_agent.evaluate_scenarios(planning_alternatives)
    
    print(f"\n🏠 Housing Impact Analysis for {len(scenario_comparison.plan_impacts)} Plans:")
    
    for i, impact in enumerate(scenario_comparison.plan_impacts, 1):
        housing = impact.housing_impact
        print(f"\n{i}. {impact.plan_name}")
        print(f"   📊 Housing Numbers:")
        print(f"      Before: {housing.current_units} units")
        print(f"      After: {housing.projected_units} units (+{housing.net_new_units})")
        print(f"      Breakdown: {housing.affordable_units_added} affordable, {housing.market_rate_units_added} market rate")
        
        print(f"   🏘️ Community Impact:")
        print(f"      Displacement Risk: {housing.displacement_risk_score:.1%}")
        print(f"      Affordability Improvement: {housing.affordability_improvement:.1f}%")
        print(f"      New Residents: ~{housing.population_capacity_change} people")
        
        print(f"   💡 Key Benefits:")
        for benefit in impact.key_benefits[:2]:
            print(f"      • {benefit}")
        
        print(f"   ⚠️ Key Concerns:")
        for concern in impact.key_concerns[:2]:
            print(f"      • {concern}")

if __name__ == "__main__":
    success = test_housing_impact_module()
    if success:
        demo_housing_impact_analysis()
    else:
        print("\n⚠️ Fix housing impact issues before proceeding")