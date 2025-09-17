"""
Agent 2: Planner
Generate neighborhood-specific scenarios with business ecosystem awareness.
Handles comparative planning and business impact modeling.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from dataclasses import dataclass
import random
from .interpreter import PlanningParameters, NeighborhoodProfile

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

class PlannerAgent:
    """
    Agent 2: Advanced scenario generation for urban planning with business impact focus.
    
    Capabilities:
    - Neighborhood-specific scenario generation
    - Business ecosystem modeling  
    - Comparative planning across neighborhoods
    - Implementation feasibility assessment
    - Cost-benefit analysis integration
    """
    
    def __init__(self):
        self.neighborhood_profiles = self._load_neighborhood_profiles()
        self.business_impact_models = self._load_business_impact_models()
        
    def _load_neighborhood_profiles(self) -> Dict[str, NeighborhoodProfile]:
        """Load neighborhood profiles (same as interpreter)"""
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
            ),
            "hayes_valley": NeighborhoodProfile(
                name="Hayes Valley",
                zoning="NCT-3 (Neighborhood Commercial Transit)",
                character="Transit-rich, mixed-use, recently gentrified, walkable",
                main_streets=["Hayes Street", "Grove Street", "Fell Street", "Oak Street"],
                landmarks=["Patricia's Green", "Hayes Valley Playground", "SF Jazz Center"],
                transport=["Van Ness-UNM BART", "Hayes-Fillmore Muni", "Multiple transit lines"],
                business_ecosystem="Upscale boutiques, galleries, restaurants, design studios, pedestrian-oriented",
                demographic_profile="Young professionals, artists, design workers, low car ownership",
                development_pressure="Medium - managed growth with community input",
                constraints=["Historic preservation", "Transit capacity", "Small lot sizes"]
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
        """
        Generate scenarios based on planning parameters.
        Handles both single neighborhood and comparative multi-neighborhood planning.
        """
        
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
        """Generate 3-4 scenarios for a single neighborhood"""
        
        profile = self.neighborhood_profiles[neighborhood]
        scenarios = []
        
        # Scenario generation based on intent
        if planning_params.intent == "business_impact" and "bike_infrastructure" in planning_params.specific_elements:
            scenarios = self._generate_bike_business_scenarios(neighborhood, profile, planning_params)
        elif planning_params.intent == "mobility":
            scenarios = self._generate_mobility_scenarios(neighborhood, profile, planning_params)
        elif planning_params.intent == "housing_development":
            scenarios = self._generate_housing_scenarios(neighborhood, profile, planning_params)
        else:
            scenarios = self._generate_mixed_scenarios(neighborhood, profile, planning_params)
        
        return scenarios
    
    def _generate_bike_business_scenarios(self, neighborhood: str, profile: NeighborhoodProfile, planning_params: PlanningParameters) -> List[PlanningScenario]:
        """Generate bike infrastructure scenarios with business impact focus"""
        
        scenarios = []
        
        # Get business impact model for this neighborhood + bike infrastructure
        impact_key = f"bike_infrastructure_{neighborhood}"
        business_impact = self.business_impact_models.get(impact_key, self._default_business_impact())
        
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
                "mitigation": business_impact.mitigation_strategies
            },
            implementation_timeline="18-24 months",
            estimated_cost="$3.5M - $5.2M"
        ))
        
        # Scenario 2: Business-First Bike Infrastructure
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
                "customer_access": {k: v.replace("-25%", "-10%") for k, v in business_impact.customer_access_change.items()},
                "revenue_impact": business_impact.revenue_impact_range.replace("-15%", "-5%"),
                "business_effects": business_impact.business_type_effects,
                "mitigation": business_impact.mitigation_strategies
            },
            implementation_timeline="12-15 months",
            estimated_cost="$1.8M - $2.5M"
        ))
        
        # Scenario 3: Gradual Transition Model
        scenarios.append(PlanningScenario(
            title=f"Phased Bike Infrastructure Transition - {profile.name}",
            type="bike_infrastructure_gradual",
            description=f"Three-phase implementation allowing {neighborhood} businesses to adapt gradually",
            neighborhood=neighborhood,
            amenities=[
                "Phase 1: Painted bike lanes",
                "Phase 2: Buffered lanes + business input",
                "Phase 3: Protected lanes with proven design",
                "Business adaptation support program"
            ],
            business_impact_analysis={
                "customer_access": business_impact.customer_access_change,
                "revenue_impact": "Phases allow adaptation: 0% to +20%",
                "business_effects": business_impact.business_type_effects,
                "mitigation": business_impact.mitigation_strategies + ["Phased implementation reduces shock"]
            },
            implementation_timeline="36 months (phased)",
            estimated_cost="$2.5M - $4.0M"
        ))
        
        return scenarios
    
    def _generate_mobility_scenarios(self, neighborhood: str, profile: NeighborhoodProfile, planning_params: PlanningParameters) -> List[PlanningScenario]:
        """Generate general mobility scenarios"""
        return [
            PlanningScenario(
                title=f"Complete Streets - {profile.name}",
                type="complete_streets",
                description=f"Transform {profile.main_streets[0]} into a complete street with bike lanes, wider sidewalks, and transit improvements",
                neighborhood=neighborhood,
                amenities=["Protected bike lanes", "Enhanced bus stops", "Wider sidewalks", "Street trees"]
            ),
            PlanningScenario(
                title=f"Transit-Oriented Mobility - {profile.name}",
                type="transit_focused",
                description=f"Improve connections to {profile.transport[0]} with bike-share and pedestrian improvements",
                neighborhood=neighborhood,
                amenities=["Bike share stations", "Improved crosswalks", "Transit plaza", "Wayfinding"]
            )
        ]
    
    def _generate_housing_scenarios(self, neighborhood: str, profile: NeighborhoodProfile, planning_params: PlanningParameters) -> List[PlanningScenario]:
        """Generate housing-focused scenarios"""
        return [
            PlanningScenario(
                title=f"Affordable Housing Development - {profile.name}",
                type="affordable_housing",
                description=f"Mixed-income development near {profile.landmarks[0]} with community benefits",
                neighborhood=neighborhood,
                units=120,
                affordable_percentage=35,
                height_ft=55,
                amenities=["Affordable units", "Community space", "Ground floor retail"]
            )
        ]
    
    def _generate_mixed_scenarios(self, neighborhood: str, profile: NeighborhoodProfile, planning_params: PlanningParameters) -> List[PlanningScenario]:
        """Generate mixed-use scenarios"""
        return [
            PlanningScenario(
                title=f"Mixed-Use Development - {profile.name}",
                type="mixed_use",
                description=f"Balanced development approach for {neighborhood} addressing multiple community needs",
                neighborhood=neighborhood,
                amenities=["Mixed-use spaces", "Community amenities", "Green infrastructure"]
            )
        ]
    
    def _perform_comparative_analysis(self, planning_params: PlanningParameters, scenarios_by_neighborhood: Dict[str, List[PlanningScenario]]) -> Dict[str, Any]:
        """Perform comparative analysis across neighborhoods"""
        
        analysis = {
            "business_impact_comparison": {},
            "implementation_feasibility": {},
            "community_fit": {},
            "cost_benefit": {}
        }
        
        # Business Impact Comparison
        if "business_impact" in planning_params.specific_elements:
            for neighborhood, scenarios in scenarios_by_neighborhood.items():
                profile = self.neighborhood_profiles[neighborhood]
                
                # Analyze business ecosystem compatibility
                if neighborhood == "marina":
                    analysis["business_impact_comparison"][neighborhood] = {
                        "risk_level": "Medium-High",
                        "primary_concern": "Loss of car-dependent suburban customers",
                        "main_opportunity": "Attract environmentally conscious affluent cyclists",
                        "adaptation_difficulty": "Moderate - businesses may resist parking loss"
                    }
                elif neighborhood == "mission":
                    analysis["business_impact_comparison"][neighborhood] = {
                        "risk_level": "Low",
                        "primary_concern": "Ensuring existing community businesses aren't displaced",
                        "main_opportunity": "Strengthen bike-friendly community culture",
                        "adaptation_difficulty": "Low - already bike-friendly culture"
                    }
        
        # Implementation Feasibility
        for neighborhood in planning_params.neighborhoods:
            profile = self.neighborhood_profiles[neighborhood]
            
            if neighborhood == "marina":
                analysis["implementation_feasibility"][neighborhood] = {
                    "political_challenges": "High - NIMBY resistance, parking concerns",
                    "technical_difficulty": "Medium - wider streets allow flexibility",
                    "timeline": "Longer due to community resistance"
                }
            elif neighborhood == "mission":
                analysis["implementation_feasibility"][neighborhood] = {
                    "political_challenges": "Medium - gentrification concerns",
                    "technical_difficulty": "High - narrow streets, high density",
                    "timeline": "Moderate with strong community engagement"
                }
        
        return analysis
    
    def _generate_comparative_recommendation(self, planning_params: PlanningParameters, comparative_analysis: Dict[str, Any]) -> str:
        """Generate overall recommendation for comparative scenarios"""
        
        if "marina" in planning_params.neighborhoods and "mission" in planning_params.neighborhoods:
            if "bike_infrastructure" in planning_params.specific_elements:
                return """
                Recommended Approach - Neighborhood-Specific Implementation:
                
                🏖️ Marina District: Implement "Business-Integrated Cycling Hub" with gradual transition
                - Focus on preserving customer access while adding cycling amenities
                - Partner with high-end businesses for cycling valet services
                - Leverage recreation-oriented demographics
                
                🌮 Mission District: Implement "Protected Bike Lane Network" with community input
                - Build on existing bike culture and community support
                - Ensure cultural business preservation measures
                - Coordinate with transit improvements
                
                The different business ecosystems require tailored approaches: Marina needs customer access preservation while Mission can leverage existing bike-friendly culture.
                """
        
        return "Comparative analysis complete. See neighborhood-specific recommendations."
    
    def _default_business_impact(self) -> BusinessImpactModel:
        """Default business impact model when specific model not available"""
        return BusinessImpactModel(
            customer_access_change={"general": "Varied impacts depending on implementation"},
            revenue_impact_range="Context dependent",
            business_type_effects={"general": "Requires specific analysis"},
            mitigation_strategies=["Stakeholder engagement", "Phased implementation"],
            opportunity_factors=["Improved streetscape", "New customer demographics"]
        )