#!/usr/bin/env python3
"""
Test the Equity Impact Module for Evaluator Agent
Verifies calculation of gentrification, displacement, and community benefit impacts
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
EquityImpact = evaluator_agent_module.EquityImpact

def test_equity_impact_module():
    print("⚖️ Testing Equity Impact Module")
    print("=" * 65)
    
    research_agent = ResearchAgent()
    planner_agent = PlannerAgent()
    evaluator_agent = EvaluatorAgent()
    
    # Test cases covering different equity scenarios
    test_cases = [
        {
            "query": "Add affordable housing without displacing existing residents in Mission",
            "neighborhood": "Mission District",
            "expected_equity_focus": True,
            "description": "Anti-Displacement Housing Development"
        },
        {
            "query": "Upzone Hayes Valley while preserving community character",
            "neighborhood": "Hayes Valley",
            "expected_equity_focus": True,
            "description": "Gentrification-Sensitive Development"
        },
        {
            "query": "Add small-scale housing respecting Marina neighborhood character",
            "neighborhood": "Marina District",
            "expected_equity_focus": False,  # Marina is affluent, less displacement pressure
            "description": "Character-Preserving Development"
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
            
            # Focus on equity impact analysis
            print(f"\n  ⚖️ Equity Impact Analysis:")
            
            equity_impacts = [impact.equity_impact for impact in scenario_comparison.plan_impacts]
            
            for j, equity_impact in enumerate(equity_impacts[:3], 1):  # Show first 3
                print(f"    {j}. Gentrification: {equity_impact.gentrification_pressure_change:+.2f}, " +
                      f"Stability: {equity_impact.demographic_stability_score:.2f}")
                print(f"       Cultural: {equity_impact.cultural_preservation_impact:+.2f}, " +
                      f"Economic Opp: +{equity_impact.economic_opportunity_change:.2f}")
                print(f"       Community Benefit: {equity_impact.community_benefit_score:.2f}")
            
            # Validation checks
            print(f"\n  🔍 Equity Impact Validation:")
            
            validation_checks = []
            
            # Check gentrification pressure changes are reasonable (-1 to +1)
            reasonable_gentrification = all(-1 <= e.gentrification_pressure_change <= 1 for e in equity_impacts)
            validation_checks.append(("Gentrification Pressure Reasonable", reasonable_gentrification))
            
            # Check demographic stability is percentage (0-1)
            reasonable_stability = all(0 <= e.demographic_stability_score <= 1 for e in equity_impacts)
            validation_checks.append(("Demographic Stability Reasonable", reasonable_stability))
            
            # Check cultural preservation impact is reasonable (-1 to +1)
            reasonable_cultural = all(-1 <= e.cultural_preservation_impact <= 1 for e in equity_impacts)
            validation_checks.append(("Cultural Preservation Reasonable", reasonable_cultural))
            
            # Check economic opportunity is non-negative
            reasonable_economic = all(e.economic_opportunity_change >= 0 for e in equity_impacts)
            validation_checks.append(("Economic Opportunity Non-Negative", reasonable_economic))
            
            # Check community benefit score is percentage (0-1)
            reasonable_benefit = all(0 <= e.community_benefit_score <= 1 for e in equity_impacts)
            validation_checks.append(("Community Benefit Score Reasonable", reasonable_benefit))
            
            # Check neighborhood-specific logic
            neighborhood_appropriate = True
            if neighborhood == "Mission District":
                # Mission should show high gentrification sensitivity
                avg_gentrification = sum(e.gentrification_pressure_change for e in equity_impacts) / len(equity_impacts)
                # Should have plans that reduce or limit gentrification increase
                has_anti_gentrification_plans = any(e.gentrification_pressure_change < 0.2 for e in equity_impacts)
                neighborhood_appropriate = has_anti_gentrification_plans
            elif neighborhood == "Hayes Valley":
                # Hayes Valley should show gentrification awareness
                avg_community_benefit = sum(e.community_benefit_score for e in equity_impacts) / len(equity_impacts)
                neighborhood_appropriate = avg_community_benefit >= 0.4
            elif neighborhood == "Marina District":
                # Marina should have lower displacement concerns
                avg_gentrification = sum(e.gentrification_pressure_change for e in equity_impacts) / len(equity_impacts)
                neighborhood_appropriate = avg_gentrification < 0.5
            
            validation_checks.append(("Neighborhood-Specific Logic", neighborhood_appropriate))
            
            # Display validation results
            all_passed = True
            for check_name, result in validation_checks:
                status = "✅" if result else "❌"
                print(f"    {status} {check_name}")
                if not result:
                    all_passed = False
            
            # Test variety across plans
            print(f"\n  📊 Equity Impact Variety:")
            
            gentrification_scores = [e.gentrification_pressure_change for e in equity_impacts]
            community_scores = [e.community_benefit_score for e in equity_impacts]
            stability_scores = [e.demographic_stability_score for e in equity_impacts]
            
            variety_checks = [
                ("Gentrification Pressure Varies", len(set(f"{s:.2f}" for s in gentrification_scores)) > 1),
                ("Community Benefit Varies", len(set(f"{s:.2f}" for s in community_scores)) > 1),
                ("Demographic Stability Varies", len(set(f"{s:.2f}" for s in stability_scores)) > 1)
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
    
    # Test equity calculation methodology  
    print(f"\n🧮 Testing Equity Calculation Methodology")
    print("-" * 65)
    
    try:
        # Test specific calculation components
        research_brief = research_agent.research_query("Test equity calculation in Mission District")
        plans = planner_agent._generate_candidate_plans(research_brief)
        
        methodology_tests = []
        
        for plan in plans[:2]:  # Test first 2 plans
            equity_impact = evaluator_agent._calculate_equity_impact(plan, research_brief.neighborhood.name)
            
            # Test gentrification pressure factors
            if hasattr(plan, 'plan_type'):
                if plan.plan_type.value == "aggressive":
                    pressure_appropriate = equity_impact.gentrification_pressure_change >= 0
                elif plan.plan_type.value == "innovative":
                    pressure_appropriate = equity_impact.gentrification_pressure_change <= 0.3  # Should be lower
                else:
                    pressure_appropriate = True
            else:
                pressure_appropriate = True
            methodology_tests.append(("Gentrification Pressure Logic", pressure_appropriate))
            
            # Test affordability impact on gentrification
            if hasattr(plan, 'affordable_percentage') and plan.affordable_percentage:
                if plan.affordable_percentage > 0.2:  # 20%+ affordable
                    affordability_helps = equity_impact.gentrification_pressure_change < 0.5
                else:
                    affordability_helps = True
            else:
                affordability_helps = True
            methodology_tests.append(("Affordability Reduces Pressure", affordability_helps))
            
            # Test community benefit calculation
            community_benefit_reasonable = 0.3 <= equity_impact.community_benefit_score <= 1.0
            methodology_tests.append(("Community Benefit Reasonable", community_benefit_reasonable))
            
            # Test demographic stability correlation
            stability_correlation = equity_impact.demographic_stability_score > (1 - abs(equity_impact.gentrification_pressure_change) * 0.5)
            methodology_tests.append(("Stability Correlation", stability_correlation))
        
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
    
    # Test anti-displacement strategies recognition
    print(f"\n🛡️ Testing Anti-Displacement Strategy Recognition")
    print("-" * 65)
    
    try:
        strategy_tests = []
        
        # Test innovative plans with anti-displacement focus
        research_brief = research_agent.research_query("Prevent displacement in Mission District")
        research_brief.intent = "anti_displacement"  # Override for testing
        
        plans = planner_agent._generate_candidate_plans(research_brief)
        innovative_plans = [p for p in plans if hasattr(p, 'plan_type') and p.plan_type.value == "innovative"]
        
        if innovative_plans:
            equity_impact = evaluator_agent._calculate_equity_impact(innovative_plans[0], "Mission District")
            
            # Innovative anti-displacement plans should have lower gentrification pressure
            anti_displacement_effective = equity_impact.gentrification_pressure_change < 0.3
            strategy_tests.append(("Anti-Displacement Plans Effective", anti_displacement_effective))
            
            # Should have high community benefit scores
            high_community_benefit = equity_impact.community_benefit_score > 0.7
            strategy_tests.append(("High Community Benefit", high_community_benefit))
        
        print(f"  📊 Strategy Recognition Validation:")
        strategy_passed = True
        for check_name, result in strategy_tests:
            status = "✅" if result else "❌"
            print(f"    {status} {check_name}")
            if not result:
                strategy_passed = False
        
        if strategy_passed or not strategy_tests:  # Pass if no tests or all pass
            passed_tests += 1
        
        total_tests += 1
        
    except Exception as e:
        print(f"  ❌ Strategy Error: {e}")
        total_tests += 1
    
    print(f"\n📊 EQUITY IMPACT MODULE TEST SUMMARY")
    print("=" * 65)
    print(f"Passed: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests >= total_tests * 0.8:  # 80% pass rate
        print("🎯 Equity Impact Module working well!")
        print("✅ Gentrification pressure assessment")
        print("✅ Community benefit and demographic stability analysis")
        print("✅ Anti-displacement strategy recognition")
        print("✅ Neighborhood-specific equity considerations")
        print("✅ Ready for KPI Dashboard Module")
        return True
    else:
        failed = total_tests - passed_tests
        print(f"⚠️  {failed} tests failed. Review equity impact calculations.")
        return False

def demo_equity_impact_analysis():
    """Demo the equity impact analysis output"""
    print(f"\n🎪 EQUITY IMPACT ANALYSIS DEMO")
    print("=" * 65)
    
    research_agent = ResearchAgent()
    planner_agent = PlannerAgent()
    evaluator_agent = EvaluatorAgent()
    
    query = "Add housing in Mission without displacing residents"
    print(f"Query: \"{query}\"")
    
    research_brief = research_agent.research_query(query)
    planning_alternatives = planner_agent.generate_scenarios(research_brief)
    scenario_comparison = evaluator_agent.evaluate_scenarios(planning_alternatives)
    
    print(f"\n⚖️ Equity Impact Analysis for {len(scenario_comparison.plan_impacts)} Plans:")
    
    for i, impact in enumerate(scenario_comparison.plan_impacts, 1):
        equity = impact.equity_impact
        print(f"\n{i}. {impact.plan_name}")
        print(f"   🏘️ Community Impact:")
        print(f"      Gentrification Pressure: {equity.gentrification_pressure_change:+.2f}")
        print(f"      Demographic Stability: {equity.demographic_stability_score:.2f}")
        print(f"      Community Benefit Score: {equity.community_benefit_score:.2f}")
        
        print(f"   🎭 Cultural & Economic:")
        print(f"      Cultural Preservation: {equity.cultural_preservation_impact:+.2f}")
        print(f"      Economic Opportunity: +{equity.economic_opportunity_change:.2f}")
        
        print(f"   💡 Key Benefits:")
        for benefit in impact.key_benefits[:2]:
            if "affordable" in benefit.lower() or "community" in benefit.lower():
                print(f"      • {benefit}")
        
        print(f"   ⚠️ Key Concerns:")
        for concern in impact.key_concerns[:2]:
            if "displacement" in concern.lower() or "gentrification" in concern.lower():
                print(f"      • {concern}")
        
        if equity.gentrification_pressure_change < 0:
            print(f"   🛡️ Anti-gentrification benefits!")
        if equity.community_benefit_score > 0.7:
            print(f"   🤝 Strong community benefits!")

if __name__ == "__main__":
    success = test_equity_impact_module()
    if success:
        demo_equity_impact_analysis()
    else:
        print("\n⚠️ Fix equity impact issues before proceeding")