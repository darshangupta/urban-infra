"""
Agent 1: Research Agent - Enhanced query understanding + comprehensive neighborhood research
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from enum import Enum


class PlanningIntent(str, Enum):
    """Planning intent categories"""
    HOUSING_DEVELOPMENT = "housing_development"
    TRANSIT_IMPROVEMENT = "transit_improvement" 
    MIXED_USE_DEVELOPMENT = "mixed_use_development"
    WALKABILITY_IMPROVEMENT = "walkability_improvement"
    CLIMATE_RESILIENCE = "climate_resilience"
    ANTI_DISPLACEMENT = "anti_displacement"


class SpatialFocus(str, Enum):
    """Spatial focus areas"""
    NEAR_TRANSIT = "near_transit"
    WATERFRONT = "waterfront"
    CULTURAL_DISTRICT = "cultural_district"
    HISTORIC_AREA = "historic_area"
    GENERAL = "general"


class ZoningDetails(BaseModel):
    """Detailed zoning information"""
    zone_type: str  # "RH-1", "NCT-3", "NCT-4"
    max_far: float
    max_height_ft: int
    min_parking: float
    ground_floor_commercial: bool
    affordable_housing_req: float  # percentage as decimal
    

class SpatialContext(BaseModel):
    """Spatial analysis results"""
    transit_access: str  # "excellent", "good", "limited"
    walk_to_bart_min: Optional[int]  # walking minutes to nearest BART
    flood_risk: Optional[str]  # "high", "medium", "low", None
    seismic_zone: Optional[str]
    historic_overlay: bool
    

class DemographicContext(BaseModel):
    """Neighborhood demographic context"""
    median_income: Optional[int]
    displacement_risk: str  # "high", "medium", "low"
    cultural_assets: str  # "high", "medium", "low"
    gentrification_pressure: str  # "high", "medium", "low"


class NeighborhoodProfile(BaseModel):
    """Complete neighborhood research profile"""
    name: str
    display_name: str
    area_type: str
    characteristics: List[str]
    zoning: ZoningDetails
    spatial: SpatialContext
    demographics: DemographicContext
    constraints: List[str]


class TargetMetrics(BaseModel):
    """Extracted target metrics from query"""
    units: Optional[int] = None
    affordability_pct: Optional[float] = None  # percentage as decimal
    height_ft: Optional[int] = None
    far: Optional[float] = None
    parking_spaces: Optional[int] = None


class ResearchBrief(BaseModel):
    """Comprehensive research briefing for planning agents"""
    # Query Analysis
    original_query: str
    intent: PlanningIntent
    spatial_focus: SpatialFocus
    target_metrics: TargetMetrics
    
    # Neighborhood Research
    neighborhood: NeighborhoodProfile
    
    # Planning Context
    key_opportunities: List[str]
    major_constraints: List[str]
    policy_considerations: List[str]
    
    # Metadata
    confidence_score: float  # 0.0 to 1.0, how confident we are in this analysis
    research_notes: List[str]  # Any important caveats or assumptions


class ResearchAgent:
    """Agent 1: Enhanced research and query understanding"""
    
    def __init__(self):
        """Initialize research agent with API clients"""
        self.api_base = "http://localhost:8001/api/v1"
        
    def research_query(self, user_query: str) -> ResearchBrief:
        """
        Main entry point: Convert user query into comprehensive research brief
        
        Args:
            user_query: Natural language planning query
            
        Returns:
            ResearchBrief: Comprehensive analysis ready for scenario planning
        """
        # This is the interface contract - implementation comes next
        raise NotImplementedError("Implementation pending")
    
    def _parse_query(self, query: str) -> Dict[str, Any]:
        """Parse natural language query into structured components"""
        import re
        
        query_lower = query.lower()
        parsed = {
            "neighborhood_name": None,
            "neighborhood_key": None,
            "intent": PlanningIntent.HOUSING_DEVELOPMENT,
            "spatial_focus": SpatialFocus.GENERAL,
            "target_metrics": {},
            "confidence": 0.0
        }
        
        # Neighborhood detection with variations
        neighborhood_patterns = {
            "marina": ["marina", "marina district", "the marina"],
            "hayes_valley": ["hayes valley", "hayes", "hayes-valley"],  
            "mission": ["mission", "mission district", "the mission"]
        }
        
        for key, variations in neighborhood_patterns.items():
            for variation in variations:
                if variation in query_lower:
                    parsed["neighborhood_key"] = key
                    parsed["neighborhood_name"] = {
                        "marina": "Marina District",
                        "hayes_valley": "Hayes Valley", 
                        "mission": "Mission District"
                    }[key]
                    parsed["confidence"] += 0.3
                    break
            if parsed["neighborhood_name"]:
                break
        
        # Intent detection with priority ordering (most specific first)
        intent_patterns = [
            (PlanningIntent.ANTI_DISPLACEMENT, ["displacement", "displace", "gentrification", "anti-displacement", "preserve residents", "without displacing"]),
            (PlanningIntent.WALKABILITY_IMPROVEMENT, ["walkable", "walkability", "pedestrian", "bike", "active transport", "more walkable"]),
            (PlanningIntent.CLIMATE_RESILIENCE, ["flood", "climate", "resilience", "sea level", "adaptation", "climate-resilient"]),
            (PlanningIntent.MIXED_USE_DEVELOPMENT, ["mixed use", "mixed-use", "ground floor", "retail", "commercial"]),
            (PlanningIntent.TRANSIT_IMPROVEMENT, ["transit-oriented", "near transit", "transportation", "commute"]),
            (PlanningIntent.HOUSING_DEVELOPMENT, ["housing", "units", "development", "affordable", "homes", "residential", "bart"])
        ]
        
        for intent, keywords in intent_patterns:
            if any(keyword in query_lower for keyword in keywords):
                parsed["intent"] = intent
                parsed["confidence"] += 0.25
                break
        
        # Spatial focus detection
        spatial_patterns = [
            (SpatialFocus.NEAR_TRANSIT, ["near transit", "bart", "transit-oriented", "near station"]),
            (SpatialFocus.WATERFRONT, ["waterfront", "bay", "marina", "flood", "shoreline"]),
            (SpatialFocus.CULTURAL_DISTRICT, ["cultural", "mission", "arts", "community"]),
            (SpatialFocus.HISTORIC_AREA, ["historic", "preservation", "heritage"])
        ]
        
        for focus, keywords in spatial_patterns:
            if any(keyword in query_lower for keyword in keywords):
                parsed["spatial_focus"] = focus
                parsed["confidence"] += 0.15
                break
        
        # Extract numeric targets using regex
        numbers = re.findall(r'\b(\d+)\b', query)
        
        # Context-aware numeric extraction - check in specific order
        for num_str in numbers:
            num = int(num_str)
            
            # Units detection (allow words in between)
            if re.search(rf'\b{num}\s+.*?\b(units?|homes?|apartments?)\b', query_lower):
                parsed["target_metrics"]["units"] = num
                parsed["confidence"] += 0.1
            
            # Height detection  
            elif re.search(rf'\b{num}\s*(ft|feet|stories?|floors?)\b', query_lower):
                if "ft" in query_lower or "feet" in query_lower:
                    parsed["target_metrics"]["height_ft"] = num
                else:  # stories/floors - convert to feet (assume 12ft per story)
                    parsed["target_metrics"]["height_ft"] = num * 12
                parsed["confidence"] += 0.1
            
            # Affordability percentage (with % sign or explicit "affordable/inclusionary")
            elif re.search(rf'\b{num}%\s*(affordable|inclusionary)?\b', query_lower) or \
                 re.search(rf'\b{num}\s*percent\s*(affordable|inclusionary)\b', query_lower):
                parsed["target_metrics"]["affordability_pct"] = num / 100.0 if num > 1 else num
                parsed["confidence"] += 0.1
        
        # Affordability keywords without numbers
        if any(word in query_lower for word in ["affordable", "inclusionary", "low income"]):
            if "affordability_pct" not in parsed["target_metrics"]:
                # Default to SF inclusionary requirements by neighborhood
                default_affordability = {
                    "marina": 0.12,
                    "hayes_valley": 0.20,
                    "mission": 0.25
                }
                parsed["target_metrics"]["affordability_pct"] = default_affordability.get(
                    parsed["neighborhood_key"], 0.20
                )
                parsed["confidence"] += 0.05
        
        # Default neighborhood if none detected
        if not parsed["neighborhood_name"]:
            parsed["neighborhood_key"] = "hayes_valley"
            parsed["neighborhood_name"] = "Hayes Valley"
            parsed["confidence"] = max(0.1, parsed["confidence"])  # Low confidence for defaults
        
        return parsed
    
    def _research_neighborhood(self, neighborhood_name: str) -> NeighborhoodProfile:
        """Conduct comprehensive neighborhood research using live API data"""
        import httpx
        
        # Normalize neighborhood name for API calls
        neighborhood_key = {
            "Marina District": "marina",
            "Hayes Valley": "hayes_valley", 
            "Mission District": "mission"
        }.get(neighborhood_name, "hayes_valley")
        
        try:
            # Fetch zoning data from our API
            with httpx.Client() as client:
                zoning_response = client.get(f"{self.api_base}/neighborhoods/{neighborhood_key}/zoning")
                
                if zoning_response.status_code != 200:
                    # Fallback to mock data if API unavailable
                    return self._get_fallback_neighborhood_profile(neighborhood_name)
                
                zoning_data = zoning_response.json()
                
                # Extract zoning details
                rules = zoning_data.get("rules", {})
                zoning_details = ZoningDetails(
                    zone_type=zoning_data.get("zone_type", "NCT-3"),
                    max_far=rules.get("max_far", 2.0),
                    max_height_ft=rules.get("max_height_ft", 45),
                    min_parking=rules.get("min_parking_per_unit", 0.5),
                    ground_floor_commercial=rules.get("ground_floor_commercial", False),
                    affordable_housing_req=rules.get("inclusionary_housing_pct", 0.20)
                )
                
                # Build spatial context from API data and known SF characteristics
                spatial_context = self._build_spatial_context(neighborhood_key, zoning_data)
                
                # Build demographic context
                demographics = self._build_demographic_context(neighborhood_key)
                
                # Determine area type and characteristics
                area_type, characteristics = self._determine_area_characteristics(neighborhood_key, zoning_details)
                
                # Extract constraints
                constraints = self._extract_constraints(neighborhood_key, zoning_data, spatial_context)
                
                return NeighborhoodProfile(
                    name=neighborhood_key,
                    display_name=neighborhood_name,
                    area_type=area_type,
                    characteristics=characteristics,
                    zoning=zoning_details,
                    spatial=spatial_context,
                    demographics=demographics,
                    constraints=constraints
                )
                
        except Exception as e:
            # Robust fallback to ensure system continues working
            print(f"Warning: API error in neighborhood research: {e}")
            return self._get_fallback_neighborhood_profile(neighborhood_name)
    
    def _analyze_spatial_context(self, neighborhood: str, query_context: Dict) -> SpatialContext:
        """Perform spatial analysis based on query requirements"""
        raise NotImplementedError("Implementation pending")
    
    def _extract_target_metrics(self, query: str, intent: PlanningIntent) -> TargetMetrics:
        """Extract specific numeric targets from query"""
        # Use the parsing results and enhance with intent-specific defaults
        parsed = self._parse_query(query)
        metrics_dict = parsed["target_metrics"]
        
        # Intent-based defaults for missing metrics
        intent_defaults = {
            PlanningIntent.HOUSING_DEVELOPMENT: {"units": 20, "affordability_pct": 0.20},
            PlanningIntent.ANTI_DISPLACEMENT: {"units": 15, "affordability_pct": 0.30},
            PlanningIntent.TRANSIT_IMPROVEMENT: {"units": 30, "affordability_pct": 0.15},
            PlanningIntent.MIXED_USE_DEVELOPMENT: {"units": 25, "affordability_pct": 0.18},
            PlanningIntent.WALKABILITY_IMPROVEMENT: {"units": 10},
            PlanningIntent.CLIMATE_RESILIENCE: {"units": 12}
        }
        
        # Apply defaults for missing values
        defaults = intent_defaults.get(intent, {"units": 15, "affordability_pct": 0.20})
        
        return TargetMetrics(
            units=metrics_dict.get("units", defaults.get("units")),
            affordability_pct=metrics_dict.get("affordability_pct", defaults.get("affordability_pct")),
            height_ft=metrics_dict.get("height_ft"),
            far=metrics_dict.get("far"),
            parking_spaces=metrics_dict.get("parking_spaces")
        )
    
    def _build_spatial_context(self, neighborhood_key: str, zoning_data: Dict) -> SpatialContext:
        """Build spatial context from API data and SF knowledge"""
        # SF neighborhood spatial characteristics (could be enhanced with real spatial analysis)
        spatial_profiles = {
            "marina": {
                "transit_access": "limited",
                "walk_to_bart_min": 25,
                "flood_risk": "high", 
                "seismic_zone": "moderate",
                "historic_overlay": False
            },
            "hayes_valley": {
                "transit_access": "excellent",
                "walk_to_bart_min": 3,
                "flood_risk": None,
                "seismic_zone": "moderate", 
                "historic_overlay": True
            },
            "mission": {
                "transit_access": "good",
                "walk_to_bart_min": 8,
                "flood_risk": None,
                "seismic_zone": "high",
                "historic_overlay": False
            }
        }
        
        profile = spatial_profiles.get(neighborhood_key, spatial_profiles["hayes_valley"])
        return SpatialContext(**profile)
    
    def _build_demographic_context(self, neighborhood_key: str) -> DemographicContext:
        """Build demographic context from neighborhood knowledge"""
        demographic_profiles = {
            "marina": {
                "median_income": 120000,
                "displacement_risk": "low",
                "cultural_assets": "low",
                "gentrification_pressure": "low"
            },
            "hayes_valley": {
                "median_income": 95000,
                "displacement_risk": "high", 
                "cultural_assets": "medium",
                "gentrification_pressure": "high"
            },
            "mission": {
                "median_income": 75000,
                "displacement_risk": "high",
                "cultural_assets": "high",
                "gentrification_pressure": "high"
            }
        }
        
        profile = demographic_profiles.get(neighborhood_key, demographic_profiles["hayes_valley"])
        return DemographicContext(**profile)
    
    def _determine_area_characteristics(self, neighborhood_key: str, zoning: ZoningDetails) -> tuple[str, List[str]]:
        """Determine area type and characteristics from zoning and neighborhood"""
        area_profiles = {
            "marina": ("residential", ["low_density", "waterfront", "affluent"]),
            "hayes_valley": ("mixed_use", ["mixed_use", "transit_rich", "gentrifying"]),
            "mission": ("mixed_use", ["dense", "diverse", "cultural"])
        }
        
        return area_profiles.get(neighborhood_key, ("mixed_use", ["urban", "developing"]))
    
    def _extract_constraints(self, neighborhood_key: str, zoning_data: Dict, spatial: SpatialContext) -> List[str]:
        """Extract planning constraints from neighborhood data"""
        constraints = []
        
        # Zoning-based constraints
        rules = zoning_data.get("rules", {})
        if rules.get("max_height_ft", 0) <= 40:
            constraints.append("height_limit")
        if rules.get("min_parking_per_unit", 0) >= 1.0:
            constraints.append("parking_requirements")
        
        # Spatial constraints
        if spatial.flood_risk:
            constraints.append("flood_zone")
        if spatial.historic_overlay:
            constraints.append("historic_preservation")
        if spatial.seismic_zone == "high":
            constraints.append("seismic_zone")
        
        # Neighborhood-specific constraints
        neighborhood_constraints = {
            "marina": ["flood_zone", "height_limit", "parking_requirements"],
            "hayes_valley": ["historic_preservation", "displacement_pressure"],
            "mission": ["displacement_risk", "cultural_preservation", "seismic_zone"]
        }
        
        # Merge with neighborhood-specific constraints
        specific_constraints = neighborhood_constraints.get(neighborhood_key, [])
        all_constraints = list(set(constraints + specific_constraints))
        
        return all_constraints
    
    def _get_fallback_neighborhood_profile(self, neighborhood_name: str) -> NeighborhoodProfile:
        """Fallback neighborhood profile when API is unavailable"""
        # Use the mock implementation as fallback
        from .mock_research_agent import MockResearchAgent
        mock_agent = MockResearchAgent()
        
        neighborhood_key = {
            "Marina District": "marina",
            "Hayes Valley": "hayes_valley",
            "Mission District": "mission"
        }.get(neighborhood_name, "hayes_valley")
        
        return mock_agent.mock_neighborhoods[neighborhood_key]
    
    def _generate_opportunities_constraints(
        self, 
        neighborhood: NeighborhoodProfile, 
        intent: PlanningIntent
    ) -> tuple[List[str], List[str]]:
        """Identify key opportunities and constraints for this planning scenario"""
        # Base opportunities from neighborhood characteristics
        opportunities = [
            f"Existing {neighborhood.zoning.zone_type} zoning allows {neighborhood.zoning.max_far} FAR",
            f"Transit access rated as {neighborhood.spatial.transit_access}",
        ]
        
        # Base constraints from neighborhood
        constraints = list(neighborhood.constraints)
        
        # Intent-specific opportunities and constraints
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
        
        elif intent == PlanningIntent.WALKABILITY_IMPROVEMENT:
            if neighborhood.spatial.transit_access != "limited":
                opportunities.append("Good transit connectivity supports walkability")
            opportunities.append("Street activation through ground floor uses")
        
        elif intent == PlanningIntent.TRANSIT_IMPROVEMENT:
            if neighborhood.spatial.walk_to_bart_min and neighborhood.spatial.walk_to_bart_min <= 10:
                opportunities.append("Close BART access enables transit-oriented development")
            opportunities.append("Transit-supportive density encourages ridership")
        
        return opportunities, constraints


# Example usage and testing
if __name__ == "__main__":
    agent = ResearchAgent()
    
    # Test cases from our CLAUDE.md examples
    test_queries = [
        "Add affordable housing near BART in Hayes Valley",
        "Make the Marina more walkable while respecting flood risks", 
        "Increase density in Mission without displacing existing residents"
    ]
    
    for query in test_queries:
        print(f"\nTesting: {query}")
        try:
            brief = agent.research_query(query)
            print(f"Intent: {brief.intent}")
            print(f"Neighborhood: {brief.neighborhood.display_name}")
            print(f"Opportunities: {brief.key_opportunities}")
        except NotImplementedError:
            print("Implementation pending...")