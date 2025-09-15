from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import time
import asyncio

router = APIRouter()

class AnalysisRequest(BaseModel):
    query: str

class ImpactMetric(BaseModel):
    before: float
    after: float
    unit: str
    confidence: float

class ComprehensiveImpact(BaseModel):
    housing: Dict[str, Any]
    accessibility: Dict[str, Any]
    equity: Dict[str, Any]
    economic: Dict[str, Any]
    environmental: Dict[str, Any]
    overall_assessment: str

class PlanningAlternative(BaseModel):
    title: str
    description: str
    total_units: int
    affordable_units: int
    height_ft: int
    far: float
    amenities: List[str]
    impact: ComprehensiveImpact

class ScenarioComparison(BaseModel):
    alternative_plans: List[PlanningAlternative]
    recommended_plan: str
    recommendation_rationale: str

class AnalysisResult(BaseModel):
    scenario_comparison: ScenarioComparison

def get_neighborhood_specifics(neighborhood: str) -> Dict[str, Any]:
    """Get specific streets, blocks, and details for each SF neighborhood"""
    specifics = {
        "Hayes Valley": {
            "primary_streets": ["Hayes St", "Grove St", "Fell St", "Oak St"],
            "cross_streets": ["Gough St", "Franklin St", "Van Ness Ave", "Laguna St"],
            "blocks_affected": ["400-500 Hayes St", "300-400 Grove St", "Hayes Green"],
            "transit_stations": ["Hayes Valley BART Plaza", "Van Ness BRT"],
            "zoning": "NCT-3 (Neighborhood Commercial Transit)",
            "landmarks": ["Patricia's Green", "Hayes Valley Farm", "Blue Bottle Coffee HQ"]
        },
        "Marina": {
            "primary_streets": ["Chestnut St", "Union St", "Fillmore St", "Lombard St"],
            "cross_streets": ["Divisadero St", "Steiner St", "Pierce St", "Scott St"],
            "blocks_affected": ["2000-2100 Chestnut St", "1900-2000 Union St"],
            "transit_stations": ["Lombard Gate Golden Gate Transit"],
            "zoning": "RH-1 (Residential House, One-Family)",
            "landmarks": ["Marina Green", "Palace of Fine Arts", "Crissy Field"]
        },
        "Mission": {
            "primary_streets": ["Mission St", "Valencia St", "16th St", "24th St"],
            "cross_streets": ["Guerrero St", "Dolores St", "Castro St", "Noe St"],
            "blocks_affected": ["3200-3300 Mission St", "2800-2900 24th St"],
            "transit_stations": ["16th St BART", "24th St BART"],
            "zoning": "NCT-4 (High-density Commercial Transit)",
            "landmarks": ["Dolores Park", "Mission Dolores", "Women's Building"]
        }
    }
    return specifics.get(neighborhood, specifics["Hayes Valley"])

