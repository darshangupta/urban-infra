"""
Agent 1: Interpreter - Advanced natural language processing for urban planning queries.
Handles multi-neighborhood detection, comparative analysis, and nuanced intent extraction.
"""

from typing import Dict, Any, List, Optional
import json
import httpx
import re
from pydantic import BaseModel
from dataclasses import dataclass
from enum import Enum


class QueryIntent(str, Enum):
    """Standardized query intent types"""
    BUSINESS_IMPACT = "business_impact"
    MOBILITY = "mobility" 
    HOUSING_DEVELOPMENT = "housing_development"
    ENVIRONMENTAL = "environmental"
    EQUITY = "equity"
    MIXED_PLANNING = "mixed_planning"
    SCENARIO_PLANNING = "scenario_planning"
    COMPARATIVE = "comparative"


class QueryDomain(str, Enum):
    """Standardized domain classifications"""
    TRANSPORTATION = "transportation"
    HOUSING = "housing"
    CLIMATE = "climate"
    ECONOMICS = "economics"
    ENVIRONMENT = "environment"
    MIXED = "mixed"


class QueryType(str, Enum):
    """Query operation types"""
    INCREASE = "increase"
    DECREASE = "decrease"
    WHAT_IF = "what_if"
    COMPARISON = "comparison"
    IMPACT_ANALYSIS = "impact_analysis"
    SOLUTION_SEEKING = "solution_seeking"


class QueryClassification(BaseModel):
    """Enhanced dynamic query classification output"""
    intent: QueryIntent
    domain: QueryDomain
    sub_domain: str  # Specific area within domain
    query_type: QueryType
    neighborhoods: List[str]
    parameters: Dict[str, Any]  # Extracted quantitative values
    confidence: float
    comparative: bool
    specific_elements: List[str]
    spatial_focus: str
    constraints: List[str]


class UrbanPlanningAPIClient:
    """Client for calling our neighborhood APIs"""
    
    def __init__(self, base_url: str = "http://localhost:8001/api/v1"):
        self.base_url = base_url
    
    def get_neighborhood_data(self, action: str, neighborhood: str = None, **kwargs) -> Dict[str, Any]:
        """Execute urban planning API calls"""
        try:
            if action == "list_neighborhoods":
                response = httpx.get(f"{self.base_url}/neighborhoods/")
                
            elif action == "get_zoning" and neighborhood:
                response = httpx.get(f"{self.base_url}/neighborhoods/{neighborhood}/zoning")
                
            elif action == "validate_proposal" and neighborhood:
                proposal_data = {
                    "far": kwargs.get("far", 1.0),
                    "height_ft": kwargs.get("height_ft", 40),
                    "lot_area_sf": kwargs.get("lot_area_sf", 2500),
                    "num_units": kwargs.get("num_units", 1)
                }
                response = httpx.post(
                    f"{self.base_url}/neighborhoods/{neighborhood}/validate-proposal",
                    json=proposal_data
                )
            else:
                return {"error": "Invalid action or missing neighborhood"}
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API call failed: {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}


@dataclass
class NeighborhoodProfile:
    """Detailed neighborhood characteristics for contextual analysis"""
    name: str
    zoning: str
    character: str
    main_streets: List[str]
    landmarks: List[str]
    transport: List[str]
    business_ecosystem: str
    demographic_profile: str
    development_pressure: str
    constraints: List[str]

class PlanningParameters(BaseModel):
    """Enhanced structured planning parameters output"""
    neighborhoods: List[str]  # Support multiple neighborhoods
    intent: str  # "housing_development", "transit_improvement", "business_impact", etc.
    priority: str  # "equity", "transit", "environmental", "economic", "balanced"
    focus: str  # "affordability", "accessibility", "business_ecosystem", etc.
    constraints: List[str]
    target_metrics: Dict[str, Any]  # units, affordability %, etc.
    spatial_focus: str  # "near_transit", "waterfront", "cultural_district", etc.
    comparative: bool = False  # True if comparing neighborhoods
    specific_elements: List[str] = []  # bike infrastructure, businesses, etc.
    confidence: float = 0.8  # Interpretation confidence


