#!/usr/bin/env python3
"""
Complete Integration Test for Agent 3 (Evaluator)
Tests the full Agent 1 → Agent 2 → Agent 3 workflow with comprehensive impact analysis
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

def test_complete_evaluator_agent():
    print("🎯 Testing Complete Agent 3 (Evaluator) Integration")
    print("=" * 80)
    
    research_agent = ResearchAgent()
    planner_agent = PlannerAgent()
    evaluator_agent = EvaluatorAgent()
    
    # Comprehensive test cases covering different impact analysis scenarios
    test_cases = [
        {
            "query": "Add 50 affordable housing units near BART in Hayes Valley",
            "expected": {
                "min_impacts": 3,
                "has_recommended": True,
                "has_kpi_dashboard": True,
                "neighborhood": "Hayes Valley"
            }
        },
        {
            "query": "Make Marina District more walkable while respecting flood risk",
            "expected": {
                "min_impacts": 3,
                "has_recommended": True,
                "has_kpi_dashboard": True,
                "neighborhood": "Marina District"
            }
        },
        {
            "query": "Prevent displacement while increasing density in Mission District",
            "expected": {
                "min_impacts": 3,
                "has_recommended": True,
                "has_kpi_dashboard": True,
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
        print("-" * 80)
        
        try:
            # Step 1: Generate research brief from Agent 1
            print("📋 Step 1: Research Brief Generation")
            research_brief = research_agent.research_query(query)
            print(f"  ✅ Research Brief: {research_brief.neighborhood.display_name}, {research_brief.intent}")
            
            # Step 2: Generate planning alternatives with Agent 2
            print("🏗️ Step 2: Planning Alternatives Generation")
            planning_alternatives = planner_agent.generate_scenarios(research_brief)
            print(f"  ✅ Planning Alternatives: {len(planning_alternatives.plans)} plans, recommended: {planning_alternatives.recommended_plan_id}")
            
            # Step 3: Generate comprehensive impact analysis with Agent 3
            print("📊 Step 3: Comprehensive Impact Analysis")
            scenario_comparison = evaluator_agent.evaluate_scenarios(planning_alternatives)
            
            print(f"  📊 Generated Impact Analysis:")
            print(f"    Scenario: {scenario_comparison.scenario_name}")
            print(f"    Plan Impacts: {len(scenario_comparison.plan_impacts)}")
            print(f"    Recommended: {scenario_comparison.recommended_plan_id}")
            print(f"    Analysis Confidence: {scenario_comparison.analysis_confidence:.0%}")
            
            # Display detailed impact analysis for first few plans
            for j, impact in enumerate(scenario_comparison.plan_impacts[:3], 1):
                print(f"    {j}. {impact.plan_name}")
                print(f"       Overall Score: {impact.overall_impact_score:.2f}")
                print(f"       Housing: +{impact.housing_impact.net_new_units} units ({impact.housing_impact.affordable_units_added} affordable)")
                print(f"       Accessibility: Walk +{impact.accessibility_impact.walk_score_change:.1f}, Transit +{impact.accessibility_impact.transit_accessibility_change:.1%}")
                print(f"       Equity: Community {impact.equity_impact.community_benefit_score:.2f}, Displacement {impact.housing_impact.displacement_risk_score:.1%}")
                print(f"       Economic: {impact.economic_impact.construction_jobs_created} jobs, ${impact.economic_impact.cost_per_unit:,.0f}/unit")
                print(f"       Environmental: {impact.environmental_impact.climate_resilience_score:.2f} resilience")
            
            print(f"  🔍 Implementation Analysis:")
            print(f"    Phases: {len(scenario_comparison.phasing_recommendations)}")
            print(f"    Policy Requirements: {len(scenario_comparison.policy_requirements)}")
            print(f"    Community Engagement: {len(scenario_comparison.community_engagement_needs)}")
            print(f"    Tradeoffs: {len(scenario_comparison.tradeoff_analysis)}")
            
            # Comprehensive validation checks
            checks = []
            
            # Basic structure validation
            has_impacts = len(scenario_comparison.plan_impacts) >= expected["min_impacts"]
            checks.append(("Minimum Impact Analyses Generated", has_impacts))
            
            has_recommended = bool(scenario_comparison.recommended_plan_id) and scenario_comparison.recommended_plan_id != "none"
            checks.append(("Has Recommended Plan", has_recommended))
            
            correct_neighborhood = expected["neighborhood"] in scenario_comparison.scenario_name
            checks.append(("Correct Neighborhood", correct_neighborhood))
            
            has_scenario_name = bool(scenario_comparison.scenario_name) and "Impact Analysis" in scenario_comparison.scenario_name
            checks.append(("Has Impact Analysis Name", has_scenario_name))
            
            # Impact analysis completeness validation
            all_impacts_complete = all(
                impact.plan_id and impact.plan_name and
                hasattr(impact, 'housing_impact') and hasattr(impact, 'accessibility_impact') and
                hasattr(impact, 'equity_impact') and hasattr(impact, 'economic_impact') and
                hasattr(impact, 'environmental_impact') and
                0 <= impact.overall_impact_score <= 1 and
                0 <= impact.confidence_level <= 1
                for impact in scenario_comparison.plan_impacts
            )
            checks.append(("All Impact Analyses Complete", all_impacts_complete))
            
            # KPI dashboard validation
            kpi_dashboard_complete = all([
                hasattr(scenario_comparison, 'cumulative_housing_impact'),
                hasattr(scenario_comparison, 'cumulative_equity_impact'),
                0.1 <= scenario_comparison.analysis_confidence <= 1.0,
                0.1 <= scenario_comparison.data_completeness <= 1.0
            ])
            checks.append(("KPI Dashboard Complete", kpi_dashboard_complete))
            
            # Housing impact validation
            housing_impacts_valid = all(
                impact.housing_impact.current_units > 0 and
                impact.housing_impact.projected_units > impact.housing_impact.current_units and
                impact.housing_impact.net_new_units > 0 and
                0 <= impact.housing_impact.displacement_risk_score <= 1 and
                impact.housing_impact.population_capacity_change > 0
                for impact in scenario_comparison.plan_impacts
            )
            checks.append(("Housing Impact Valid", housing_impacts_valid))
            
            # Accessibility impact validation
            accessibility_impacts_valid = all(
                -10 <= impact.accessibility_impact.walk_score_change <= 10 and
                0 <= impact.accessibility_impact.transit_accessibility_change <= 1 and
                impact.accessibility_impact.parking_impact >= 0 and
                0 <= impact.accessibility_impact.traffic_impact_score <= 1
                for impact in scenario_comparison.plan_impacts
            )
            checks.append(("Accessibility Impact Valid", accessibility_impacts_valid))
            
            # Equity impact validation
            equity_impacts_valid = all(
                -1 <= impact.equity_impact.gentrification_pressure_change <= 1 and
                0 <= impact.equity_impact.demographic_stability_score <= 1 and
                0 <= impact.equity_impact.community_benefit_score <= 1 and
                impact.equity_impact.economic_opportunity_change >= 0
                for impact in scenario_comparison.plan_impacts
            )
            checks.append(("Equity Impact Valid", equity_impacts_valid))
            
            # Economic impact validation
            economic_impacts_valid = all(
                impact.economic_impact.construction_jobs_created > 0 and
                impact.economic_impact.tax_revenue_increase > 0 and
                impact.economic_impact.cost_per_unit > 100000 and  # SF reality check
                -1 <= impact.economic_impact.local_business_impact_score <= 1
                for impact in scenario_comparison.plan_impacts
            )
            checks.append(("Economic Impact Valid", economic_impacts_valid))
            
            # Environmental impact validation
            environmental_impacts_valid = all(
                impact.environmental_impact.carbon_footprint_change > 0 and
                0 <= impact.environmental_impact.climate_resilience_score <= 1 and
                0 <= impact.environmental_impact.stormwater_impact_score <= 1 and
                0 <= impact.environmental_impact.energy_efficiency_rating <= 1
                for impact in scenario_comparison.plan_impacts
            )
            checks.append(("Environmental Impact Valid", environmental_impacts_valid))
            
            # Benefits and concerns validation
            benefits_concerns_valid = all(
                len(impact.key_benefits) > 0 and
                len(impact.key_concerns) > 0 and
                len(impact.mitigation_strategies) > 0
                for impact in scenario_comparison.plan_impacts
            )
            checks.append(("Benefits/Concerns Analysis Complete", benefits_concerns_valid))
            
            # Implementation planning validation
            implementation_complete = all([
                len(scenario_comparison.phasing_recommendations) > 0,
                len(scenario_comparison.policy_requirements) > 0,
                len(scenario_comparison.community_engagement_needs) > 0,
                len(scenario_comparison.tradeoff_analysis) > 0,
                len(scenario_comparison.comparison_rationale) > 10
            ])
            checks.append(("Implementation Planning Complete", implementation_complete))
            
            # Plan optimization validation
            plans_are_optimized = True
            if len(scenario_comparison.plan_impacts) > 1:
                # Check if recommended plan is actually in the top plans
                recommended_impact = next(
                    (impact for impact in scenario_comparison.plan_impacts 
                     if impact.plan_id == scenario_comparison.recommended_plan_id),
                    None
                )
                if recommended_impact:
                    avg_score = sum(p.overall_impact_score for p in scenario_comparison.plan_impacts) / len(scenario_comparison.plan_impacts)
                    plans_are_optimized = recommended_impact.overall_impact_score >= avg_score
            checks.append(("Plan Optimization Working", plans_are_optimized))
            
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
    
    # Test Agent 2 → Agent 3 data flow integration
    print(f"\n🔗 Testing Agent 2 → Agent 3 Data Flow Integration")
    print("-" * 80)
    
    try:
        research_brief = research_agent.research_query("Test Agent 2-3 integration in Hayes Valley")
        planning_alternatives = planner_agent.generate_scenarios(research_brief)
        scenario_comparison = evaluator_agent.evaluate_scenarios(planning_alternatives)
        
        # Test data flow consistency
        agent2_plan_ids = {plan.plan_id for plan in planning_alternatives.plans}
        agent3_plan_ids = {impact.plan_id for impact in scenario_comparison.plan_impacts}
        
        data_flow_checks = [
            ("All Plans Have Impact Analysis", agent2_plan_ids == agent3_plan_ids),
            ("Scenario Names Consistent", planning_alternatives.scenario_name in scenario_comparison.scenario_name),
            ("Recommended Plan Consistent", scenario_comparison.recommended_plan_id in agent2_plan_ids),
            ("Confidence Levels Reasonable", all(
                0.1 <= impact.confidence_level <= 1.0 for impact in scenario_comparison.plan_impacts
            )),
        ]
        
        print(f"  📊 Data Flow Validation:")
        data_flow_passed = True
        for check_name, result in data_flow_checks:
            status = "✅" if result else "❌"
            print(f"    {status} {check_name}")
            if not result:
                data_flow_passed = False
        
        if data_flow_passed:
            passed_tests += 1
        
        total_tests += 1
        
    except Exception as e:
        print(f"  ❌ Data Flow Error: {e}")
        total_tests += 1
    
    print(f"\n📈 COMPLETE AGENT 3 TEST SUMMARY")
    print("=" * 80)
    print(f"Passed: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests >= total_tests * 0.85:  # 85% pass rate
        print("🏆 AGENT 3 (EVALUATOR) FULLY FUNCTIONAL!")
        print("✅ Complete Agent 1 → Agent 2 → Agent 3 workflow working")
        print("✅ Comprehensive impact analysis with 5 impact categories")
        print("✅ KPI dashboard with before/after metrics")
        print("✅ Implementation planning and policy requirements")
        print("✅ Plan optimization and recommendation system")
        print("✅ Ready for complete E2E workflow testing")
        return True
    else:
        failed = total_tests - passed_tests
        print(f"⚠️  {failed} tests failed. Review complete integration.")
        return False

def demo_complete_agent3_workflow():
    """Demonstrate the complete Agent 1 → Agent 2 → Agent 3 workflow"""
    print(f"\n🎪 COMPLETE AGENT 1 → 2 → 3 WORKFLOW DEMO")
    print("=" * 80)
    
    research_agent = ResearchAgent()
    planner_agent = PlannerAgent()
    evaluator_agent = EvaluatorAgent()
    
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
    
    # Agent 3: Impact Analysis
    print(f"\n3️⃣ Agent 3 (Evaluator):")
    scenario_comparison = evaluator_agent.evaluate_scenarios(planning_alternatives)
    print(f"   Impact Analysis: {scenario_comparison.scenario_name}")
    print(f"   Plans Evaluated: {len(scenario_comparison.plan_impacts)}")
    print(f"   Recommended: {scenario_comparison.recommended_plan_id}")
    print(f"   Analysis Confidence: {scenario_comparison.analysis_confidence:.0%}")
    
    print(f"\n📊 Comprehensive Impact Analysis Summary:")
    
    # Housing Impact Summary
    housing_summary = scenario_comparison.cumulative_housing_impact
    print(f"   🏠 Housing: +{housing_summary.net_new_units} units ({housing_summary.affordable_units_added} affordable)")
    print(f"      Displacement Risk: {housing_summary.displacement_risk_score:.1%}")
    print(f"      New Residents: ~{housing_summary.population_capacity_change} people")
    
    # Recommended Plan Details
    recommended_impact = next(
        (impact for impact in scenario_comparison.plan_impacts 
         if impact.plan_id == scenario_comparison.recommended_plan_id),
        scenario_comparison.plan_impacts[0] if scenario_comparison.plan_impacts else None
    )
    
    if recommended_impact:
        print(f"\n🎯 Recommended Plan Impact Analysis: {recommended_impact.plan_name}")
        print(f"   Overall Score: {recommended_impact.overall_impact_score:.2f}")
        print(f"   🏠 Housing: +{recommended_impact.housing_impact.net_new_units} units")
        print(f"   🚶 Accessibility: Walk +{recommended_impact.accessibility_impact.walk_score_change:.1f}, Transit +{recommended_impact.accessibility_impact.transit_accessibility_change:.1%}")
        print(f"   ⚖️ Equity: Community {recommended_impact.equity_impact.community_benefit_score:.2f}, Gentrification {recommended_impact.equity_impact.gentrification_pressure_change:+.2f}")
        print(f"   💰 Economic: {recommended_impact.economic_impact.construction_jobs_created} jobs, ${recommended_impact.economic_impact.tax_revenue_increase:,.0f} tax revenue")
        print(f"   🌍 Environmental: {recommended_impact.environmental_impact.climate_resilience_score:.2f} resilience")
        
        print(f"\n🔑 Key Benefits:")
        for benefit in recommended_impact.key_benefits[:3]:
            print(f"   • {benefit}")
        
        print(f"\n⚠️ Key Concerns:")
        for concern in recommended_impact.key_concerns[:3]:
            print(f"   • {concern}")
    
    print(f"\n🔄 Key Tradeoffs:")
    for tradeoff in scenario_comparison.tradeoff_analysis[:3]:
        print(f"   • {tradeoff}")
    
    print(f"\n🛠️ Implementation Plan:")
    for phase in scenario_comparison.phasing_recommendations:
        print(f"   • {phase}")

if __name__ == "__main__":
    success = test_complete_evaluator_agent()
    if success:
        demo_complete_agent3_workflow()
    else:
        print("\n⚠️ Fix integration issues before proceeding")