def create_mock_impact(neighborhood: str = "Hayes Valley") -> ComprehensiveImpact:
    """Create mock comprehensive impact data with neighborhood-specific details"""
    specifics = get_neighborhood_specifics(neighborhood)
    
    return ComprehensiveImpact(
        housing={
            "metrics": {
                "units_added": ImpactMetric(before=1200, after=1350, unit=" units", confidence=0.85),
                "affordable_percentage": ImpactMetric(before=12.5, after=20.3, unit="%", confidence=0.78),
                "median_rent": ImpactMetric(before=3200, after=3080, unit="$/month", confidence=0.72)
            },
            "benefits": [
                f"Adds 150 new units along {', '.join(specifics['primary_streets'][:2])}",
                f"Targets {specifics['blocks_affected'][0]} for mixed-income housing",
                f"Enhances walkability to {specifics['landmarks'][0]}"
            ],
            "concerns": [
                f"Increased density on {specifics['blocks_affected'][0]} may strain parking",
                f"Construction impacts on {specifics['cross_streets'][0]} intersection"
            ],
            "mitigation_strategies": [
                f"Implement 18-month construction schedule for {specifics['blocks_affected'][0]}",
                f"Add community benefits fund for {specifics['landmarks'][0]} improvements",
                f"Preserve existing character along {specifics['primary_streets'][1]}"
            ]
        },
        accessibility={
            "metrics": {
                "walk_score": ImpactMetric(before=78, after=84, unit=" points", confidence=0.88),
                "transit_access": ImpactMetric(before=0.4, after=0.6, unit=" miles to BART", confidence=0.92),
                "bike_network": ImpactMetric(before=2.1, after=3.4, unit=" miles protected lanes", confidence=0.81)
            },
            "benefits": [
                f"Direct access to {specifics['transit_stations'][0]}",
                f"New bike lanes connecting {specifics['cross_streets'][0]} to {specifics['cross_streets'][1]}",
                f"Improved pedestrian access to {specifics['landmarks'][1]}"
            ],
            "concerns": [
                f"Peak hour congestion at {specifics['cross_streets'][0]} & {specifics['primary_streets'][0]}",
                f"Loading zone conflicts on {specifics['primary_streets'][1]}"
            ],
            "mitigation_strategies": [
                f"Install smart traffic signals at {specifics['cross_streets'][0]} intersection",
                f"Create dedicated bike parking near {specifics['transit_stations'][0]}",
                f"Add wayfinding from {specifics['primary_streets'][0]} to transit"
            ]
        },
        equity={
            "metrics": {
                "displacement_risk": ImpactMetric(before=0.3, after=0.2, unit=" risk index", confidence=0.69),
                "community_benefits": ImpactMetric(before=15, after=28, unit=" programs", confidence=0.75),
                "local_hiring": ImpactMetric(before=25, after=45, unit="% local workers", confidence=0.82)
            },
            "benefits": [
                f"Protects existing residents on {specifics['blocks_affected'][0]}",
                f"Creates community space near {specifics['landmarks'][0]}",
                f"Prioritizes local hiring for {specifics['primary_streets'][0]} businesses"
            ],
            "concerns": [
                f"Rising rents may affect {specifics['cross_streets'][1]} corridor",
                f"Commercial displacement along {specifics['primary_streets'][1]}"
            ],
            "mitigation_strategies": [
                f"Establish tenant protection fund for {specifics['blocks_affected'][0]} residents",
                f"Create affordable commercial space on {specifics['primary_streets'][0]}",
                f"Partner with {specifics['landmarks'][2]} for local workforce training"
            ]
        },
        economic={
            "metrics": {
                "property_values": ImpactMetric(before=890000, after=920000, unit="$ median", confidence=0.77),
                "local_businesses": ImpactMetric(before=42, after=48, unit=" establishments", confidence=0.71),
                "construction_jobs": ImpactMetric(before=0, after=180, unit=" temporary jobs", confidence=0.89)
            },
            "benefits": ["Job creation", "Increased local spending"],
            "concerns": ["Property tax increases"],
            "mitigation_strategies": ["Property tax relief programs", "Small business support"]
        },
        environmental={
            "metrics": {
                "carbon_footprint": ImpactMetric(before=2.8, after=2.3, unit=" tons CO2/unit/year", confidence=0.84),
                "green_space": ImpactMetric(before=0.2, after=0.4, unit=" acres per 1000 residents", confidence=0.79),
                "stormwater_management": ImpactMetric(before=65, after=85, unit="% runoff captured", confidence=0.73)
            },
            "benefits": ["Reduced carbon emissions", "Improved green infrastructure"],
            "concerns": ["Construction environmental impact"],
            "mitigation_strategies": ["Green building certification", "Tree preservation plan"]
        },
        overall_assessment=f"This development in {neighborhood} provides significant benefits for housing affordability and community equity while maintaining environmental sustainability standards. The project targets {specifics['blocks_affected'][0]} with transit-oriented density near {specifics['transit_stations'][0]}. Key considerations include managing displacement risks on {specifics['cross_streets'][1]} and ensuring community benefits are preserved around {specifics['landmarks'][0]}."
    )

