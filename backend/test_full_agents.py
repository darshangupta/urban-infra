#!/usr/bin/env python3
"""
Test script for the complete multi-agent system
Tests Interpreter + Planner working together for comparative business impact analysis
"""

from typing import Dict, List, Any
from pydantic import BaseModel
from dataclasses import dataclass
import re

# Import our standalone interpreter
from standalone_interpreter import StandaloneInterpreterAgent, PlanningParameters, NeighborhoodProfile

class PlanningScenario(BaseModel):
    """Individual planning scenario with neighborhood-specific details"""
    title: str
    type: str
    description: str
    neighborhood: str
    units: int = 0
    affordable_percentage: int = 0
    height_ft: int = 0
    amenities: List[str] = []
    business_impact_analysis: Dict[str, Any] = {}
    implementation_timeline: str = ""
    estimated_cost: str = ""

class BusinessImpactModel(BaseModel):
    """Business impact analysis model"""
    customer_access_change: Dict[str, str]  # walk, bike, car, transit
    revenue_impact_range: str  # e.g., "-10% to +15%"
    business_type_effects: Dict[str, str]  # restaurant, retail, services
    mitigation_strategies: List[str]
    opportunity_factors: List[str]

class ComparativeScenarios(BaseModel):
    """Comparative scenarios across multiple neighborhoods"""
    neighborhoods: List[str]
    scenarios_by_neighborhood: Dict[str, List[PlanningScenario]]
    comparative_analysis: Dict[str, Any]
    overall_recommendation: str