class InterpreterAgent:
    """
    Agent 1: Advanced natural language interpretation for urban planning queries.
    
    Capabilities:
    - Multi-neighborhood detection and comparison
    - Nuanced intent analysis (not just keywords)
    - Business ecosystem understanding
    - Comparative query processing
    - Context-aware confidence scoring
    """
    
    def __init__(self, api_client: UrbanPlanningAPIClient = None):
        self.api_client = api_client or UrbanPlanningAPIClient()
        self.neighborhood_profiles = self._load_neighborhood_profiles()
        self.comparison_indicators = [
            'vs', 'versus', 'compared to', 'compare', 'difference between',
            'how does', 'impact on', 'affect', 'between', 'and', 'both'
        ]
    
    def _load_neighborhood_profiles(self) -> Dict[str, NeighborhoodProfile]:
        """Load detailed neighborhood profiles for contextual analysis"""
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
    
    def detect_neighborhoods(self, query: str) -> List[str]:
        """Advanced neighborhood detection including variations and landmarks"""
        query_lower = query.lower()
        detected = []
        
        # Comprehensive neighborhood detection patterns
        neighborhood_patterns = {
            "marina": [
                "marina", "marina district", "the marina",
                "palace of fine arts", "chestnut street", "union street", 
                "marina green", "crissy field", "marina harbor", "lombard street",
                "cow hollow"  # Adjacent area often grouped with Marina
            ],
            "mission": [
                "mission", "mission district", "the mission",
                "valencia", "valencia street", "valencia corridor",
                "16th street", "24th street", "mission street",
                "mission dolores", "balmy alley", "mission cultural center",
                "la mission", "16th and mission", "24th and mission"
            ],
            "hayes_valley": [
                "hayes valley", "hayes", "patricia's green",
                "hayes street", "grove street", "fell street",
                "sf jazz", "jazz center", "octavia street"
            ]
        }
        
        for neighborhood, patterns in neighborhood_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                detected.append(neighborhood)
        
        # Default to Hayes Valley if no neighborhood detected
        if not detected:
            detected = ["hayes_valley"]
            
        return detected
    
    def detect_comparative_intent(self, query: str) -> bool:
        """Detect if query is asking for comparison between neighborhoods or scenarios"""
        query_lower = query.lower()
        
        # Direct comparison indicators
        has_comparison_words = any(indicator in query_lower for indicator in self.comparison_indicators)
        
        # Multiple neighborhood detection
        neighborhoods = self.detect_neighborhoods(query)
        multiple_neighborhoods = len(neighborhoods) > 1
        
        # Question patterns that imply comparison
        comparison_patterns = [
            r"how (?:would|does|might) .+ affect .+ in .+ (?:vs|versus|compared to|and) .+",
            r"what (?:is|would be) the (?:difference|impact) .+ between .+ and .+",
            r"compare .+ in .+ (?:with|to|and) .+",
            r".+ impact on .+ in both .+",
            r"how (?:different|similar) .+ in .+ (?:vs|versus|compared to|and) .+"
        ]
        
        has_comparison_pattern = any(re.search(pattern, query_lower) for pattern in comparison_patterns)
        
        return has_comparison_words or multiple_neighborhoods or has_comparison_pattern
    
    def extract_specific_elements(self, query: str) -> List[str]:
        """Extract specific urban planning elements mentioned in the query"""
        query_lower = query.lower()
        elements = []
        
        element_patterns = {
            "bike_infrastructure": ["bike", "bicycle", "cycling", "bike lane", "bike path", "cycling infrastructure"],
            "business_impact": ["business", "businesses", "retail", "restaurant", "shop", "commercial", "economic impact"],
            "transit": ["transit", "bart", "muni", "bus", "transportation", "public transport"],
            "housing": ["housing", "apartments", "units", "affordable housing", "residential"],
            "parks": ["park", "green space", "open space", "recreation", "playground"],
            "streets": ["street", "road", "sidewalk", "crosswalk", "intersection", "traffic"],
            "zoning": ["zoning", "development", "density", "height", "floor area ratio", "far"],
            "equity": ["equity", "displacement", "gentrification", "affordability", "community"]
        }
        
        for element_type, patterns in element_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                elements.append(element_type)
        
        return elements

    def classify_query(self, user_query: str) -> QueryClassification:
        """
        ENHANCED: Dynamic query classification using rule-based intelligence
        This replaces hardcoded scenario detection with intelligent categorization
        """
        return self._rule_based_classify_query(user_query)

    def interpret_query(self, user_query: str) -> PlanningParameters:
        """Convert natural language query to structured planning parameters with enhanced capabilities"""
        return self._rule_based_interpret_query(user_query)
    
    
    def _rule_based_interpret_query(self, user_query: str) -> PlanningParameters:
        """Rule-based interpretation as fallback when AI agent is not available"""
        
        # 1. Detect neighborhoods
        neighborhoods = self.detect_neighborhoods(user_query)
        
        # 2. Detect comparative intent
        is_comparative = self.detect_comparative_intent(user_query)
        
        # 3. Extract specific elements
        elements = self.extract_specific_elements(user_query)
        
        # 4. Determine intent type
        intent_type = self._determine_intent_type(user_query.lower(), elements)
        
        # 5. Determine priority and focus
        priority, focus = self._determine_priority_focus(user_query.lower(), intent_type, elements)
        
        # 6. Get constraints based on neighborhoods
        constraints = []
        for neighborhood in neighborhoods:
            if neighborhood in self.neighborhood_profiles:
                constraints.extend(self.neighborhood_profiles[neighborhood].constraints)
        
        # 7. Calculate confidence
        confidence = self._calculate_confidence(user_query, neighborhoods, elements, is_comparative)
        
        return PlanningParameters(
            neighborhoods=neighborhoods,
            intent=intent_type,
            priority=priority,
            focus=focus,
            constraints=list(set(constraints)),  # Remove duplicates
            target_metrics={},  # Could extract specific numbers if needed
            spatial_focus="general",
            comparative=is_comparative,
            specific_elements=elements,
            confidence=confidence
        )
    
    def _determine_intent_type(self, query_lower: str, elements: List[str]) -> str:
        """Determine intent type using contextual analysis"""
        
        # Business impact analysis
        if "business_impact" in elements and any(word in query_lower for word in ["affect", "impact", "influence"]):
            return "business_impact"
        
        # Transportation/mobility focus
        if "bike_infrastructure" in elements or "transit" in elements:
            return "mobility"
        
        # Housing development
        if "housing" in elements:
            return "housing_development"
        
        # Environmental planning
        if "parks" in elements or any(word in query_lower for word in ["green", "environment", "climate"]):
            return "environmental"
        
        # Equity and community
        if "equity" in elements or any(word in query_lower for word in ["displacement", "community", "gentrification"]):
            return "equity"
        
        # Default to mixed planning
        return "mixed_planning"
    
    def _determine_priority_focus(self, query_lower: str, intent_type: str, elements: List[str]) -> tuple[str, str]:
        """Determine priority and focus with contextual understanding"""
        
        if intent_type == "business_impact":
            return "economic", "business_ecosystem"
        elif intent_type == "mobility":
            return "transit", "accessibility"
        elif intent_type == "housing_development":
            if any(word in query_lower for word in ["affordable", "equity", "displacement"]):
                return "equity", "affordability"
            else:
                return "balanced", "housing_production"
        elif intent_type == "environmental":
            return "environmental", "sustainability"
        elif intent_type == "equity":
            return "equity", "community_stability"
        else:
            return "balanced", "comprehensive"
    
    def _calculate_confidence(self, query: str, neighborhoods: List[str], elements: List[str], is_comparative: bool) -> float:
        """Calculate interpretation confidence based on multiple factors"""
        base_confidence = 0.5
        
        # Query length and specificity
        query_words = len(query.split())
        if query_words > 10:
            base_confidence += 0.1
        
        # Neighborhood specificity
        if len(neighborhoods) == 1:
            base_confidence += 0.15
        elif len(neighborhoods) > 1:
            base_confidence += 0.2  # Comparative queries are more specific
        
        # Element detection
        base_confidence += min(0.2, len(elements) * 0.05)
        
        # Comparative queries get confidence boost for specificity
        if is_comparative:
            base_confidence += 0.15
        
        return min(0.95, base_confidence)
    
    
    def _rule_based_classify_query(self, user_query: str) -> QueryClassification:
        """Rule-based classification fallback"""
        
        query_lower = user_query.lower()
        neighborhoods = self.detect_neighborhoods(query_lower)
        elements = self.extract_specific_elements(query_lower)
        is_comparative = self.detect_comparative_intent(query_lower)
        
        # Determine intent
        if "business" in query_lower and ("affect" in query_lower or "impact" in query_lower):
            intent = QueryIntent.BUSINESS_IMPACT
            domain = QueryDomain.ECONOMICS
        elif any(word in query_lower for word in ["bike", "transit", "transport", "traffic"]):
            intent = QueryIntent.MOBILITY
            domain = QueryDomain.TRANSPORTATION
        elif "housing" in query_lower or "units" in query_lower:
            intent = QueryIntent.HOUSING_DEVELOPMENT
            domain = QueryDomain.HOUSING
        elif any(word in query_lower for word in ["climate", "environment", "green"]):
            intent = QueryIntent.ENVIRONMENTAL
            domain = QueryDomain.ENVIRONMENT
        elif any(word in query_lower for word in ["displacement", "equity", "gentrification"]):
            intent = QueryIntent.EQUITY
            domain = QueryDomain.MIXED
        elif is_comparative:
            intent = QueryIntent.COMPARATIVE
            domain = QueryDomain.MIXED
        else:
            intent = QueryIntent.MIXED_PLANNING
            domain = QueryDomain.MIXED
        
        # Determine query type
        if any(word in query_lower for word in ["what if", "if we", "suppose"]):
            query_type = QueryType.WHAT_IF
        elif any(word in query_lower for word in ["compare", "vs", "versus", "difference"]):
            query_type = QueryType.COMPARISON
        elif any(word in query_lower for word in ["impact", "affect", "effect"]):
            query_type = QueryType.IMPACT_ANALYSIS
        elif any(word in query_lower for word in ["increase", "more", "additional"]):
            query_type = QueryType.INCREASE
        elif any(word in query_lower for word in ["decrease", "less", "reduce"]):
            query_type = QueryType.DECREASE
        else:
            query_type = QueryType.SOLUTION_SEEKING
        
        # Extract parameters (basic number detection)
        import re
        numbers = re.findall(r'\d+(?:\.\d+)?', query_lower)
        parameters = {}
        if numbers:
            if "%" in query_lower:
                parameters["percentage"] = float(numbers[0]) / 100
            elif any(word in query_lower for word in ["units", "housing"]):
                parameters["units"] = int(numbers[0])
            elif "years" in query_lower:
                parameters["timeframe_years"] = int(numbers[0])
        
        # Get constraints
        constraints = []
        for neighborhood in neighborhoods:
            if neighborhood in self.neighborhood_profiles:
                constraints.extend(self.neighborhood_profiles[neighborhood].constraints)
        
        return QueryClassification(
            intent=intent,
            domain=domain,
            sub_domain=f"{domain.value}_{intent.value}",
            query_type=query_type,
            neighborhoods=neighborhoods,
            parameters=parameters,
            confidence=self._calculate_confidence(user_query, neighborhoods, elements, is_comparative),
            comparative=is_comparative,
            specific_elements=elements,
            spatial_focus="general",
            constraints=list(set(constraints))
        )


# Example usage and testing
if __name__ == "__main__":
    # Test the enhanced interpreter
    interpreter = InterpreterAgent()
    
    test_queries = [
        "Add affordable housing near BART in Hayes Valley",
        "How would more bike infrastructure affect businesses in the Marina vs the Mission?",
        "Compare walkability improvements between Marina and Mission",
        "What's the impact of bike lanes on local businesses in both neighborhoods?",
        "Make the Marina more walkable while respecting flood risks",
        "Increase density in Mission without displacing existing residents"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}")
        result = interpreter.interpret_query(query)
        print(f"Neighborhoods: {result.neighborhoods}")
        print(f"Intent: {result.intent}")
        print(f"Priority: {result.priority}")
        print(f"Focus: {result.focus}")
        print(f"Comparative: {result.comparative}")
        print(f"Elements: {result.specific_elements}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Constraints: {result.constraints}")