def analyze_query_intent(query: str) -> Dict[str, Any]:
    """Analyze the user's query to understand intent and generate appropriate responses"""
    query_lower = query.lower()
    
    # Extract neighborhood
    if "hayes valley" in query_lower:
        neighborhood = "Hayes Valley"
    elif "marina" in query_lower:
        neighborhood = "Marina"
    elif "mission" in query_lower:
        neighborhood = "Mission"
    else:
        neighborhood = "Hayes Valley"
    
    # Analyze intent keywords
    intent = {
        "focus": "mixed",  # mixed, affordable, luxury, commercial
        "density": "medium",  # low, medium, high
        "priority": "balanced",  # housing, transit, equity, environmental, economic
        "urgency": "standard",  # fast, standard, careful
        "scale": "moderate"  # small, moderate, large
    }
    
    # Housing focus
    if any(word in query_lower for word in ["affordable", "low income", "subsidized"]):
        intent["focus"] = "affordable"
    elif any(word in query_lower for word in ["luxury", "high end", "premium"]):
        intent["focus"] = "luxury"
    elif any(word in query_lower for word in ["commercial", "retail", "office"]):
        intent["focus"] = "commercial"
    
    # Density preferences
    if any(word in query_lower for word in ["high density", "maximize", "many units", "tall"]):
        intent["density"] = "high"
    elif any(word in query_lower for word in ["low density", "preserve character", "small scale"]):
        intent["density"] = "low"
    
    # Priority areas
    if any(word in query_lower for word in ["transit", "bart", "bus", "walkable"]):
        intent["priority"] = "transit"
    elif any(word in query_lower for word in ["displacement", "gentrification", "community"]):
        intent["priority"] = "equity"
    elif any(word in query_lower for word in ["green", "environment", "climate", "sustainable"]):
        intent["priority"] = "environmental"
    elif any(word in query_lower for word in ["jobs", "business", "economic"]):
        intent["priority"] = "economic"
    
    # Urgency
    if any(word in query_lower for word in ["quickly", "fast", "urgent", "immediate"]):
        intent["urgency"] = "fast"
    elif any(word in query_lower for word in ["carefully", "slow", "gradual", "community input"]):
        intent["urgency"] = "careful"
    
    # Scale
    if any(word in query_lower for word in ["200", "300", "many", "lots of", "maximum"]):
        intent["scale"] = "large"
    elif any(word in query_lower for word in ["50", "few", "small", "pilot"]):
        intent["scale"] = "small"
    
    return {
        "neighborhood": neighborhood,
        "intent": intent,
        "query": query
    }

