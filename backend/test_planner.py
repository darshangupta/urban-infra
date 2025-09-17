#!/usr/bin/env python3
"""
Test script for Agent 2 (Planner) with business impact modeling
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from standalone_interpreter import StandaloneInterpreterAgent
from agents.planner import PlannerAgent

def test_planner_with_business_focus():
    """Test the planner with business impact focused scenarios"""
    
    # Initialize agents
    interpreter = StandaloneInterpreterAgent()
    planner = PlannerAgent()
    
    # Test queries focused on business impact
    test_queries = [
        "How would more bike infrastructure affect businesses in the Marina vs the Mission?",
        "What's the impact of bike lanes on local businesses in both neighborhoods?",
        "Compare bike infrastructure effects on Marina and Mission businesses"
    ]
    
    print("🚀 Testing Agent 2 (Planner) with Business Impact Focus")
    print("=" * 80)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        print("=" * 60)
        
        # Step 1: Interpret the query
        planning_params = interpreter.interpret_query(query)
        print(f"🧠 Interpreter Output:")
        print(f"   Neighborhoods: {planning_params.neighborhoods}")
        print(f"   Intent: {planning_params.intent}")
        print(f"   Comparative: {planning_params.comparative}")
        print(f"   Elements: {planning_params.specific_elements}")
        
        # Step 2: Generate scenarios
        print(f"\n🏗️  Planner Output:")
        scenarios = planner.generate_scenarios(planning_params)
        
        if planning_params.comparative:
            print(f"   🔄 COMPARATIVE ANALYSIS:")
            print(f"   Neighborhoods: {scenarios.neighborhoods}")
            
            for neighborhood, neighborhood_scenarios in scenarios.scenarios_by_neighborhood.items():
                print(f"\n   🏘️  {neighborhood.upper()} SCENARIOS:")
                for j, scenario in enumerate(neighborhood_scenarios, 1):
                    print(f"      {j}. {scenario.title}")
                    print(f"         Type: {scenario.type}")
                    print(f"         Description: {scenario.description[:80]}...")
                    if scenario.business_impact_analysis:
                        print(f"         💼 Revenue Impact: {scenario.business_impact_analysis.get('revenue_impact', 'N/A')}")
                        print(f"         🚗 Access Changes: {len(scenario.business_impact_analysis.get('customer_access', {}))} modes analyzed")
            
            print(f"\n   📊 COMPARATIVE ANALYSIS:")
            if scenarios.comparative_analysis.get("business_impact_comparison"):
                for neighborhood, analysis in scenarios.comparative_analysis["business_impact_comparison"].items():
                    print(f"      {neighborhood.upper()}:")
                    print(f"         Risk Level: {analysis.get('risk_level')}")
                    print(f"         Main Opportunity: {analysis.get('main_opportunity')}")
                    print(f"         Adaptation Difficulty: {analysis.get('adaptation_difficulty')}")
            
            print(f"\n   💡 OVERALL RECOMMENDATION:")
            print(f"   {scenarios.overall_recommendation[:200]}...")
        
        else:
            print(f"   Single neighborhood analysis for {planning_params.neighborhoods[0]}")
            
        print("\n" + "-" * 60)

def test_detailed_business_impact():
    """Test detailed business impact analysis"""
    
    interpreter = StandaloneInterpreterAgent()
    planner = PlannerAgent()
    
    query = "How would bike lanes on Chestnut Street affect Marina businesses compared to Valencia Street businesses in Mission?"
    
    print(f"\n🔍 DETAILED BUSINESS IMPACT ANALYSIS")
    print("=" * 70)
    print(f"Query: {query}")
    
    # Interpret and plan
    planning_params = interpreter.interpret_query(query)
    scenarios = planner.generate_scenarios(planning_params)
    
    # Show detailed business impact for each neighborhood
    for neighborhood, neighborhood_scenarios in scenarios.scenarios_by_neighborhood.items():
        print(f"\n🏘️  {neighborhood.upper()} - DETAILED BUSINESS ANALYSIS:")
        
        for scenario in neighborhood_scenarios:
            if scenario.business_impact_analysis:
                print(f"\n   📋 Scenario: {scenario.title}")
                
                impact = scenario.business_impact_analysis
                
                if "customer_access" in impact:
                    print(f"   🚶 Customer Access Changes:")
                    for mode, change in impact["customer_access"].items():
                        print(f"      {mode.title()}: {change}")
                
                if "business_effects" in impact:
                    print(f"   🏪 Business Type Effects:")
                    for business_type, effect in impact["business_effects"].items():
                        print(f"      {business_type.replace('_', ' ').title()}: {effect}")
                
                if "mitigation" in impact:
                    print(f"   🛡️  Mitigation Strategies:")
                    for strategy in impact["mitigation"][:3]:  # Show first 3
                        print(f"      • {strategy}")
                
                print(f"   💰 Revenue Impact: {impact.get('revenue_impact', 'N/A')}")
                print(f"   ⏱️  Timeline: {scenario.implementation_timeline}")
                print(f"   💸 Cost: {scenario.estimated_cost}")

if __name__ == "__main__":
    test_planner_with_business_focus()
    test_detailed_business_impact()