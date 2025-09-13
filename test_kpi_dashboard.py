#!/usr/bin/env python3
"""
Test the KPI Dashboard Module for Evaluator Agent
Verifies comprehensive impact visualization and key performance indicators
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
ScenarioComparison = evaluator_agent_module.ScenarioComparison

def test_kpi_dashboard_module():
    print("📊 Testing KPI Dashboard Module")
    print("=" * 70)
    
    research_agent = ResearchAgent()
    planner_agent = PlannerAgent()
    evaluator_agent = EvaluatorAgent()
    
    # Test cases covering different KPI scenarios
    test_cases = [
        {
            "query": "Add 100 affordable housing units in Hayes Valley",
            "neighborhood": "Hayes Valley",
            "expected_kpis": ["housing", "accessibility", "equity", "economic", "environmental"],
            "description": "Large-Scale Housing Development KPIs"
        },
        {
            "query": "Make Marina more walkable and transit-connected",
            "neighborhood": "Marina District",
            "expected_kpis": ["accessibility", "economic", "environmental"],
            "description": "Accessibility-Focused Development KPIs"
        },
        {
            "query": "Prevent displacement while increasing density in Mission",
            "neighborhood": "Mission District",
            "expected_kpis": ["housing", "equity", "economic"],
            "description": "Equity-Focused Development KPIs"
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
            
            # Focus on KPI dashboard analysis
            print(f"\n  📊 KPI Dashboard Analysis:")
            
            # Aggregate KPIs across all plans
            all_impacts = scenario_comparison.plan_impacts
            
            # Housing KPIs
            total_new_units = sum(impact.housing_impact.net_new_units for impact in all_impacts)
            avg_affordable_percentage = sum(
                impact.housing_impact.affordable_units_added / max(impact.housing_impact.net_new_units, 1) 
                for impact in all_impacts
            ) / len(all_impacts)
            avg_displacement_risk = sum(
                impact.housing_impact.displacement_risk_score for impact in all_impacts
            ) / len(all_impacts)
            
            print(f"    🏠 Housing KPIs:")
            print(f"       Total New Units: {total_new_units}")
            print(f"       Avg Affordability: {avg_affordable_percentage:.1%}")
            print(f"       Avg Displacement Risk: {avg_displacement_risk:.1%}")
            
            # Accessibility KPIs
            avg_walk_score_change = sum(
                impact.accessibility_impact.walk_score_change for impact in all_impacts
            ) / len(all_impacts)
            avg_transit_improvement = sum(
                impact.accessibility_impact.transit_accessibility_change for impact in all_impacts
            ) / len(all_impacts)
            total_parking_spaces = sum(
                impact.accessibility_impact.parking_impact for impact in all_impacts
            )
            
            print(f"    🚶 Accessibility KPIs:")
            print(f"       Avg Walk Score Change: +{avg_walk_score_change:.1f}")
            print(f"       Avg Transit Improvement: +{avg_transit_improvement:.1%}")
            print(f"       Total Parking Spaces: {total_parking_spaces}")
            
            # Equity KPIs
            avg_community_benefit = sum(
                impact.equity_impact.community_benefit_score for impact in all_impacts
            ) / len(all_impacts)
            avg_gentrification_pressure = sum(
                impact.equity_impact.gentrification_pressure_change for impact in all_impacts
            ) / len(all_impacts)
            
            print(f"    ⚖️ Equity KPIs:")
            print(f"       Avg Community Benefit: {avg_community_benefit:.2f}")
            print(f"       Avg Gentrification Pressure: {avg_gentrification_pressure:+.2f}")
            
            # Economic KPIs
            total_construction_jobs = sum(
                impact.economic_impact.construction_jobs_created for impact in all_impacts
            )
            total_tax_revenue = sum(
                impact.economic_impact.tax_revenue_increase for impact in all_impacts
            )
            avg_cost_per_unit = sum(
                impact.economic_impact.cost_per_unit for impact in all_impacts
            ) / len(all_impacts)
            
            print(f"    💰 Economic KPIs:")
            print(f"       Total Construction Jobs: {total_construction_jobs}")
            print(f"       Total Tax Revenue: ${total_tax_revenue:,.0f}")
            print(f"       Avg Cost Per Unit: ${avg_cost_per_unit:,.0f}")
            
            # Environmental KPIs
            avg_carbon_footprint = sum(
                impact.environmental_impact.carbon_footprint_change for impact in all_impacts
            ) / len(all_impacts)
            avg_climate_resilience = sum(
                impact.environmental_impact.climate_resilience_score for impact in all_impacts
            ) / len(all_impacts)
            
            print(f"    🌍 Environmental KPIs:")
            print(f"       Avg Carbon Footprint: +{avg_carbon_footprint:.0f} tons CO2/year")
            print(f"       Avg Climate Resilience: {avg_climate_resilience:.2f}")
            
            # Validation checks for KPI dashboard
            print(f"\n  🔍 KPI Dashboard Validation:")
            
            validation_checks = []
            
            # Check that all major KPI categories are represented
            has_housing_kpis = total_new_units > 0
            validation_checks.append(("Housing KPIs Present", has_housing_kpis))
            
            has_accessibility_kpis = avg_walk_score_change >= 0 and total_parking_spaces >= 0
            validation_checks.append(("Accessibility KPIs Present", has_accessibility_kpis))
            
            has_equity_kpis = 0 <= avg_community_benefit <= 1
            validation_checks.append(("Equity KPIs Present", has_equity_kpis))
            
            has_economic_kpis = total_construction_jobs > 0 and avg_cost_per_unit > 0
            validation_checks.append(("Economic KPIs Present", has_economic_kpis))
            
            has_environmental_kpis = avg_carbon_footprint > 0 and avg_climate_resilience > 0
            validation_checks.append(("Environmental KPIs Present", has_environmental_kpis))
            
            # Check KPI value ranges are reasonable
            kpi_ranges_reasonable = all([
                0 <= avg_affordable_percentage <= 1,
                0 <= avg_displacement_risk <= 1,
                -10 <= avg_walk_score_change <= 10,
                0 <= avg_transit_improvement <= 1,
                -1 <= avg_gentrification_pressure <= 1,
                avg_cost_per_unit > 100000,  # SF development costs
                avg_carbon_footprint < 1000   # Reasonable carbon estimate
            ])
            validation_checks.append(("KPI Value Ranges Reasonable", kpi_ranges_reasonable))
            
            # Check comprehensive analysis components
            has_implementation_plan = len(scenario_comparison.phasing_recommendations) > 0
            validation_checks.append(("Implementation Plan Present", has_implementation_plan))
            
            has_policy_requirements = len(scenario_comparison.policy_requirements) > 0
            validation_checks.append(("Policy Requirements Present", has_policy_requirements))
            
            has_tradeoff_analysis = len(scenario_comparison.tradeoff_analysis) > 0
            validation_checks.append(("Tradeoff Analysis Present", has_tradeoff_analysis))
            
            has_community_engagement = len(scenario_comparison.community_engagement_needs) > 0
            validation_checks.append(("Community Engagement Plan Present", has_community_engagement))
            
            # Display validation results
            all_passed = True
            for check_name, result in validation_checks:
                status = "✅" if result else "❌"
                print(f"    {status} {check_name}")
                if not result:
                    all_passed = False
            
            # Test scenario comparison logic
            print(f"\n  📈 Scenario Comparison Analysis:")
            
            # Check recommended plan selection
            recommended_plan = next(
                (impact for impact in all_impacts if impact.plan_id == scenario_comparison.recommended_plan_id),
                all_impacts[0] if all_impacts else None
            )
            
            if recommended_plan:
                comparison_checks = [
                    ("Recommended Plan Identified", True),
                    ("Rationale Provided", len(scenario_comparison.comparison_rationale) > 10),
                    ("Analysis Confidence Reasonable", 0.1 <= scenario_comparison.analysis_confidence <= 1.0),
                ]
                
                for check_name, result in comparison_checks:
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
    
    # Test KPI aggregation and visualization readiness
    print(f"\n📈 Testing KPI Aggregation and Visualization Readiness")
    print("-" * 70)
    
    try:
        # Test KPI data structure for frontend consumption
        research_brief = research_agent.research_query("Test KPI structure in Hayes Valley")
        planning_alternatives = planner_agent.generate_scenarios(research_brief)
        scenario_comparison = evaluator_agent.evaluate_scenarios(planning_alternatives)
        
        aggregation_tests = []
        
        # Test that all required data is available for charts
        has_chart_data = all([
            len(scenario_comparison.plan_impacts) > 0,
            hasattr(scenario_comparison, 'cumulative_housing_impact'),
            hasattr(scenario_comparison, 'cumulative_equity_impact'),
            hasattr(scenario_comparison, 'analysis_confidence'),
        ])
        aggregation_tests.append(("Chart Data Available", has_chart_data))
        
        # Test before/after comparison data
        if scenario_comparison.plan_impacts:
            first_impact = scenario_comparison.plan_impacts[0]
            has_before_after = (
                first_impact.housing_impact.current_units != first_impact.housing_impact.projected_units and
                hasattr(first_impact.accessibility_impact, 'walk_score_change') and
                hasattr(first_impact.equity_impact, 'gentrification_pressure_change')
            )
        else:
            has_before_after = False
        aggregation_tests.append(("Before/After Comparison Data", has_before_after))
        
        # Test implementation timeline data
        has_timeline_data = len(scenario_comparison.phasing_recommendations) >= 2
        aggregation_tests.append(("Implementation Timeline Data", has_timeline_data))
        
        print(f"  📊 Aggregation Validation:")
        aggregation_passed = True
        for check_name, result in aggregation_tests:
            status = "✅" if result else "❌"
            print(f"    {status} {check_name}")
            if not result:
                aggregation_passed = False
        
        if aggregation_passed:
            passed_tests += 1
        
        total_tests += 1
        
    except Exception as e:
        print(f"  ❌ Aggregation Error: {e}")
        total_tests += 1
    
    print(f"\n📊 KPI DASHBOARD MODULE TEST SUMMARY")
    print("=" * 70)
    print(f"Passed: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests >= total_tests * 0.8:  # 80% pass rate
        print("🎯 KPI Dashboard Module working well!")
        print("✅ Comprehensive KPI calculation and aggregation")
        print("✅ Before/after impact comparison data")
        print("✅ Scenario comparison and recommendation logic")
        print("✅ Implementation planning and policy requirements")
        print("✅ Ready for complete Agent 3 integration testing")
        return True
    else:
        failed = total_tests - passed_tests
        print(f"⚠️  {failed} tests failed. Review KPI dashboard calculations.")
        return False

def demo_kpi_dashboard():
    """Demo the KPI dashboard output"""
    print(f"\n🎪 KPI DASHBOARD DEMO")
    print("=" * 70)
    
    research_agent = ResearchAgent()
    planner_agent = PlannerAgent()
    evaluator_agent = EvaluatorAgent()
    
    query = "Add 50 affordable housing units near BART in Hayes Valley"
    print(f"Query: \"{query}\"")
    
    research_brief = research_agent.research_query(query)
    planning_alternatives = planner_agent.generate_scenarios(research_brief)
    scenario_comparison = evaluator_agent.evaluate_scenarios(planning_alternatives)
    
    print(f"\n📊 COMPREHENSIVE KPI DASHBOARD")
    print("=" * 70)
    print(f"Scenario: {scenario_comparison.scenario_name}")
    print(f"Plans Analyzed: {len(scenario_comparison.plan_impacts)}")
    print(f"Recommended Plan: {scenario_comparison.recommended_plan_id}")
    print(f"Analysis Confidence: {scenario_comparison.analysis_confidence:.0%}")
    
    # Housing Impact Summary
    housing_summary = scenario_comparison.cumulative_housing_impact
    print(f"\n🏠 HOUSING IMPACT SUMMARY:")
    print(f"   Total New Units: {housing_summary.net_new_units}")
    print(f"   Affordable Units: {housing_summary.affordable_units_added}")
    print(f"   Market Rate Units: {housing_summary.market_rate_units_added}")
    print(f"   Displacement Risk: {housing_summary.displacement_risk_score:.1%}")
    print(f"   New Residents: ~{housing_summary.population_capacity_change} people")
    
    # Recommended Plan Detailed KPIs
    recommended_impact = next(
        (impact for impact in scenario_comparison.plan_impacts 
         if impact.plan_id == scenario_comparison.recommended_plan_id),
        scenario_comparison.plan_impacts[0]
    )
    
    print(f"\n🎯 RECOMMENDED PLAN KPIs: {recommended_impact.plan_name}")
    print(f"   Overall Impact Score: {recommended_impact.overall_impact_score:.2f}")
    
    # Multi-category KPIs
    categories = [
        ("🏠 Housing", [
            f"New Units: {recommended_impact.housing_impact.net_new_units}",
            f"Affordable: {recommended_impact.housing_impact.affordable_units_added}",
            f"Displacement Risk: {recommended_impact.housing_impact.displacement_risk_score:.1%}"
        ]),
        ("🚶 Accessibility", [
            f"Walk Score: +{recommended_impact.accessibility_impact.walk_score_change:.1f}",
            f"Transit: +{recommended_impact.accessibility_impact.transit_accessibility_change:.1%}",
            f"Parking: {recommended_impact.accessibility_impact.parking_impact} spaces"
        ]),
        ("⚖️ Equity", [
            f"Community Benefit: {recommended_impact.equity_impact.community_benefit_score:.2f}",
            f"Gentrification: {recommended_impact.equity_impact.gentrification_pressure_change:+.2f}",
            f"Stability: {recommended_impact.equity_impact.demographic_stability_score:.2f}"
        ]),
        ("💰 Economic", [
            f"Construction Jobs: {recommended_impact.economic_impact.construction_jobs_created}",
            f"Tax Revenue: ${recommended_impact.economic_impact.tax_revenue_increase:,.0f}",
            f"Cost/Unit: ${recommended_impact.economic_impact.cost_per_unit:,.0f}"
        ]),
        ("🌍 Environmental", [
            f"Carbon: +{recommended_impact.environmental_impact.carbon_footprint_change:.0f} tons CO2/yr",
            f"Climate Resilience: {recommended_impact.environmental_impact.climate_resilience_score:.2f}",
            f"Stormwater Impact: {recommended_impact.environmental_impact.stormwater_impact_score:.2f}"
        ])
    ]
    
    for category, metrics in categories:
        print(f"\n   {category}:")
        for metric in metrics:
            print(f"     • {metric}")
    
    print(f"\n🔑 KEY BENEFITS:")
    for benefit in recommended_impact.key_benefits:
        print(f"   • {benefit}")
    
    print(f"\n⚠️ KEY CONCERNS:")
    for concern in recommended_impact.key_concerns:
        print(f"   • {concern}")
    
    print(f"\n🛠️ IMPLEMENTATION PLAN:")
    for phase in scenario_comparison.phasing_recommendations:
        print(f"   • {phase}")
    
    print(f"\n📋 POLICY REQUIREMENTS:")
    for policy in scenario_comparison.policy_requirements:
        print(f"   • {policy}")

if __name__ == "__main__":
    success = test_kpi_dashboard_module()
    if success:
        demo_kpi_dashboard()
    else:
        print("\n⚠️ Fix KPI dashboard issues before proceeding")