def generate_plan_archetypes(intent: Dict[str, Any], neighborhood: str, query: str) -> List[Dict[str, Any]]:
    """Generate completely different urban planning interventions based on query intent"""
    
    query_lower = query.lower()
    plan_pool = []
    
    # INFRASTRUCTURE & TRANSPORTATION INTERVENTIONS
    if any(word in query_lower for word in ["walkable", "bike", "transit", "traffic", "parking", "street", "road"]):
        plan_pool.extend([
            {
                "title": "Complete Streets Redesign",
                "type": "infrastructure",
                "description": f"Redesign key streets in {neighborhood} to prioritize pedestrians, cyclists, and transit",
                "units_range": (0, 0),  # No housing units
                "affordable_pct": 0,
                "height_range": (0, 0),
                "amenities": ["Protected bike lanes", "Wider sidewalks", "Transit priority signals", "Street trees", "Bike share stations"],
                "focus": "mobility_transformation",
                "intervention_type": "infrastructure"
            },
            {
                "title": "Neighborhood Slow Zone",
                "type": "traffic_calming",
                "description": f"Traffic calming and pedestrian safety improvements throughout {neighborhood}",
                "units_range": (0, 0),
                "affordable_pct": 0,
                "height_range": (0, 0),
                "amenities": ["Speed bumps", "Crosswalk improvements", "Parklets", "Play streets", "Traffic circles"],
                "focus": "safety_first",
                "intervention_type": "policy"
            },
            {
                "title": "Car-Free District Pilot",
                "type": "car_free",
                "description": f"Create car-free zones in {neighborhood} with alternative mobility options",
                "units_range": (0, 0),
                "affordable_pct": 0,
                "height_range": (0, 0),
                "amenities": ["E-bike rentals", "Cargo bike shares", "Micro-transit", "Walking paths", "Public plazas"],
                "focus": "car_reduction",
                "intervention_type": "pilot"
            }
        ])
    
    # PARKS & OPEN SPACE INTERVENTIONS  
    if any(word in query_lower for word in ["park", "green", "space", "environment", "recreation", "playground"]):
        plan_pool.extend([
            {
                "title": "Neighborhood Green Network",
                "type": "park_system",
                "description": f"Create connected network of parks and green spaces throughout {neighborhood}",
                "units_range": (0, 0),
                "affordable_pct": 0,
                "height_range": (0, 0),
                "amenities": ["Community gardens", "Playgrounds", "Dog parks", "Walking trails", "Native landscaping"],
                "focus": "ecological_connectivity",
                "intervention_type": "open_space"
            },
            {
                "title": "Pocket Park Transformation",
                "type": "small_parks",
                "description": f"Convert underutilized lots in {neighborhood} into small neighborhood parks",
                "units_range": (0, 0),
                "affordable_pct": 0,
                "height_range": (0, 0),
                "amenities": ["Seating areas", "Community bulletin boards", "Little free libraries", "Chess tables", "Food gardens"],
                "focus": "neighborhood_activation",
                "intervention_type": "land_use"
            },
            {
                "title": "Climate Resilience Corridor",
                "type": "climate_adaptation",
                "description": f"Green infrastructure in {neighborhood} for stormwater management and urban heat reduction",
                "units_range": (0, 0),
                "affordable_pct": 0,
                "height_range": (0, 0),
                "amenities": ["Rain gardens", "Bioswales", "Urban forest", "Cooling stations", "Flood barriers"],
                "focus": "climate_adaptation",
                "intervention_type": "environmental"
            }
        ])
    
    # BUSINESS & ECONOMIC DEVELOPMENT INTERVENTIONS
    if any(word in query_lower for word in ["business", "economic", "jobs", "commercial", "retail", "restaurant"]):
        plan_pool.extend([
            {
                "title": "Local Business Incubator District",
                "type": "business_development",
                "description": f"Support local entrepreneurship and business development in {neighborhood}",
                "units_range": (0, 0),
                "affordable_pct": 0,
                "height_range": (0, 0),
                "amenities": ["Shared commercial kitchens", "Pop-up retail spaces", "Business mentorship", "Micro-loans", "Co-working hubs"],
                "focus": "economic_empowerment",
                "intervention_type": "economic"
            },
            {
                "title": "Neighborhood Commercial Revitalization",
                "type": "commercial_improvement",
                "description": f"Strengthen existing commercial corridors in {neighborhood} with facade improvements and programming",
                "units_range": (0, 0),
                "affordable_pct": 0,
                "height_range": (0, 0),
                "amenities": ["Storefront improvements", "Street festivals", "Farmers markets", "Outdoor dining", "Art installations"],
                "focus": "commercial_vitality",
                "intervention_type": "revitalization"
            }
        ])
    
    # COMMUNITY & SOCIAL INTERVENTIONS
    if any(word in query_lower for word in ["community", "social", "gathering", "culture", "arts", "seniors", "youth"]):
        plan_pool.extend([
            {
                "title": "Community Hub Network",
                "type": "community_facilities",
                "description": f"Establish community centers and gathering spaces throughout {neighborhood}",
                "units_range": (0, 0),
                "affordable_pct": 0,
                "height_range": (0, 0),
                "amenities": ["Community centers", "Meeting rooms", "Event spaces", "Maker spaces", "Cultural programming"],
                "focus": "social_cohesion",
                "intervention_type": "community"
            },
            {
                "title": "Intergenerational Programming Initiative",
                "type": "social_programs",
                "description": f"Programs and spaces in {neighborhood} that bring different age groups together",
                "units_range": (0, 0),
                "affordable_pct": 0,
                "height_range": (0, 0),
                "amenities": ["Senior-youth mentoring", "Shared gardens", "Skill exchanges", "Story circles", "Game rooms"],
                "focus": "age_integration",
                "intervention_type": "programming"
            }
        ])
    
    # POLICY & REGULATORY INTERVENTIONS
    if any(word in query_lower for word in ["zoning", "policy", "regulation", "height", "density", "permit"]):
        plan_pool.extend([
            {
                "title": "Zoning Reform Initiative",
                "type": "policy_change",
                "description": f"Update zoning regulations in {neighborhood} to enable more flexible and equitable development",
                "units_range": (0, 0),
                "affordable_pct": 0,
                "height_range": (0, 0),
                "amenities": ["Accessory dwelling unit allowances", "Mixed-use permissions", "Reduced parking requirements", "Height bonuses for affordable housing"],
                "focus": "regulatory_flexibility",
                "intervention_type": "policy"
            },
            {
                "title": "Community Land Trust Establishment",
                "type": "land_policy",
                "description": f"Create community land trust in {neighborhood} to preserve long-term affordability",
                "units_range": (0, 0),
                "affordable_pct": 0,
                "height_range": (0, 0),
                "amenities": ["Land acquisition fund", "Resident ownership programs", "Anti-speculation measures", "Community governance"],
                "focus": "anti_displacement",
                "intervention_type": "policy"
            }
        ])
    
    # ONLY ADD HOUSING IF EXPLICITLY REQUESTED
    if any(word in query_lower for word in ["housing", "apartment", "units", "homes", "residential", "live", "rent"]):
        # AFFORDABLE/EQUITY FOCUSED PLANS
        if intent["focus"] == "affordable" or intent["priority"] == "equity":
            plan_pool.extend([
                {
                    "title": "Social Housing Cooperative",
                    "type": "cooperative",
                    "description": f"Community-owned affordable housing in {neighborhood} with resident control and permanently affordable units",
                    "units_range": (80, 150),
                    "affordable_pct": 0.8,
                    "height_range": (35, 50),
                    "amenities": ["Community kitchen", "Childcare co-op", "Tool library", "Meeting halls", "Urban farm"],
                    "focus": "community_ownership",
                    "intervention_type": "housing"
                },
                {
                    "title": "Micro-Unit Affordable Complex",
                    "type": "micro_units",
                    "description": f"High-density micro-units in {neighborhood} maximizing affordable housing count",
                    "units_range": (200, 400),
                    "affordable_pct": 0.75,
                    "height_range": (55, 75),
                    "amenities": ["Shared kitchens", "Co-working lounges", "Bike workshop", "Laundromat"],
                    "focus": "density_optimization",
                    "intervention_type": "housing"
                }
            ])
        
        # LUXURY/HIGH-END PLANS
        if intent["focus"] == "luxury":
            plan_pool.extend([
                {
                    "title": "Boutique Luxury Condominiums",
                    "type": "luxury_condos",
                    "description": f"Premium residential development in {neighborhood} with high-end finishes and services",
                    "units_range": (40, 80),
                    "affordable_pct": 0.12,
                    "height_range": (45, 65),
                    "amenities": ["Concierge", "Private gym", "Wine cellar", "Rooftop deck", "Valet parking"],
                    "focus": "luxury_services",
                    "intervention_type": "housing"
                }
            ])
        
        # LOW-DENSITY/CHARACTER PRESERVATION PLANS
        if intent["density"] == "low":
            plan_pool.extend([
                {
                    "title": "Townhouse Village",
                    "type": "townhouses",
                    "description": f"Low-rise townhouse development in {neighborhood} preserving neighborhood scale",
                    "units_range": (30, 80),
                    "affordable_pct": 0.3,
                    "height_range": (25, 40),
                    "amenities": ["Private gardens", "Shared courtyards", "Neighborhood watch", "Block parties"],
                    "focus": "human_scale",
                    "intervention_type": "housing"
                }
            ])
        
        # GENERAL HOUSING OPTIONS
        plan_pool.extend([
            {
                "title": "Adaptive Mixed-Use Development",
                "type": "adaptive_mixed",
                "description": f"Flexible mixed-use development in {neighborhood} designed to evolve with community needs",
                "units_range": (100, 180),
                "affordable_pct": 0.25,
                "height_range": (45, 65),
                "amenities": ["Flexible community space", "Pop-up retail", "Maker space", "Event hall"],
                "focus": "adaptability",
                "intervention_type": "housing"
            }
        ])
    
    return plan_pool


