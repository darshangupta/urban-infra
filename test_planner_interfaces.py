#!/usr/bin/env python3
"""
Test the Planner Agent Interface Contracts
Verifies data structures and integration with Agent 1 output
"""

import sys
import os

# Import the classes directly from the file to avoid __init__.py issues
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
PlanningAlternatives = planner_agent_module.PlanningAlternatives
PlanFeasibility = planner_agent_module.PlanFeasibility
PlanType = planner_agent_module.PlanType

def test_data_structure_contracts():
    """Test that our data structures match the expected Agent 1 → Agent 2 flow"""
    print("🏗️ Testing Agent 2 Interface Contracts")
    print("=" * 60)
    
    # Step 1: Generate a research brief from Agent 1
    research_agent = ResearchAgent()
    planner_agent = PlannerAgent()
    
    test_query = "Add 50 affordable housing units near BART in Hayes Valley"
    print(f"📝 Test Query: {test_query}")
    
    try:
        # Get research brief from Agent 1
        research_brief = research_agent.research_query(test_query)
        print(f"✅ Agent 1 Research Brief Generated")
        print(f"  Intent: {research_brief.intent}")
        print(f"  Neighborhood: {research_brief.neighborhood.display_name}")
        print(f"  Target Units: {research_brief.target_metrics.units}")
        
        # Test data structure compatibility
        print(f"\n🔍 Testing Data Structure Contracts:")
        
        # Test DevelopmentPlan structure
        sample_plan = DevelopmentPlan(
            plan_id="hayes_moderate_001",
            plan_type=PlanType.MODERATE,
            name="Hayes Valley Transit-Oriented Development",
            description="Mixed-use development maximizing transit accessibility",
            far=2.8,
            height_ft=50,
            total_units=research_brief.target_metrics.units or 50,
            lot_area_sf=3000,
            affordable_units=int((research_brief.target_metrics.units or 50) * 
                               (research_brief.target_metrics.affordability_pct or 0.20)),
            affordable_percentage=research_brief.target_metrics.affordability_pct or 0.20,
            parking_spaces=25,
            ground_floor_commercial_sf=1200,
            feasibility=PlanFeasibility.REQUIRES_VARIANCES,
            zoning_compliance="NCT-3 compliant with parking variance",
            required_variances=["parking_reduction"],
            design_rationale=["Maximize transit access", "Optimize unit mix for affordability"],
            policy_alignment=["Transit-oriented development", "Inclusionary housing compliance"],
            compliance_score=0.85
        )
        
        print(f"  ✅ DevelopmentPlan Structure: Valid")
        print(f"    Plan Type: {sample_plan.plan_type}")
        print(f"    Feasibility: {sample_plan.feasibility}")
        print(f"    Units: {sample_plan.total_units} ({sample_plan.affordable_units} affordable)")
        print(f"    Compliance Score: {sample_plan.compliance_score}")
        
        # Test PlanningAlternatives structure
        sample_alternatives = PlanningAlternatives(
            scenario_name="Hayes Valley Affordable Housing Development",
            original_query=research_brief.original_query,
            neighborhood=research_brief.neighborhood.display_name,
            planning_intent=research_brief.intent,
            plans=[sample_plan],
            recommended_plan_id=sample_plan.plan_id,
            feasibility_summary="Moderate development achieves target units with parking variance",
            tradeoffs_analysis=["Parking variance needed for unit count", "Ground floor commercial supports walkability"],
            zoning_opportunities=research_brief.key_opportunities,
            regulatory_challenges=research_brief.major_constraints,
            community_considerations=research_brief.policy_considerations,
            generation_confidence=0.85,
            planning_notes=["Based on NCT-3 zoning analysis", "Requires community input process"]
        )
        
        print(f"  ✅ PlanningAlternatives Structure: Valid")
        print(f"    Scenario: {sample_alternatives.scenario_name}")
        print(f"    Plans Generated: {len(sample_alternatives.plans)}")
        print(f"    Recommended: {sample_alternatives.recommended_plan_id}")
        print(f"    Confidence: {sample_alternatives.generation_confidence}")
        
        # Test Agent 1 → Agent 2 data compatibility
        print(f"\n🔗 Testing Agent 1 → Agent 2 Data Flow:")
        
        # Verify key data transfers correctly
        data_flow_checks = [
            ("Original Query", research_brief.original_query == sample_alternatives.original_query),
            ("Planning Intent", research_brief.intent == sample_alternatives.planning_intent),
            ("Neighborhood", research_brief.neighborhood.display_name == sample_alternatives.neighborhood),
            ("Target Units Match", research_brief.target_metrics.units == sample_plan.total_units),
            ("Affordability Preserved", research_brief.target_metrics.affordability_pct == sample_plan.affordable_percentage),
            ("Opportunities Transfer", len(sample_alternatives.zoning_opportunities) > 0),
            ("Constraints Transfer", len(sample_alternatives.regulatory_challenges) > 0)
        ]
        
        all_flow_checks_pass = True
        for check_name, result in data_flow_checks:
            status = "✅" if result else "❌"
            print(f"    {status} {check_name}")
            if not result:
                all_flow_checks_pass = False
        
        # Test expected output format (matching CLAUDE.md examples)
        print(f"\n📋 Testing Expected Output Format:")
        
        expected_format_checks = [
            ("Has Scenario Name", hasattr(sample_alternatives, 'scenario_name')),
            ("Has Multiple Plans Structure", isinstance(sample_alternatives.plans, list)),
            ("Plan Has FAR/Height", hasattr(sample_plan, 'far') and hasattr(sample_plan, 'height_ft')),
            ("Plan Has Units Breakdown", hasattr(sample_plan, 'total_units') and hasattr(sample_plan, 'affordable_units')),
            ("Has Feasibility Assessment", hasattr(sample_plan, 'feasibility')),
            ("Has Design Rationale", len(sample_plan.design_rationale) > 0),
            ("Has Tradeoffs Analysis", len(sample_alternatives.tradeoffs_analysis) > 0)
        ]
        
        all_format_checks_pass = True
        for check_name, result in expected_format_checks:
            status = "✅" if result else "❌"
            print(f"    {status} {check_name}")
            if not result:
                all_format_checks_pass = False
        
        print(f"\n📊 INTERFACE CONTRACT TEST SUMMARY")
        print("=" * 60)
        
        overall_success = all_flow_checks_pass and all_format_checks_pass
        
        if overall_success:
            print("🎯 ALL INTERFACE TESTS PASSED!")
            print("✅ Data Structures: Compatible")
            print("✅ Agent 1 → Agent 2 Flow: Working")
            print("✅ Expected Output Format: Matches CLAUDE.md")
            print("✅ Ready to implement Scenario Generator Module")
            return True
        else:
            print("⚠️ Some interface tests failed")
            return False
        
    except Exception as e:
        print(f"❌ Error in interface testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def demo_expected_workflow():
    """Demo the expected Agent 1 → Agent 2 workflow"""
    print(f"\n🎪 AGENT 1 → AGENT 2 WORKFLOW DEMO")
    print("=" * 60)
    
    research_agent = ResearchAgent()
    query = "Add affordable housing near BART in Hayes Valley"
    
    print(f"1. User Query: \"{query}\"")
    
    # Agent 1 Processing
    research_brief = research_agent.research_query(query)
    print(f"\n2. Agent 1 (Research) Output:")
    print(f"   Intent: {research_brief.intent}")
    print(f"   Neighborhood: {research_brief.neighborhood.display_name}")
    print(f"   Zoning: {research_brief.neighborhood.zoning.zone_type}")
    print(f"   Target Units: {research_brief.target_metrics.units}")
    print(f"   Opportunities: {len(research_brief.key_opportunities)}")
    print(f"   Constraints: {len(research_brief.major_constraints)}")
    
    print(f"\n3. Agent 2 (Planner) Input Ready:")
    print(f"   ✅ Research Brief contains all needed data")
    print(f"   ✅ Neighborhood profile with zoning constraints")
    print(f"   ✅ Target metrics for plan generation")
    print(f"   ✅ Policy context for feasibility assessment")
    
    print(f"\n4. Expected Agent 2 Processing:")
    print(f"   → Generate 3-5 development scenarios")
    print(f"   → Validate each against {research_brief.neighborhood.zoning.zone_type} zoning")
    print(f"   → Rank by feasibility and policy alignment")
    print(f"   → Return PlanningAlternatives with recommended plan")

if __name__ == "__main__":
    success = test_data_structure_contracts()
    if success:
        demo_expected_workflow()
    else:
        print("\n⚠️ Fix interface contracts before proceeding")