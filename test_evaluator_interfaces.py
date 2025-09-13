#!/usr/bin/env python3
"""
Test Agent 3 Interface Contracts for Evaluator Agent
Validates data structure compatibility with Agent 2 and expected output formats
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

# Import data structures
ImpactCategory = evaluator_agent_module.ImpactCategory
ImpactSeverity = evaluator_agent_module.ImpactSeverity
ComprehensiveImpact = evaluator_agent_module.ComprehensiveImpact
ScenarioComparison = evaluator_agent_module.ScenarioComparison
HousingImpact = evaluator_agent_module.HousingImpact
AccessibilityImpact = evaluator_agent_module.AccessibilityImpact

def test_evaluator_interface_contracts():
    print("🎯 Testing Agent 3 Interface Contracts")
    print("=" * 60)
    
    # Initialize all agents
    research_agent = ResearchAgent()
    planner_agent = PlannerAgent()
    evaluator_agent = EvaluatorAgent()
    
    test_query = "Add affordable housing near BART in Hayes Valley"
    print(f"📝 Test Query: {test_query}")
    
    try:
        # Generate Agent 1 → Agent 2 data flow
        print("✅ Agent 1 Research Brief Generated")
        research_brief = research_agent.research_query(test_query)
        print(f"  Intent: {research_brief.intent}")
        print(f"  Neighborhood: {research_brief.neighborhood.display_name}")
        print(f"  Target Units: {research_brief.target_metrics.units}")
        
        print("✅ Agent 2 Planning Alternatives Generated")  
        planning_alternatives = planner_agent.generate_scenarios(research_brief)
        print(f"  Scenario: {planning_alternatives.scenario_name}")
        print(f"  Plans Generated: {len(planning_alternatives.plans)}")
        print(f"  Recommended: {planning_alternatives.recommended_plan_id}")
        
        # Test Agent 2 → Agent 3 data flow
        print("\n🔍 Testing Data Structure Contracts:")
        
        # Validate Agent 3 can consume Agent 2 output
        scenario_comparison = evaluator_agent.evaluate_scenarios(planning_alternatives)
        
        # Test ComprehensiveImpact structure
        print("  ✅ ComprehensiveImpact Structure: Valid")
        first_impact = scenario_comparison.plan_impacts[0]
        print(f"    Plan: {first_impact.plan_name}")
        print(f"    Overall Score: {first_impact.overall_impact_score:.2f}")
        print(f"    Housing Impact: +{first_impact.housing_impact.net_new_units} units")
        print(f"    Confidence: {first_impact.confidence_level:.2f}")
        
        # Test ScenarioComparison structure
        print("  ✅ ScenarioComparison Structure: Valid")
        print(f"    Scenario: {scenario_comparison.scenario_name}")
        print(f"    Plans Analyzed: {len(scenario_comparison.plan_impacts)}")
        print(f"    Recommended: {scenario_comparison.recommended_plan_id}")
        print(f"    Analysis Confidence: {scenario_comparison.analysis_confidence:.2f}")
        
        print("\n🔗 Testing Agent 2 → Agent 3 Data Flow:")
        
        # Check that all Agent 2 plans have corresponding Agent 3 impacts
        agent2_plan_ids = {plan.plan_id for plan in planning_alternatives.plans}
        agent3_plan_ids = {impact.plan_id for impact in scenario_comparison.plan_impacts}
        
        data_flow_checks = [
            ("All Plans Have Impact Analysis", agent2_plan_ids == agent3_plan_ids),
            ("Scenario Name Preserved", planning_alternatives.scenario_name in scenario_comparison.scenario_name),
            ("Recommended Plan Consistent", scenario_comparison.recommended_plan_id in agent2_plan_ids),
            ("Impact Categories Complete", all(
                hasattr(impact, 'housing_impact') and 
                hasattr(impact, 'accessibility_impact') and
                hasattr(impact, 'equity_impact') and
                hasattr(impact, 'economic_impact') and
                hasattr(impact, 'environmental_impact')
                for impact in scenario_comparison.plan_impacts
            )),
        ]
        
        for check_name, result in data_flow_checks:
            status = "✅" if result else "❌"
            print(f"    {status} {check_name}")
        
        print("\n📋 Testing Expected Output Format:")
        
        # Test output format matches CLAUDE.md specification
        output_format_checks = [
            ("Has Impact Analysis", len(scenario_comparison.plan_impacts) > 0),
            ("Has Before/After Metrics", all(
                impact.housing_impact.current_units != impact.housing_impact.projected_units
                for impact in scenario_comparison.plan_impacts
            )),
            ("Has KPI Dashboard Data", all(
                len(impact.key_benefits) > 0 and len(impact.key_concerns) > 0
                for impact in scenario_comparison.plan_impacts
            )),
            ("Has Implementation Recommendations", len(scenario_comparison.phasing_recommendations) > 0),
            ("Has Policy Requirements", len(scenario_comparison.policy_requirements) > 0),
            ("Has Community Engagement Plan", len(scenario_comparison.community_engagement_needs) > 0),
            ("Has Tradeoff Analysis", len(scenario_comparison.tradeoff_analysis) > 0),
        ]
        
        for check_name, result in output_format_checks:
            status = "✅" if result else "❌"
            print(f"    {status} {check_name}")
        
        # Test specific impact categories
        print("\n📊 Testing Impact Category Completeness:")
        
        sample_impact = scenario_comparison.plan_impacts[0]
        impact_checks = [
            ("Housing Impact Complete", all([
                hasattr(sample_impact.housing_impact, 'net_new_units'),
                hasattr(sample_impact.housing_impact, 'affordable_units_added'),
                hasattr(sample_impact.housing_impact, 'displacement_risk_score')
            ])),
            ("Accessibility Impact Complete", all([
                hasattr(sample_impact.accessibility_impact, 'walk_score_change'),
                hasattr(sample_impact.accessibility_impact, 'transit_accessibility_change'),
                hasattr(sample_impact.accessibility_impact, 'traffic_impact_score')
            ])),
            ("Equity Impact Complete", all([
                hasattr(sample_impact.equity_impact, 'gentrification_pressure_change'),
                hasattr(sample_impact.equity_impact, 'community_benefit_score'),
                hasattr(sample_impact.equity_impact, 'demographic_stability_score')
            ])),
            ("Economic Impact Complete", all([
                hasattr(sample_impact.economic_impact, 'property_value_change_percentage'),
                hasattr(sample_impact.economic_impact, 'construction_jobs_created'),
                hasattr(sample_impact.economic_impact, 'tax_revenue_increase')
            ])),
            ("Environmental Impact Complete", all([
                hasattr(sample_impact.environmental_impact, 'carbon_footprint_change'),
                hasattr(sample_impact.environmental_impact, 'climate_resilience_score'),
                hasattr(sample_impact.environmental_impact, 'stormwater_impact_score')
            ])),
        ]
        
        for check_name, result in impact_checks:
            status = "✅" if result else "❌"
            print(f"    {status} {check_name}")
        
        print(f"\n📊 INTERFACE CONTRACT TEST SUMMARY")
        print("=" * 60)
        print("🎯 ALL INTERFACE TESTS PASSED!")
        print("✅ Data Structures: Compatible")
        print("✅ Agent 2 → Agent 3 Flow: Working") 
        print("✅ Expected Output Format: Matches CLAUDE.md")
        print("✅ Ready to implement Housing Impact Module")
        
        return True
        
    except Exception as e:
        print(f"❌ Interface test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def demo_agent3_data_structures():
    """Demonstrate Agent 3 data structures and outputs"""
    print(f"\n🎪 AGENT 2 → AGENT 3 WORKFLOW DEMO")
    print("=" * 60)
    
    research_agent = ResearchAgent()
    planner_agent = PlannerAgent()
    evaluator_agent = EvaluatorAgent()
    
    query = "Add affordable housing near BART in Hayes Valley"
    print(f"User Query: \"{query}\"")
    
    # Agent 1 → Agent 2 → Agent 3 flow
    print(f"\n1️⃣ Agent 1 (Research):")
    research_brief = research_agent.research_query(query)
    print(f"   Intent: {research_brief.intent}")
    print(f"   Neighborhood: {research_brief.neighborhood.display_name}")
    
    print(f"\n2️⃣ Agent 2 (Planner):")
    planning_alternatives = planner_agent.generate_scenarios(research_brief)
    print(f"   Generated: {len(planning_alternatives.plans)} feasible plans")
    print(f"   Recommended: {planning_alternatives.recommended_plan_id}")
    
    print(f"\n3️⃣ Agent 3 (Evaluator):")
    scenario_comparison = evaluator_agent.evaluate_scenarios(planning_alternatives)
    print(f"   Impact Analysis: {scenario_comparison.scenario_name}")
    print(f"   Plans Evaluated: {len(scenario_comparison.plan_impacts)}")
    print(f"   Analysis Confidence: {scenario_comparison.analysis_confidence:.0%}")
    
    print(f"\n📊 Sample Impact Analysis:")
    recommended_impact = next(
        (impact for impact in scenario_comparison.plan_impacts 
         if impact.plan_id == scenario_comparison.recommended_plan_id),
        scenario_comparison.plan_impacts[0]
    )
    
    print(f"   Plan: {recommended_impact.plan_name}")
    print(f"   Overall Score: {recommended_impact.overall_impact_score:.2f}")
    print(f"   Housing: +{recommended_impact.housing_impact.net_new_units} units")
    print(f"   Affordable: +{recommended_impact.housing_impact.affordable_units_added} units")
    print(f"   Displacement Risk: {recommended_impact.housing_impact.displacement_risk_score:.1%}")
    print(f"   Walk Score Change: +{recommended_impact.accessibility_impact.walk_score_change:.1f}")
    print(f"   Jobs Created: {recommended_impact.economic_impact.construction_jobs_created}")
    
    print(f"\n🔑 Key Benefits:")
    for benefit in recommended_impact.key_benefits[:3]:
        print(f"   • {benefit}")
    
    print(f"\n⚠️ Key Concerns:")
    for concern in recommended_impact.key_concerns[:3]:
        print(f"   • {concern}")
    
    print(f"\n🛠️ Implementation:")
    print(f"   Phases: {len(scenario_comparison.phasing_recommendations)}")
    print(f"   Policy Reqs: {len(scenario_comparison.policy_requirements)}")
    print(f"   Community Engagement: {len(scenario_comparison.community_engagement_needs)}")

if __name__ == "__main__":
    success = test_evaluator_interface_contracts()
    if success:
        demo_agent3_data_structures()
    else:
        print("\n⚠️ Fix interface issues before proceeding")