def generate_dynamic_alternatives(analysis: Dict[str, Any]) -> List[PlanningAlternative]:
                "affordable_pct": 0.8,
                "height_range": (35, 50),
                "amenities": ["Community kitchen", "Childcare co-op", "Tool library", "Meeting halls", "Urban farm"],
                "focus": "community_ownership"
            },
            {
                "title": "Inclusionary Mixed-Income Village",
                "type": "mixed_income",
                "description": f"Integrated affordable and market-rate housing in {neighborhood} with shared community facilities",
                "units_range": (120, 200),
                "affordable_pct": 0.5,
                "height_range": (40, 60),
                "amenities": ["Community center", "Shared workspace", "Playground", "Community gardens"],
                "focus": "integration"
            },
            {
                "title": "Micro-Unit Affordable Complex",
                "type": "micro_units",
                "description": f"High-density micro-units in {neighborhood} maximizing affordable housing count",
                "units_range": (200, 400),
                "affordable_pct": 0.75,
                "height_range": (55, 75),
                "amenities": ["Shared kitchens", "Co-working lounges", "Bike workshop", "Laundromat"],
                "focus": "density_optimization"
            }
        ])
    
    # LUXURY/HIGH-END PLANS
    if intent["focus"] == "luxury":
        plan_pool.extend([
            {
                "title": "Boutique Luxury Condominiums",
                "type": "luxury_condos",
                "description": f"Premium residential development in {neighborhood} with high-end finishes and services",
                "units_range": (40, 80),
                "affordable_pct": 0.12,
                "height_range": (45, 65),
                "amenities": ["Concierge", "Private gym", "Wine cellar", "Rooftop deck", "Valet parking"],
                "focus": "luxury_services"
            },
            {
                "title": "Mixed-Use Luxury Tower",
                "type": "luxury_tower",
                "description": f"High-rise luxury development in {neighborhood} with integrated retail and dining",
                "units_range": (100, 180),
                "affordable_pct": 0.15,
                "height_range": (65, 85),
                "amenities": ["Restaurant", "Retail spaces", "Spa", "Business center", "Sky lounge"],
                "focus": "vertical_integration"
            }
        ])
    
    # TRANSIT/MOBILITY FOCUSED PLANS
    if intent["priority"] == "transit":
        plan_pool.extend([
            {
                "title": "Transit-Oriented Village",
                "type": "tod",
                "description": f"Car-free development in {neighborhood} designed around public transit access",
                "units_range": (150, 280),
                "affordable_pct": 0.3,
                "height_range": (50, 70),
                "amenities": ["Bike share station", "Transit pass office", "Car-share hub", "E-scooter parking"],
                "focus": "mobility_hub"
            },
            {
                "title": "Mixed-Use Transit Plaza",
                "type": "transit_plaza",
                "description": f"Development in {neighborhood} integrated with improved transit infrastructure",
                "units_range": (180, 320),
                "affordable_pct": 0.25,
                "height_range": (55, 80),
                "amenities": ["Transit center", "Bus rapid transit", "Retail concourse", "Public plaza"],
                "focus": "transit_integration"
            }
        ])
    
    # COMMERCIAL/MIXED-USE PLANS
    if intent["focus"] == "commercial":
        plan_pool.extend([
            {
                "title": "Live-Work Innovation District",
                "type": "live_work",
                "description": f"Mixed residential and workspace development in {neighborhood} for creative professionals",
                "units_range": (100, 200),
                "affordable_pct": 0.2,
                "height_range": (40, 60),
                "amenities": ["Maker spaces", "Art studios", "Co-working", "Gallery space", "Coffee roastery"],
                "focus": "creative_economy"
            },
            {
                "title": "Neighborhood Commercial Hub",
                "type": "commercial_hub",
                "description": f"Mixed-use development in {neighborhood} anchored by local businesses and services",
                "units_range": (80, 160),
                "affordable_pct": 0.25,
                "height_range": (35, 55),
                "amenities": ["Local retail", "Farmers market", "Community bank", "Medical clinic"],
                "focus": "local_services"
            }
        ])
    
    # ENVIRONMENTAL/SUSTAINABILITY FOCUSED PLANS
    if intent["priority"] == "environmental":
        plan_pool.extend([
            {
                "title": "Net-Zero Eco-Village",
                "type": "eco_village",
                "description": f"Carbon-neutral development in {neighborhood} with advanced sustainability features",
                "units_range": (90, 160),
                "affordable_pct": 0.35,
                "height_range": (35, 50),
                "amenities": ["Solar gardens", "Rainwater harvesting", "Composting center", "Native plant nursery"],
                "focus": "environmental_innovation"
            },
            {
                "title": "Climate-Resilient Housing",
                "type": "climate_resilient",
                "description": f"Flood and earthquake resistant housing in {neighborhood} designed for climate adaptation",
                "units_range": (120, 220),
                "affordable_pct": 0.4,
                "height_range": (40, 65),
                "amenities": ["Emergency shelter", "Community resilience center", "Food storage", "Backup power"],
                "focus": "disaster_preparedness"
            }
        ])
    
    # LOW-DENSITY/CHARACTER PRESERVATION PLANS
    if intent["density"] == "low":
        plan_pool.extend([
            {
                "title": "Townhouse Village",
                "type": "townhouses",
                "description": f"Low-rise townhouse development in {neighborhood} preserving neighborhood scale",
                "units_range": (30, 80),
                "affordable_pct": 0.3,
                "height_range": (25, 40),
                "amenities": ["Private gardens", "Shared courtyards", "Neighborhood watch", "Block parties"],
                "focus": "human_scale"
            },
            {
                "title": "Cottage Court Community",
                "type": "cottage_court",
                "description": f"Small-scale cottage development in {neighborhood} with shared common spaces",
                "units_range": (20, 60),
                "affordable_pct": 0.4,
                "height_range": (20, 35),
                "amenities": ["Community garden", "Shared kitchen", "Library nook", "Kids playground"],
                "focus": "intimate_community"
            }
        ])
    
    # DEFAULT/GENERAL PLANS (always available)
    plan_pool.extend([
        {
            "title": "Adaptive Mixed-Use Development",
            "type": "adaptive_mixed",
            "description": f"Flexible mixed-use development in {neighborhood} designed to evolve with community needs",
            "units_range": (100, 180),
            "affordable_pct": 0.25,
            "height_range": (45, 65),
            "amenities": ["Flexible community space", "Pop-up retail", "Maker space", "Event hall"],
            "focus": "adaptability"
        },
        {
            "title": "Infill Housing Cluster",
            "type": "infill",
            "description": f"Strategic infill development in {neighborhood} filling gaps in existing urban fabric",
            "units_range": (60, 120),
            "affordable_pct": 0.35,
            "height_range": (35, 55),
            "amenities": ["Pocket parks", "Neighborhood retail", "Community room", "Bike storage"],
            "focus": "urban_fabric"
        },
        {
            "title": "Multi-Generational Housing",
            "type": "multi_gen",
            "description": f"Housing in {neighborhood} designed for diverse age groups and family structures",
            "units_range": (80, 160),
            "affordable_pct": 0.4,
            "height_range": (40, 60),
            "amenities": ["Senior center", "Childcare", "Intergenerational programs", "Accessible design"],
            "focus": "demographic_diversity"
        }
    ])
    
    return plan_pool

