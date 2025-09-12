"""
Mock Implementation of Research Agent for testing interface and data flow
"""

from .research_agent import (
    ResearchAgent, ResearchBrief, NeighborhoodProfile, ZoningDetails,
    SpatialContext, DemographicContext, TargetMetrics, PlanningIntent, SpatialFocus
)
from typing import Dict, Any, List


class MockResearchAgent(ResearchAgent):
    """Mock implementation for testing and development"""
    
    def __init__(self):
        super().__init__()
        # Pre-defined mock data for our 3 SF neighborhoods
        self.mock_neighborhoods = {
            "marina": self._get_marina_profile(),
            "hayes_valley": self._get_hayes_valley_profile(),
            "mission": self._get_mission_profile()
        }
    
    def research_query(self, user_query: str) -> ResearchBrief:
        """Mock implementation with realistic SF planning data"""
        
        # Parse query using simple keyword matching
        parsed = self._parse_query(user_query)
        
        # Get neighborhood profile
        neighborhood_key = parsed["neighborhood_key"]
        neighborhood_profile = self.mock_neighborhoods.get(
            neighborhood_key, 
            self._get_hayes_valley_profile()  # Default fallback
        )
        
        # Extract targets
        target_metrics = self._extract_target_metrics(user_query, parsed["intent"])
        
        # Generate opportunities and constraints
        opportunities, constraints = self._generate_opportunities_constraints(
            neighborhood_profile, parsed["intent"]
        )
        
        return ResearchBrief(
            original_query=user_query,
            intent=parsed["intent"],
            spatial_focus=parsed["spatial_focus"],
            target_metrics=target_metrics,
            neighborhood=neighborhood_profile,
            key_opportunities=opportunities,
            major_constraints=constraints,
            policy_considerations=self._get_policy_considerations(parsed["intent"]),
            confidence_score=0.85,  # Mock confidence
            research_notes=[f"Analysis based on {neighborhood_profile.display_name} zoning data"]
        )
    
    def _parse_query(self, query: str) -> Dict[str, Any]:
        """Simple keyword-based query parsing"""
        query_lower = query.lower()
        
        # Neighborhood detection
        if "marina" in query_lower:
            neighborhood_key = "marina"
        elif "hayes" in query_lower:
            neighborhood_key = "hayes_valley"
        elif "mission" in query_lower:
            neighborhood_key = "mission"
        else:
            neighborhood_key = "hayes_valley"  # Default
        
        # Intent detection
        if "affordable" in query_lower or "housing" in query_lower:
            intent = PlanningIntent.HOUSING_DEVELOPMENT
        elif "walkable" in query_lower or "walk" in query_lower:
            intent = PlanningIntent.WALKABILITY_IMPROVEMENT
        elif "density" in query_lower or "displacement" in query_lower:
            intent = PlanningIntent.ANTI_DISPLACEMENT
        elif "transit" in query_lower:
            intent = PlanningIntent.TRANSIT_IMPROVEMENT
        elif "flood" in query_lower or "climate" in query_lower:
            intent = PlanningIntent.CLIMATE_RESILIENCE
        else:
            intent = PlanningIntent.HOUSING_DEVELOPMENT  # Default
        
        # Spatial focus detection
        if "bart" in query_lower or "transit" in query_lower:
            spatial_focus = SpatialFocus.NEAR_TRANSIT
        elif "waterfront" in query_lower or "flood" in query_lower:
            spatial_focus = SpatialFocus.WATERFRONT
        elif "cultural" in query_lower or "mission" in query_lower:
            spatial_focus = SpatialFocus.CULTURAL_DISTRICT
        else:
            spatial_focus = SpatialFocus.GENERAL
        
        return {
            "neighborhood_key": neighborhood_key,
            "intent": intent,
            "spatial_focus": spatial_focus
        }
    
    def _extract_target_metrics(self, query: str, intent: PlanningIntent) -> TargetMetrics:
        """Extract numeric targets from query or use defaults based on intent"""
        
        # Default targets by intent and neighborhood scale
        defaults = {
            PlanningIntent.HOUSING_DEVELOPMENT: TargetMetrics(units=20, affordability_pct=0.20),
            PlanningIntent.ANTI_DISPLACEMENT: TargetMetrics(units=15, affordability_pct=0.25),
            PlanningIntent.TRANSIT_IMPROVEMENT: TargetMetrics(units=25, affordability_pct=0.15),
            PlanningIntent.WALKABILITY_IMPROVEMENT: TargetMetrics(units=10),
            PlanningIntent.CLIMATE_RESILIENCE: TargetMetrics(units=8)
        }
        
        return defaults.get(intent, TargetMetrics(units=15, affordability_pct=0.20))
    
    def _generate_opportunities_constraints(
        self, 
        neighborhood: NeighborhoodProfile, 
        intent: PlanningIntent
    ) -> tuple[List[str], List[str]]:
        """Generate realistic opportunities and constraints"""
        
        # Base opportunities and constraints from neighborhood
        opportunities = [
            f"Existing {neighborhood.zoning.zone_type} zoning allows {neighborhood.zoning.max_far} FAR",
            f"Transit access rated as {neighborhood.spatial.transit_access}",
        ]
        
        constraints = list(neighborhood.constraints)
        
        # Intent-specific considerations
        if intent == PlanningIntent.HOUSING_DEVELOPMENT:
            opportunities.append(f"{neighborhood.zoning.affordable_housing_req*100:.0f}% inclusionary housing requirement")
            if neighborhood.spatial.transit_access == "excellent":
                opportunities.append("Parking variances possible due to excellent transit")
        
        elif intent == PlanningIntent.ANTI_DISPLACEMENT:
            constraints.append(f"Displacement risk: {neighborhood.demographics.displacement_risk}")
            opportunities.append("Community land trust strategies applicable")
        
        elif intent == PlanningIntent.CLIMATE_RESILIENCE:
            if neighborhood.spatial.flood_risk:
                constraints.append(f"Flood risk: {neighborhood.spatial.flood_risk}")
                opportunities.append("Elevated development strategies needed")
        
        return opportunities, constraints
    
    def _get_policy_considerations(self, intent: PlanningIntent) -> List[str]:
        """Get relevant policy considerations"""
        base_policies = ["SF Planning Code compliance required", "Community input process needed"]
        
        intent_policies = {
            PlanningIntent.HOUSING_DEVELOPMENT: ["Inclusionary housing requirements", "CEQA review"],
            PlanningIntent.ANTI_DISPLACEMENT: ["Tenant protections", "Community benefits agreement"],
            PlanningIntent.CLIMATE_RESILIENCE: ["Sea level rise projections", "Building code updates"],
            PlanningIntent.WALKABILITY_IMPROVEMENT: ["ADA compliance", "Traffic impact analysis"]
        }
        
        return base_policies + intent_policies.get(intent, [])
    
    def _get_marina_profile(self) -> NeighborhoodProfile:
        """Marina District neighborhood profile"""
        return NeighborhoodProfile(
            name="marina",
            display_name="Marina District",
            area_type="residential",
            characteristics=["low_density", "waterfront", "affluent"],
            zoning=ZoningDetails(
                zone_type="RH-1",
                max_far=0.8,
                max_height_ft=40,
                min_parking=1.0,
                ground_floor_commercial=False,
                affordable_housing_req=0.12
            ),
            spatial=SpatialContext(
                transit_access="limited",
                walk_to_bart_min=25,
                flood_risk="high",
                seismic_zone="moderate",
                historic_overlay=False
            ),
            demographics=DemographicContext(
                median_income=120000,
                displacement_risk="low",
                cultural_assets="low",
                gentrification_pressure="low"
            ),
            constraints=["flood_zone", "height_limit", "parking_requirements"]
        )
    
    def _get_hayes_valley_profile(self) -> NeighborhoodProfile:
        """Hayes Valley neighborhood profile"""
        return NeighborhoodProfile(
            name="hayes_valley",
            display_name="Hayes Valley",
            area_type="mixed_use",
            characteristics=["mixed_use", "transit_rich", "gentrifying"],
            zoning=ZoningDetails(
                zone_type="NCT-3",
                max_far=3.0,
                max_height_ft=55,
                min_parking=0.5,
                ground_floor_commercial=True,
                affordable_housing_req=0.20
            ),
            spatial=SpatialContext(
                transit_access="excellent",
                walk_to_bart_min=3,
                flood_risk=None,
                seismic_zone="moderate",
                historic_overlay=True
            ),
            demographics=DemographicContext(
                median_income=95000,
                displacement_risk="high",
                cultural_assets="medium",
                gentrification_pressure="high"
            ),
            constraints=["historic_preservation", "displacement_pressure"]
        )
    
    def _get_mission_profile(self) -> NeighborhoodProfile:
        """Mission District neighborhood profile"""
        return NeighborhoodProfile(
            name="mission",
            display_name="Mission District", 
            area_type="mixed_use",
            characteristics=["dense", "diverse", "cultural"],
            zoning=ZoningDetails(
                zone_type="NCT-4",
                max_far=4.0,
                max_height_ft=85,
                min_parking=0.25,
                ground_floor_commercial=True,
                affordable_housing_req=0.25
            ),
            spatial=SpatialContext(
                transit_access="good",
                walk_to_bart_min=8,
                flood_risk=None,
                seismic_zone="high",
                historic_overlay=False
            ),
            demographics=DemographicContext(
                median_income=75000,
                displacement_risk="high",
                cultural_assets="high",
                gentrification_pressure="high"
            ),
            constraints=["displacement_risk", "cultural_preservation", "seismic_zone"]
        )