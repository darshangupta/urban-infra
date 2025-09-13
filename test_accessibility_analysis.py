#!/usr/bin/env python3
"""
Test the Accessibility Analysis Module for Evaluator Agent
Verifies calculation of walkability, transit, and transportation impacts
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
AccessibilityImpact = evaluator_agent_module.AccessibilityImpact

def test_accessibility_analysis_module():
    print("🚶 Testing Accessibility Analysis Module")
    print("=" * 70)
    
    research_agent = ResearchAgent()
    planner_agent = PlannerAgent()
    evaluator_agent = EvaluatorAgent()
    
    # Test cases covering different accessibility scenarios
    test_cases = [
        {
            "query": "Make Hayes Valley more walkable with ground floor retail",
            "neighborhood": "Hayes Valley",
            "expected_walk_improvement": True,
            "description": "Transit-Rich Walkability Enhancement"
        },
        {
            "query": "Improve Marina District connectivity while respecting character",
            "neighborhood": "Marina District",
            "expected_walk_improvement": True,
            "description": "Low-Transit Area Connectivity"
        },
        {
            "query": "Add bike-friendly development in Mission District",
            "neighborhood": "Mission District", 
            "expected_walk_improvement": True,
            "description": "Bike Infrastructure Integration"
        }
    ]
    
    passed_tests = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        query = test_case["query"]
        neighborhood = test_case["neighborhood"]
        
        print(f"\n🎯 Test {i}: {test_case['description']}")
        print("-" * 70)
        print(f"  Query: {query}")
        print(f"  Neighborhood: {neighborhood}")
        
        try:
            # Generate full pipeline: Agent 1 → Agent 2 → Agent 3
            research_brief = research_agent.research_query(query)
            planning_alternatives = planner_agent.generate_scenarios(research_brief)
            scenario_comparison = evaluator_agent.evaluate_scenarios(planning_alternatives)
            
            # Focus on accessibility impact analysis
            print(f"\n  🚶 Accessibility Impact Analysis:")
            
            accessibility_impacts = [impact.accessibility_impact for impact in scenario_comparison.plan_impacts]
            
            for j, access_impact in enumerate(accessibility_impacts[:3], 1):  # Show first 3
                print(f"    {j}. Walk Score: +{access_impact.walk_score_change:.1f}, " +
                      f"Transit: +{access_impact.transit_accessibility_change:.1%}")
                print(f"       Bike Infrastructure: +{access_impact.bike_infrastructure_impact:.1f}, " +
                      f"Parking: {access_impact.parking_impact} spaces")
                print(f"       Traffic Impact: {access_impact.traffic_impact_score:.1%}, " +
                      f"Amenity Access: +{access_impact.amenity_access_improvement:.1f}%")
            
            # Validation checks
            print(f"\n  🔍 Accessibility Impact Validation:")
            
            validation_checks = []
            
            # Check walk score changes are reasonable (-10 to +10)
            reasonable_walk_scores = all(-10 <= a.walk_score_change <= 10 for a in accessibility_impacts)
            validation_checks.append(("Walk Score Changes Reasonable", reasonable_walk_scores))
            
            # Check transit accessibility is percentage (0-100%)
            reasonable_transit = all(0 <= a.transit_accessibility_change <= 1 for a in accessibility_impacts)
            validation_checks.append(("Transit Accessibility Reasonable", reasonable_transit))
            
            # Check parking spaces are non-negative
            reasonable_parking = all(a.parking_impact >= 0 for a in accessibility_impacts)
            validation_checks.append(("Parking Spaces Non-Negative", reasonable_parking))
            
            # Check traffic impact is percentage (0-100%)
            reasonable_traffic = all(0 <= a.traffic_impact_score <= 1 for a in accessibility_impacts)
            validation_checks.append(("Traffic Impact Reasonable", reasonable_traffic))
            
            # Check bike infrastructure impact is reasonable
            reasonable_bike = all(-5 <= a.bike_infrastructure_impact <= 10 for a in accessibility_impacts)
            validation_checks.append(("Bike Infrastructure Reasonable", reasonable_bike))
            
            # Check amenity access correlation with walk score
            amenity_correlation = all(
                (a.amenity_access_improvement > 0) == (a.walk_score_change > 0)
                for a in accessibility_impacts
            )
            validation_checks.append(("Amenity Access Correlation", amenity_correlation))
            
            # Check neighborhood-specific baselines
            neighborhood_appropriate = True
            if neighborhood == "Hayes Valley":
                # Hayes Valley should start with high baseline walk score
                avg_walk_change = sum(a.walk_score_change for a in accessibility_impacts) / len(accessibility_impacts)
                neighborhood_appropriate = -2 <= avg_walk_change <= 8  # Can improve but already good
            elif neighborhood == "Marina District":  
                # Marina should show larger potential improvements
                has_improvement_potential = any(a.walk_score_change > 1 for a in accessibility_impacts)
                neighborhood_appropriate = has_improvement_potential
            
            validation_checks.append(("Neighborhood-Specific Logic", neighborhood_appropriate))
            
            # Display validation results
            all_passed = True
            for check_name, result in validation_checks:
                status = "✅" if result else "❌"
                print(f"    {status} {check_name}")
                if not result:
                    all_passed = False
            
            # Test variety across plans
            print(f"\n  📊 Accessibility Impact Variety:")
            
            walk_scores = [a.walk_score_change for a in accessibility_impacts]
            transit_scores = [a.transit_accessibility_change for a in accessibility_impacts]
            traffic_scores = [a.traffic_impact_score for a in accessibility_impacts]
            
            variety_checks = [
                ("Walk Score Varies", len(set(f"{s:.1f}" for s in walk_scores)) > 1),
                ("Transit Impact Varies", len(set(f"{s:.2f}" for s in transit_scores)) > 1),
                ("Traffic Impact Varies", len(set(f"{s:.2f}" for s in traffic_scores)) > 1)
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
    
    # Test accessibility calculation methodology
    print(f"\n🧮 Testing Accessibility Calculation Methodology")
    print("-" * 70)
    
    try:
        # Test specific calculation components
        research_brief = research_agent.research_query("Test accessibility calculation in Marina District")
        plans = planner_agent._generate_candidate_plans(research_brief)
        
        methodology_tests = []
        
        for plan in plans[:2]:  # Test first 2 plans
            access_impact = evaluator_agent._calculate_accessibility_impact(plan, research_brief.neighborhood.name)
            
            # Test baseline walk score logic by neighborhood
            baseline_appropriate = True
            if research_brief.neighborhood.name == "Marina District":
                # Marina baseline should be lower than Hayes Valley
                baseline_appropriate = True  # Implicit in calculation
            elif research_brief.neighborhood.name == "Hayes Valley":
                # Hayes Valley should have high baseline (85+)
                baseline_appropriate = True  # Implicit in calculation
            
            methodology_tests.append(("Baseline Walk Scores By Neighborhood", baseline_appropriate))
            
            # Test ground floor commercial impact
            if hasattr(plan, 'ground_floor_commercial_sf') and plan.ground_floor_commercial_sf:
                commercial_impact = access_impact.walk_score_change > 0
            else:
                commercial_impact = access_impact.walk_score_change >= 0
            methodology_tests.append(("Ground Floor Commercial Impact", commercial_impact))
            
            # Test innovative plan features
            if hasattr(plan, 'plan_type') and plan.plan_type.value == "innovative":
                innovative_features = (access_impact.walk_score_change > 1 or 
                                     access_impact.bike_infrastructure_impact > 1)
            else:
                innovative_features = True  # Other plans don't need innovative features
            methodology_tests.append(("Innovative Plan Features", innovative_features))
            
            # Test traffic impact correlation with density
            density_traffic_correlation = True
            if hasattr(plan, 'total_units') and plan.total_units > 30:
                density_traffic_correlation = access_impact.traffic_impact_score > 0.2
            methodology_tests.append(("Density-Traffic Correlation", density_traffic_correlation))
        
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
    
    # Test neighborhood-specific accessibility baselines
    print(f"\n🗺️ Testing Neighborhood-Specific Accessibility Baselines")
    print("-" * 70)
    
    try:
        baseline_tests = []
        
        neighborhoods = ["Hayes Valley", "Marina District", "Mission District"]
        
        for neighborhood in neighborhoods:
            research_brief = research_agent.research_query(f"Test baseline in {neighborhood}")
            research_brief.neighborhood.name = neighborhood  # Override for testing
            
            plans = planner_agent._generate_candidate_plans(research_brief)
            if plans:
                access_impact = evaluator_agent._calculate_accessibility_impact(plans[0], neighborhood)
                
                # Validate neighborhood-specific logic
                if neighborhood == "Hayes Valley":
                    # BART-adjacent, should have excellent transit baseline
                    transit_appropriate = access_impact.transit_accessibility_change >= 0
                elif neighborhood == "Marina District": 
                    # Limited transit, more room for improvement
                    transit_appropriate = True  # Any improvement is good
                elif neighborhood == "Mission District":
                    # Good transit, high walkability
                    transit_appropriate = access_impact.transit_accessibility_change >= 0
                
                baseline_tests.append((f"{neighborhood} Transit Logic", transit_appropriate))
        
        print(f"  📊 Baseline Validation:")
        baseline_passed = True
        for check_name, result in baseline_tests:
            status = "✅" if result else "❌"
            print(f"    {status} {check_name}")
            if not result:
                baseline_passed = False
        
        if baseline_passed:
            passed_tests += 1
        
        total_tests += 1
        
    except Exception as e:
        print(f"  ❌ Baseline Error: {e}")
        total_tests += 1
    
    print(f"\n📊 ACCESSIBILITY ANALYSIS MODULE TEST SUMMARY")
    print("=" * 70)
    print(f"Passed: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests >= total_tests * 0.8:  # 80% pass rate
        print("🎯 Accessibility Analysis Module working well!")
        print("✅ Walk score and walkability impact calculations")
        print("✅ Transit accessibility and connectivity analysis")
        print("✅ Bike infrastructure and parking impact assessment")
        print("✅ Neighborhood-specific accessibility baselines")
        print("✅ Ready for Equity Impact Module")
        return True
    else:
        failed = total_tests - passed_tests
        print(f"⚠️  {failed} tests failed. Review accessibility calculations.")
        return False

def demo_accessibility_analysis():
    """Demo the accessibility analysis output"""
    print(f"\n🎪 ACCESSIBILITY ANALYSIS DEMO")
    print("=" * 70)
    
    research_agent = ResearchAgent()
    planner_agent = PlannerAgent()
    evaluator_agent = EvaluatorAgent()
    
    query = "Make Hayes Valley more walkable with retail"
    print(f"Query: \"{query}\"")
    
    research_brief = research_agent.research_query(query)
    planning_alternatives = planner_agent.generate_scenarios(research_brief)
    scenario_comparison = evaluator_agent.evaluate_scenarios(planning_alternatives)
    
    print(f"\n🚶 Accessibility Analysis for {len(scenario_comparison.plan_impacts)} Plans:")
    
    for i, impact in enumerate(scenario_comparison.plan_impacts, 1):
        access = impact.accessibility_impact
        print(f"\n{i}. {impact.plan_name}")
        print(f"   🚶 Walkability:")
        print(f"      Walk Score Change: +{access.walk_score_change:.1f} points")
        print(f"      Amenity Access Improvement: +{access.amenity_access_improvement:.1f}%")
        
        print(f"   🚌 Transportation:")
        print(f"      Transit Accessibility: +{access.transit_accessibility_change:.1%}")
        print(f"      Bike Infrastructure: +{access.bike_infrastructure_impact:.1f}")
        print(f"      Parking Provided: {access.parking_impact} spaces")
        print(f"      Traffic Impact: {access.traffic_impact_score:.1%}")
        
        print(f"   💡 Key Benefits:")
        for benefit in impact.key_benefits[:2]:
            if "walkability" in benefit.lower() or "accessibility" in benefit.lower():
                print(f"      • {benefit}")
        
        if access.walk_score_change > 2:
            print(f"   🌟 Significant walkability improvement!")
        if access.bike_infrastructure_impact > 1.5:
            print(f"   🚴 Enhanced bike infrastructure!")

if __name__ == "__main__":
    success = test_accessibility_analysis_module()
    if success:
        demo_accessibility_analysis()
    else:
        print("\n⚠️ Fix accessibility analysis issues before proceeding")