def generate_dynamic_alternatives(analysis: Dict[str, Any]) -> List[PlanningAlternative]:
    """Generate fundamentally different planning alternatives based on query analysis"""
    neighborhood = analysis["neighborhood"]
    intent = analysis["intent"]
    
    # Get pool of relevant plan archetypes
    plan_pool = generate_plan_archetypes(intent, neighborhood)
    
    # Select 3 most relevant plans based on intent
    import random
    random.seed(hash(analysis["query"]))  # Consistent randomness based on query
    
    # Filter and rank plans by relevance
    scored_plans = []
    for plan in plan_pool:
        score = 0
        
        # Score based on intent matching
        if intent["focus"] == "affordable" and plan["affordable_pct"] > 0.3:
            score += 3
        if intent["focus"] == "luxury" and plan["type"] in ["luxury_condos", "luxury_tower"]:
            score += 3
        if intent["focus"] == "commercial" and plan["type"] in ["live_work", "commercial_hub"]:
            score += 3
        if intent["priority"] == "transit" and plan["type"] in ["tod", "transit_plaza"]:
            score += 3
        if intent["priority"] == "environmental" and plan["type"] in ["eco_village", "climate_resilient"]:
            score += 3
        if intent["priority"] == "equity" and plan["affordable_pct"] > 0.4:
            score += 2
        if intent["density"] == "low" and plan["type"] in ["townhouses", "cottage_court"]:
            score += 3
        if intent["density"] == "high" and plan["units_range"][1] > 200:
            score += 2
        
        # Add small random component for variety
        score += random.uniform(0, 1)
        
        scored_plans.append((score, plan))
    
    # Sort by score and take top 3
    scored_plans.sort(key=lambda x: x[0], reverse=True)
    selected_plans = [plan for score, plan in scored_plans[:3]]
    
    # Convert to PlanningAlternative objects
    alternatives = []
    for i, plan_template in enumerate(selected_plans):
        # Add variety to units within the range
        min_units, max_units = plan_template["units_range"]
        units = min_units + int((max_units - min_units) * (0.3 + i * 0.35))
        
        min_height, max_height = plan_template["height_range"]
        height = min_height + int((max_height - min_height) * (0.3 + i * 0.35))
        
        affordable_units = int(units * plan_template["affordable_pct"])
        
        # Calculate FAR based on units and typical unit size
        typical_unit_sf = 800
        lot_area_sf = 15000  # Typical lot area
        far = (units * typical_unit_sf) / lot_area_sf
        
        alternatives.append(PlanningAlternative(
            title=plan_template["title"],
            description=plan_template["description"],
            total_units=units,
            affordable_units=affordable_units,
            height_ft=height,
            far=round(far, 1),
            amenities=plan_template["amenities"],
            impact=create_mock_impact(neighborhood)
        ))
    
    return alternatives