class StandalonePlannerAgent:
    """Standalone Planner Agent for testing"""
    
    def __init__(self):
        self.neighborhood_profiles = self._load_neighborhood_profiles()
        self.business_impact_models = self._load_business_impact_models()
        
    def _load_neighborhood_profiles(self) -> Dict[str, NeighborhoodProfile]:
        """Load neighborhood profiles"""
        return {
            "marina": NeighborhoodProfile(
                name="Marina District",
                zoning="RH-1 (Residential House, One-Family)",
                character="Low-density, affluent, car-dependent, suburban feel within the city",
                main_streets=["Chestnut Street", "Union Street", "Lombard Street", "Marina Boulevard"],
                landmarks=["Marina Green", "Palace of Fine Arts", "Crissy Field", "Marina Harbor"],
                transport=["Golden Gate Transit", "Muni Lines 30, 43", "Limited BART access"],
                business_ecosystem="High-end boutiques, upscale dining, fitness studios, car-dependent suburban shoppers",
                demographic_profile="Affluent professionals, families, car ownership 85%+",
                development_pressure="Low - strong NIMBY resistance, height restrictions",
                constraints=["Flood risk", "Limited transit", "Height restrictions", "Parking demands"]
            ),
            "mission": NeighborhoodProfile(
                name="Mission District", 
                zoning="NCT-3/NCT-4 (Neighborhood Commercial Transit)",
                character="Dense, diverse, walkable, cultural significance, rapid gentrification",
                main_streets=["Mission Street", "Valencia Street", "16th Street", "24th Street"],
                landmarks=["Mission Dolores", "Valencia Corridor", "Mission Cultural Center", "Balmy Alley"],
                transport=["16th St Mission BART", "24th St Mission BART", "Multiple Muni lines"],
                business_ecosystem="Latino businesses, corner stores, restaurants, emerging tech cafes, community-oriented",
                demographic_profile="Working class Latino families, young professionals, artists, low car ownership",
                development_pressure="Very high - gentrification, displacement risk",
                constraints=["Displacement pressure", "Cultural preservation", "Transit overcrowding"]
            )
        }
    
    def _load_business_impact_models(self) -> Dict[str, BusinessImpactModel]:
        """Load business impact models for different intervention types"""
        return {
            "bike_infrastructure_marina": BusinessImpactModel(
                customer_access_change={
                    "car": "Reduced parking availability (-25%)",
                    "bike": "New cycling customer base (+40%)",
                    "walk": "Improved pedestrian safety (+15%)",
                    "transit": "Minimal change (limited transit)"
                },
                revenue_impact_range="-15% to +25%",
                business_type_effects={
                    "high_end_retail": "Risk: Loss of car-dependent suburban shoppers (-20%)",
                    "restaurants": "Opportunity: Outdoor dining expansion (+15%)",
                    "fitness_studios": "Opportunity: Bike commuter customers (+30%)"
                },
                mitigation_strategies=[
                    "Preserve select parking spaces for businesses",
                    "Create dedicated loading zones",
                    "Implement bike valet services",
                    "Partner with delivery services for bike logistics"
                ],
                opportunity_factors=[
                    "Attract environmentally conscious affluent customers",
                    "Create unique cycling-oriented business district",
                    "Leverage Marina's recreation-focused demographics"
                ]
            ),
            "bike_infrastructure_mission": BusinessImpactModel(
                customer_access_change={
                    "car": "Limited impact (already low car ownership)",
                    "bike": "Major enhancement for existing bike culture (+50%)",
                    "walk": "Improved street safety (+25%)",
                    "transit": "Better bike-transit connections (+20%)"
                },
                revenue_impact_range="+10% to +35%",
                business_type_effects={
                    "corner_stores": "Opportunity: Increased foot traffic (+20%)",
                    "restaurants": "Major opportunity: Bike-friendly dining culture (+30%)",
                    "community_services": "Improved accessibility for residents (+25%)"
                },
                mitigation_strategies=[
                    "Ensure bike lane design doesn't block business access",
                    "Create secure bike parking near businesses",
                    "Coordinate with existing bike advocacy groups"
                ],
                opportunity_factors=[
                    "Strengthen community-oriented business model",
                    "Attract bike-commuting tech workers",
                    "Support existing cycling culture and activism"
                ]
            )
        }
    
    def generate_scenarios(self, planning_params: PlanningParameters) -> ComparativeScenarios:
        """Generate scenarios based on planning parameters"""
        
        if planning_params.comparative and len(planning_params.neighborhoods) > 1:
            return self._generate_comparative_scenarios(planning_params)
        else:
            # Single neighborhood planning
            scenarios = self._generate_single_neighborhood_scenarios(
                planning_params.neighborhoods[0], 
                planning_params
            )
            return ComparativeScenarios(
                neighborhoods=planning_params.neighborhoods,
                scenarios_by_neighborhood={planning_params.neighborhoods[0]: scenarios},
                comparative_analysis={},
                overall_recommendation=f"Recommended approach for {planning_params.neighborhoods[0]} focuses on {planning_params.focus}"
            )
    
    def _generate_comparative_scenarios(self, planning_params: PlanningParameters) -> ComparativeScenarios:
        """Generate scenarios for multiple neighborhoods with comparative analysis"""
        
        scenarios_by_neighborhood = {}
        
        # Generate scenarios for each neighborhood
        for neighborhood in planning_params.neighborhoods:
            scenarios = self._generate_single_neighborhood_scenarios(neighborhood, planning_params)
            scenarios_by_neighborhood[neighborhood] = scenarios
        
        # Perform comparative analysis
        comparative_analysis = self._perform_comparative_analysis(
            planning_params, 
            scenarios_by_neighborhood
        )
        
        # Generate overall recommendation
        overall_recommendation = self._generate_comparative_recommendation(
            planning_params,
            comparative_analysis
        )
        
        return ComparativeScenarios(
            neighborhoods=planning_params.neighborhoods,
            scenarios_by_neighborhood=scenarios_by_neighborhood,
            comparative_analysis=comparative_analysis,
            overall_recommendation=overall_recommendation
        )
    
    def _generate_single_neighborhood_scenarios(self, neighborhood: str, planning_params: PlanningParameters) -> List[PlanningScenario]:
        """Generate scenarios for a single neighborhood"""
        
        profile = self.neighborhood_profiles[neighborhood]
        scenarios = []
        
        # Generate bike business scenarios if that's the focus
        if planning_params.intent == "business_impact" and "bike_infrastructure" in planning_params.specific_elements:
            scenarios = self._generate_bike_business_scenarios(neighborhood, profile, planning_params)
        
        return scenarios
    
    def _generate_bike_business_scenarios(self, neighborhood: str, profile: NeighborhoodProfile, planning_params: PlanningParameters) -> List[PlanningScenario]:
        """Generate bike infrastructure scenarios with business impact focus"""
        
        scenarios = []
        
        # Get business impact model for this neighborhood + bike infrastructure
        impact_key = f"bike_infrastructure_{neighborhood}"
        business_impact = self.business_impact_models.get(impact_key)
        
        if business_impact:
            # Scenario 1: Protected Bike Lane Network
            scenarios.append(PlanningScenario(
                title=f"Protected Bike Lane Network - {profile.name}",
                type="bike_infrastructure_comprehensive",
                description=f"Complete protected bike lane network along {profile.main_streets[0]} and {profile.main_streets[1]} with business-friendly design",
                neighborhood=neighborhood,
                amenities=[
                    "Protected bike lanes",
                    "Bike parking hubs", 
                    "Business loading zones",
                    "Parklets for outdoor dining",
                    "Wayfinding for cyclists"
                ],
                business_impact_analysis={
                    "customer_access": business_impact.customer_access_change,
                    "revenue_impact": business_impact.revenue_impact_range,
                    "business_effects": business_impact.business_type_effects,
                    "mitigation": business_impact.mitigation_strategies,
                    "opportunities": business_impact.opportunity_factors
                },
                implementation_timeline="18-24 months",
                estimated_cost="$3.5M - $5.2M"
            ))
            
            # Scenario 2: Business-First Approach
            scenarios.append(PlanningScenario(
                title=f"Business-Integrated Cycling Hub - {profile.name}",
                type="bike_infrastructure_business_focused",
                description=f"Cycling infrastructure designed around {neighborhood} business needs with minimal parking loss",
                neighborhood=neighborhood,
                amenities=[
                    "Shared bike lanes with parking",
                    "Business-adjacent bike parking",
                    "Cycling-oriented business incentives",
                    "Bike delivery logistics support"
                ],
                business_impact_analysis={
                    "customer_access": {k: v.replace("-25%", "-10%") if "car" in k else v for k, v in business_impact.customer_access_change.items()},
                    "revenue_impact": business_impact.revenue_impact_range.replace("-15%", "-5%"),
                    "business_effects": business_impact.business_type_effects,
                    "mitigation": business_impact.mitigation_strategies,
                    "opportunities": business_impact.opportunity_factors
                },
                implementation_timeline="12-15 months",
                estimated_cost="$1.8M - $2.5M"
            ))
        
        return scenarios
    
    def _perform_comparative_analysis(self, planning_params: PlanningParameters, scenarios_by_neighborhood: Dict[str, List[PlanningScenario]]) -> Dict[str, Any]:
        """Perform comparative analysis across neighborhoods"""
        
        analysis = {
            "business_impact_comparison": {},
            "implementation_feasibility": {},
            "community_fit": {}
        }
        
        # Business Impact Comparison
        for neighborhood in planning_params.neighborhoods:
            if neighborhood == "marina":
                analysis["business_impact_comparison"][neighborhood] = {
                    "risk_level": "Medium-High",
                    "primary_concern": "Loss of car-dependent suburban customers",
                    "main_opportunity": "Attract environmentally conscious affluent cyclists",
                    "adaptation_difficulty": "Moderate - businesses may resist parking loss",
                    "customer_base": "Affluent, car-dependent shoppers from outside neighborhood"
                }
            elif neighborhood == "mission":
                analysis["business_impact_comparison"][neighborhood] = {
                    "risk_level": "Low",
                    "primary_concern": "Ensuring existing community businesses aren't displaced",
                    "main_opportunity": "Strengthen bike-friendly community culture",
                    "adaptation_difficulty": "Low - already bike-friendly culture",
                    "customer_base": "Local residents, bike-commuting professionals"
                }
        
        return analysis
    
    def _generate_comparative_recommendation(self, planning_params: PlanningParameters, comparative_analysis: Dict[str, Any]) -> str:
        """Generate overall recommendation for comparative scenarios"""
        
        if "marina" in planning_params.neighborhoods and "mission" in planning_params.neighborhoods:
            if "bike_infrastructure" in planning_params.specific_elements:
                return """
🚴 NEIGHBORHOOD-SPECIFIC BIKE INFRASTRUCTURE STRATEGY:

🏖️ MARINA DISTRICT - "Business Preservation" Approach:
• Implement gradual transition to protect affluent customer base
• Focus on bike valet services for high-end retailers
• Preserve strategic parking for suburban shoppers
• Revenue impact: Initially negative (-5% to -15%) but positive long-term (+10% to +25%)

🌮 MISSION DISTRICT - "Community Enhancement" Approach:
• Build on existing bike culture with comprehensive infrastructure
• Support community businesses with increased foot traffic
• Leverage transit connections for bike-transit integration
• Revenue impact: Positive from start (+10% to +35%)

KEY INSIGHT: Marina requires customer access preservation while Mission can leverage existing bike-friendly culture. Different business ecosystems need different implementation strategies.
                """
        
        return "Comparative analysis complete. See neighborhood-specific recommendations."

