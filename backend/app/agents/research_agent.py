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
        
        # Intent detection with priority ordering
        intent_patterns = [
            (PlanningIntent.ANTI_DISPLACEMENT, ["displacement", "displace", "gentrification", "anti-displacement", "community", "preserve residents"]),
            (PlanningIntent.CLIMATE_RESILIENCE, ["flood", "climate", "resilience", "sea level", "adaptation", "waterfront protection"]),
            (PlanningIntent.WALKABILITY_IMPROVEMENT, ["walkable", "walkability", "pedestrian", "bike", "active transport"]),
            (PlanningIntent.TRANSIT_IMPROVEMENT, ["transit", "bart", "muni", "transportation", "commute"]),
            (PlanningIntent.MIXED_USE_DEVELOPMENT, ["mixed use", "mixed-use", "commercial", "ground floor", "retail"]),
            (PlanningIntent.HOUSING_DEVELOPMENT, ["housing", "units", "development", "affordable", "homes", "residential"])
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
        
        # Context-aware numeric extraction
        for num_str in numbers:
            num = int(num_str)
            
            # Units detection
            if re.search(rf'\b{num}\s*(units?|homes?|apartments?|housing)\b', query_lower):
                parsed["target_metrics"]["units"] = num
                parsed["confidence"] += 0.1
            
            # Height detection
            elif re.search(rf'\b{num}\s*(ft|feet|stories?|floors?)\b', query_lower):
                if "ft" in query_lower or "feet" in query_lower:
                    parsed["target_metrics"]["height_ft"] = num
                else:  # stories/floors - convert to feet (assume 12ft per story)
                    parsed["target_metrics"]["height_ft"] = num * 12
                parsed["confidence"] += 0.1
            
            # Affordability percentage
            elif re.search(rf'\b{num}%?\s*(affordable|inclusionary)\b', query_lower):
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
        """Conduct comprehensive neighborhood research"""
        raise NotImplementedError("Implementation pending")
    
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
    
    def _generate_opportunities_constraints(
        self, 
        neighborhood: NeighborhoodProfile, 
        intent: PlanningIntent
    ) -> tuple[List[str], List[str]]:
        """Identify key opportunities and constraints for this planning scenario"""
        raise NotImplementedError("Implementation pending")


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