@router.post("/analyze")
async def analyze_query(request: AnalysisRequest) -> AnalysisResult:
    """Analyze urban planning query and return comprehensive impact assessment"""
    
    # Add artificial delay to simulate processing
    await asyncio.sleep(2)
    
    # Analyze the query to understand user intent
    analysis = analyze_query_intent(request.query)
    neighborhood = analysis["neighborhood"]
    intent = analysis["intent"]
    
    # Generate dynamic alternatives based on query analysis
    alternatives = generate_dynamic_alternatives(analysis)
    
    # Determine recommended plan based on intent
    if intent["priority"] == "equity":
        recommended = alternatives[0].title  # Most community-focused
    elif intent["priority"] == "transit" or intent["density"] == "high":
        recommended = alternatives[2].title  # Highest density/transit focus
    else:
        recommended = alternatives[1].title  # Balanced approach
    
    # Generate dynamic recommendation rationale
    rationale = f"Based on your query about {request.query.lower()}, this option best addresses "
    if intent["focus"] == "affordable":
        rationale += f"affordable housing priorities in {neighborhood} while maintaining community character."
    elif intent["priority"] == "transit":
        rationale += f"transit connectivity and walkability improvements in {neighborhood}."
    elif intent["priority"] == "equity":
        rationale += f"community equity and displacement prevention in {neighborhood}."
    elif intent["density"] == "high":
        rationale += f"maximizing housing production in {neighborhood} near existing transit infrastructure."
    else:
        rationale += f"balanced growth that serves multiple community needs in {neighborhood}."
    
    scenario = ScenarioComparison(
        alternative_plans=alternatives,
        recommended_plan=recommended,
        recommendation_rationale=rationale
    )
    
    return AnalysisResult(scenario_comparison=scenario)