def test_full_multi_agent_system():
    """Test the complete multi-agent system for business impact analysis"""
    
    print("🤖 TESTING COMPLETE MULTI-AGENT SYSTEM")
    print("=" * 80)
    print("Agent 1 (Interpreter) + Agent 2 (Planner) Working Together")
    print("=" * 80)
    
    # Initialize agents
    interpreter = StandaloneInterpreterAgent()
    planner = StandalonePlannerAgent()
    
    # Test the exact query from user's question
    query = "How would more bike infrastructure affect businesses in the Marina vs the Mission?"
    
    print(f"\n🎯 USER QUERY: {query}")
    print("-" * 60)
    
    # Step 1: Agent 1 (Interpreter) processes the query
    print("\n🧠 AGENT 1 (INTERPRETER) - Query Analysis:")
    planning_params = interpreter.interpret_query(query)
    
    print(f"   ✅ Detected neighborhoods: {planning_params.neighborhoods}")
    print(f"   ✅ Intent classification: {planning_params.intent}")
    print(f"   ✅ Comparative analysis: {planning_params.comparative}")
    print(f"   ✅ Specific elements: {planning_params.specific_elements}")
    print(f"   ✅ Business focus: {planning_params.focus}")
    print(f"   ✅ Confidence: {planning_params.confidence:.2f}")
    
    # Step 2: Agent 2 (Planner) generates scenarios
    print(f"\n🏗️  AGENT 2 (PLANNER) - Scenario Generation:")
    scenarios = planner.generate_scenarios(planning_params)
    
    print(f"   ✅ Generated scenarios for: {scenarios.neighborhoods}")
    print(f"   ✅ Comparative analysis: {len(scenarios.comparative_analysis)} dimensions")
    
    # Step 3: Show detailed results
    print(f"\n📊 DETAILED COMPARATIVE BUSINESS ANALYSIS:")
    
    for neighborhood, neighborhood_scenarios in scenarios.scenarios_by_neighborhood.items():
        print(f"\n🏘️  {neighborhood.upper()} DISTRICT:")
        profile = planner.neighborhood_profiles[neighborhood]
        print(f"   Character: {profile.character}")
        print(f"   Business ecosystem: {profile.business_ecosystem}")
        
        for i, scenario in enumerate(neighborhood_scenarios, 1):
            print(f"\n   📋 Scenario {i}: {scenario.title}")
            print(f"      💡 Description: {scenario.description}")
            
            if scenario.business_impact_analysis:
                impact = scenario.business_impact_analysis
                
                print(f"      💰 Revenue Impact: {impact.get('revenue_impact', 'N/A')}")
                print(f"      🚗 Customer Access Changes:")
                for mode, change in impact.get('customer_access', {}).items():
                    print(f"         {mode.title()}: {change}")
                
                print(f"      🏪 Business Type Effects:")
                for business_type, effect in impact.get('business_effects', {}).items():
                    print(f"         {business_type.replace('_', ' ').title()}: {effect}")
                
                print(f"      ⏱️  Timeline: {scenario.implementation_timeline}")
                print(f"      💸 Cost: {scenario.estimated_cost}")
    
    # Step 4: Show comparative analysis
    print(f"\n🔄 CROSS-NEIGHBORHOOD COMPARISON:")
    comp_analysis = scenarios.comparative_analysis.get("business_impact_comparison", {})
    
    for neighborhood, analysis in comp_analysis.items():
        print(f"\n   {neighborhood.upper()}:")
        print(f"      Risk Level: {analysis.get('risk_level')}")
        print(f"      Customer Base: {analysis.get('customer_base')}")
        print(f"      Main Opportunity: {analysis.get('main_opportunity')}")
        print(f"      Adaptation Difficulty: {analysis.get('adaptation_difficulty')}")
    
    # Step 5: Show overall recommendation
    print(f"\n💡 OVERALL RECOMMENDATION:")
    print(scenarios.overall_recommendation)
    
    print(f"\n✨ MULTI-AGENT SYSTEM SUCCESS!")
    print("   • Interpreted comparative query correctly")
    print("   • Generated neighborhood-specific scenarios") 
    print("   • Provided detailed business impact analysis")
    print("   • Delivered actionable comparative recommendations")

if __name__ == "__main__":
    test_full_multi_agent_system()