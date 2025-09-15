import asyncio
import random
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(tags=["analysis"])

class PlanAnalysisRequest(BaseModel):
    query: str

class PlanningAlternative(BaseModel):
    title: str
    type: str
    description: str
    units: int
    affordable_percentage: int
    height_ft: int
    amenities: List[str]

class ImpactMetric(BaseModel):
    before: float
    after: float
    unit: str
    confidence: float

class CategoryImpact(BaseModel):
    metrics: Dict[str, ImpactMetric]
    benefits: List[str]
    concerns: List[str]
    mitigation_strategies: List[str]

class ComprehensiveImpact(BaseModel):
    housing: CategoryImpact
    accessibility: CategoryImpact
    equity: CategoryImpact
    economic: CategoryImpact
    environmental: CategoryImpact
    overall_assessment: str

class AnalysisResponse(BaseModel):
    query: str
    neighborhood: str
    alternatives: List[PlanningAlternative]
    recommended: str
    rationale: str
    impact: ComprehensiveImpact

# SF-specific street and landmark data
SF_STREET_DATA = {
    "hayes_valley": {
        "main_streets": ["Hayes Street", "Grove Street", "Fell Street", "Oak Street"],
        "landmarks": ["Patricia's Green", "Hayes Valley Playground", "Proxy SF", "SF Jazz Center"],
        "transport": ["Van Ness-UNM BART", "Hayes-Fillmore Muni"],
        "zoning": "NCT-3"
    },
    "marina": {
        "main_streets": ["Chestnut Street", "Union Street", "Lombard Street", "Marina Boulevard"],
        "landmarks": ["Marina Green", "Palace of Fine Arts", "Crissy Field", "Marina Harbor"],
        "transport": ["Golden Gate Transit", "Muni Lines 30, 43"],
        "zoning": "RH-1"
    },
    "mission": {
        "main_streets": ["Mission Street", "Valencia Street", "16th Street", "24th Street"],
        "landmarks": ["Mission Dolores", "Valencia Corridor", "Mission Cultural Center", "Balmy Alley"],
        "transport": ["16th St Mission BART", "24th St Mission BART"],
        "zoning": "NCT-3"
    }
}

def analyze_query_intent(query: str) -> Dict[str, Any]:
    """Analyze user query to understand intent and extract parameters."""
    query_lower = query.lower()
    
    # Neighborhood detection
    neighborhood = "hayes_valley"  # default
    if any(word in query_lower for word in ["marina", "palace of fine arts", "chestnut street"]):
        neighborhood = "marina"
    elif any(word in query_lower for word in ["mission", "valencia", "16th street", "24th street"]):
        neighborhood = "mission"
    elif any(word in query_lower for word in ["hayes", "patricia", "grove street", "fell street"]):
        neighborhood = "hayes_valley"
    
    # Intent analysis
    intent = {
        "type": "mixed",
        "priority": "balanced",
        "density": "medium", 
        "focus": "community"
    }
    
    # Housing intent
    if any(word in query_lower for word in ["affordable", "low-income", "community housing"]):
        intent["type"] = "housing"
        intent["priority"] = "equity"
        intent["focus"] = "affordability"
    
    # Environmental intent  
    elif any(word in query_lower for word in ["park", "green", "climate", "sustainability", "environment"]):
        intent["type"] = "environmental"
        intent["priority"] = "environmental"
        intent["focus"] = "green_space"
    
    # Transit intent
    elif any(word in query_lower for word in ["transit", "bart", "muni", "transport", "walkable"]):
        intent["type"] = "transit"
        intent["priority"] = "transit"
        intent["focus"] = "mobility"
    
    # Business/Economic intent
    elif any(word in query_lower for word in ["business", "commercial", "retail", "jobs", "economic"]):
        intent["type"] = "economic"
        intent["priority"] = "economic"
        intent["focus"] = "commercial"
    
    # Density analysis
    if any(word in query_lower for word in ["high-rise", "dense", "maximum", "lots of units"]):
        intent["density"] = "high"
    elif any(word in query_lower for word in ["low-rise", "small", "townhouse", "preserve character"]):
        intent["density"] = "low"
    
    return {
        "query": query,
        "neighborhood": neighborhood,
        "intent": intent
    }

def generate_plan_archetypes(intent: Dict[str, Any], neighborhood: str, query: str) -> List[Dict[str, Any]]:
    """Generate diverse urban planning intervention options beyond just housing."""
    plan_pool = []
    query_lower = query.lower()
    
    # INFRASTRUCTURE & TRANSPORTATION INTERVENTIONS
    if any(word in query_lower for word in ["street", "transportation", "bike", "walk", "transit", "infrastructure"]):
        plan_pool.extend([
            {
                "title": "Complete Streets Transformation",
                "type": "street_redesign",
                "description": f"Transform key streets in {neighborhood} with protected bike lanes, wider sidewalks, and green infrastructure",
                "units_range": (0, 0),  # No housing units
                "affordable_pct": 0,
                "height_range": (0, 0),
                "amenities": ["Protected bike lanes", "Bus rapid transit", "Parklets", "Street trees", "Improved crossings"],
                "focus": "mobility_safety",
                "intervention_type": "infrastructure"
            },
            {
                "title": "Car-Free District",
                "type": "pedestrian_zone",
                "description": f"Create a car-free zone in central {neighborhood} prioritizing pedestrians, cyclists, and public space",
                "units_range": (0, 0),
                "affordable_pct": 0,
                "height_range": (0, 0),
                "amenities": ["Pedestrian plazas", "Outdoor dining", "Pop-up markets", "Street performance spaces"],
                "focus": "pedestrian_priority",
                "intervention_type": "infrastructure"
            }
        ])
    
    # PARKS & OPEN SPACE INTERVENTIONS
    if any(word in query_lower for word in ["park", "green", "open space", "recreation", "playground"]):
        plan_pool.extend([
            {
                "title": "Green Network Expansion",
                "type": "park_system",
                "description": f"Create connected green spaces throughout {neighborhood} with new parks and improved existing ones",
                "units_range": (0, 0),
                "affordable_pct": 0,
                "height_range": (0, 0),
                "amenities": ["New pocket parks", "Community gardens", "Children's play areas", "Dog runs", "Outdoor fitness"],
                "focus": "green_connectivity",
                "intervention_type": "environmental"
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
                "amenities": ["Facade improvements", "Street activation", "Small business support", "Public art", "Outdoor seating"],
                "focus": "commercial_vitality",
                "intervention_type": "economic"
            }
        ])
    
    # COMMUNITY & SOCIAL INTERVENTIONS
    if any(word in query_lower for word in ["community", "social", "services", "health", "education", "seniors"]):
        plan_pool.extend([
            {
                "title": "Community Services Hub",
                "type": "social_infrastructure",
                "description": f"Centralized community services and programming in {neighborhood}",
                "units_range": (0, 0),
                "affordable_pct": 0,
                "height_range": (0, 0),
                "amenities": ["Community health clinic", "Senior center", "Childcare facility", "Job training center", "Food assistance"],
                "focus": "social_support",
                "intervention_type": "community"
            },
            {
                "title": "Cultural Arts District",
                "type": "cultural_preservation",
                "description": f"Preserve and enhance cultural identity in {neighborhood} through arts and programming",
                "units_range": (0, 0),
                "affordable_pct": 0,
                "height_range": (0, 0),
                "amenities": ["Artist studios", "Performance venues", "Cultural center", "Public murals", "Community festivals"],
                "focus": "cultural_identity",
                "intervention_type": "community"
            }
        ])
    
    # POLICY & REGULATORY INTERVENTIONS
    if any(word in query_lower for word in ["zoning", "policy", "regulation", "affordable", "displacement", "gentrification"]):
        plan_pool.extend([
            {
                "title": "Anti-Displacement Policy Package",
                "type": "policy_reform",
                "description": f"Comprehensive policies to prevent displacement and preserve community in {neighborhood}",
                "units_range": (0, 0),
                "affordable_pct": 0,
                "height_range": (0, 0),
                "amenities": ["Tenant protections", "Community ownership programs", "Affordable housing preservation", "Commercial rent control"],
                "focus": "community_preservation",
                "intervention_type": "policy"
            },
            {
                "title": "Inclusionary Zoning Reform",
                "type": "zoning_update",
                "description": f"Update zoning in {neighborhood} to require more affordable housing and community benefits",
                "units_range": (0, 0),
                "affordable_pct": 0,
                "height_range": (0, 0),
                "amenities": ["Increased affordability requirements", "Community benefit districts", "Development impact fees", "Height bonuses for public good"],
                "focus": "regulatory_equity",
                "intervention_type": "policy"
            }
        ])
    
    # HOUSING INTERVENTIONS (only if specifically requested)
    if any(word in query_lower for word in ["housing", "apartments", "units", "homes", "residential"]):
        plan_pool.extend([
            {
                "title": "Community Land Trust Housing",
                "type": "community_ownership",
                "description": f"Permanently affordable community-controlled housing development in {neighborhood}",
                "units_range": (80, 150),
                "affordable_pct": 0.8,
                "height_range": (35, 50),
                "amenities": ["Community kitchen", "Childcare co-op", "Tool library", "Meeting halls", "Urban farm"],
                "focus": "community_ownership",
                "intervention_type": "housing"
            },
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
    """Generate planning alternatives based on query analysis with diverse intervention types."""
    query = analysis.get("query", "")
    neighborhood = analysis["neighborhood"]
    intent = analysis["intent"]
    
    # Generate plans using the new diverse intervention system
    plan_pool = generate_plan_archetypes(intent, neighborhood, query)
    
    # Select best 3 plans based on intent and scoring
    scored_plans = []
    for plan in plan_pool:
        score = 0
        
        # Score based on intervention alignment
        if plan["intervention_type"] == "housing" and any(word in query.lower() for word in ["housing", "apartments", "units", "homes"]):
            score += 10
        elif plan["intervention_type"] == "infrastructure" and any(word in query.lower() for word in ["street", "transit", "bike", "walk", "transport"]):
            score += 10  
        elif plan["intervention_type"] == "environmental" and any(word in query.lower() for word in ["park", "green", "climate", "environment"]):
            score += 10
        elif plan["intervention_type"] == "economic" and any(word in query.lower() for word in ["business", "jobs", "economic", "commercial"]):
            score += 10
        elif plan["intervention_type"] == "community" and any(word in query.lower() for word in ["community", "social", "services"]):
            score += 10
        elif plan["intervention_type"] == "policy" and any(word in query.lower() for word in ["zoning", "policy", "regulation"]):
            score += 10
        
        # Score based on intent priorities
        if intent["priority"] == "equity" and plan.get("affordable_pct", 0) > 0.3:
            score += 5
        if intent["priority"] == "environmental" and plan["intervention_type"] == "environmental":
            score += 8
        if intent["priority"] == "transit" and "transit" in plan.get("focus", ""):
            score += 6
        if intent["density"] == "high" and plan.get("units_range", (0,0))[1] > 200:
            score += 4
        
        scored_plans.append((score, plan))
    
    # Sort by score and select top 3
    scored_plans.sort(key=lambda x: x[0], reverse=True)
    top_plans = [plan for _, plan in scored_plans[:3]]
    
    # If we don't have enough diverse plans, add some defaults
    if len(top_plans) < 3:
        defaults = [
            {
                "title": "Balanced Mixed-Use Development",
                "type": "mixed_use",
                "description": f"Moderate density mixed-use development in {neighborhood} with community amenities",
                "units_range": (120, 200),
                "affordable_pct": 0.25,
                "height_range": (40, 60),
                "amenities": ["Community space", "Ground floor retail", "Childcare", "Bike parking"],
                "intervention_type": "housing"
            },
            {
                "title": "Green Infrastructure Improvements",
                "type": "green_infrastructure",
                "description": f"Environmental improvements throughout {neighborhood}",
                "units_range": (0, 0),
                "affordable_pct": 0,
                "height_range": (0, 0),
                "amenities": ["Street trees", "Rain gardens", "Green roofs", "Solar installations"],
                "intervention_type": "environmental"
            }
        ]
        top_plans.extend(defaults[:3-len(top_plans)])
    
    # Convert to PlanningAlternative format
    alternatives = []
    for i, plan in enumerate(top_plans):
        alt = PlanningAlternative(
            title=plan["title"],
            type=plan["type"],
            description=plan["description"],
            units=plan.get("units_range", (0,0))[1] if plan.get("units_range") else 0,
            affordable_percentage=int(plan.get("affordable_pct", 0) * 100),
            height_ft=plan.get("height_range", (0,0))[1] if plan.get("height_range") else 0,
            amenities=plan.get("amenities", [])
        )
        alternatives.append(alt)
    
    return alternatives

def generate_comprehensive_impact(neighborhood: str, plan: PlanningAlternative) -> ComprehensiveImpact:
    """Generate detailed impact analysis with SF-specific street references."""
    
    # Get neighborhood-specific context
    neighborhood_data = SF_STREET_DATA.get(neighborhood, SF_STREET_DATA["hayes_valley"])
    main_streets = neighborhood_data["main_streets"]
    landmarks = neighborhood_data["landmarks"]
    
    # Housing Impact
    housing_metrics = {
        "total_units": ImpactMetric(before=1200.0, after=1200.0 + plan.units, unit="", confidence=0.9),
        "affordable_units": ImpactMetric(
            before=300.0, 
            after=300.0 + (plan.units * plan.affordable_percentage / 100), 
            unit="", 
            confidence=0.85
        )
    }
    
    housing_benefits = [
        f"Adds {plan.units} new housing units near {landmarks[0]}" if plan.units > 0 else f"Preserves existing housing character around {main_streets[0]}",
        f"Increases affordable housing stock by {plan.affordable_percentage}% along {main_streets[1]}" if plan.affordable_percentage > 20 else f"Maintains existing affordability levels"
    ]
    
    housing_concerns = [
        f"Potential displacement pressure on {main_streets[2]} corridor" if plan.units > 150 else f"Limited new housing supply relative to demand",
        f"Construction impacts on {neighborhood_data['transport'][0]} access" if plan.units > 0 else f"No direct housing production"
    ]
    
    # Accessibility Impact  
    accessibility_metrics = {
        "walk_score": ImpactMetric(before=78.0, after=min(100.0, 78.0 + (plan.units * 0.02)), unit="/100", confidence=0.8),
        "transit_access": ImpactMetric(before=0.65, after=min(1.0, 0.65 + (plan.units * 0.0008)), unit="ratio", confidence=0.75)
    }
    
    accessibility_benefits = [
        f"Improved pedestrian connections between {landmarks[1]} and {main_streets[0]}",
        f"Enhanced access to {neighborhood_data['transport'][0]} station" if len(neighborhood_data['transport']) > 0 else "Better local transit connections"
    ]
    
    # Equity Impact
    equity_metrics = {
        "affordability_ratio": ImpactMetric(before=0.25, after=0.25 + (plan.affordable_percentage * 0.003), unit="ratio", confidence=0.8),
        "displacement_risk": ImpactMetric(before=0.6, after=max(0.1, 0.6 - (plan.affordable_percentage * 0.005)), unit="risk", confidence=0.7)
    }
    
    equity_benefits = [
        f"Increased affordable housing options near {landmarks[2]}" if plan.affordable_percentage > 15 else f"Maintains existing community fabric",
        f"Community ownership opportunities along {main_streets[3]}" if "community" in plan.type.lower() else f"Standard affordable housing requirements"
    ]
    
    # Economic Impact
    economic_metrics = {
        "property_values": ImpactMetric(before=850000.0, after=850000.0 + (plan.units * 1200), unit="$", confidence=0.7),
        "local_jobs": ImpactMetric(before=450.0, after=450.0 + max(5, plan.units * 0.3), unit="", confidence=0.65)
    }
    
    economic_benefits = [
        f"Construction jobs during development phase near {main_streets[0]}",
        f"Increased foot traffic for businesses along {main_streets[1]} corridor"
    ]
    
    # Environmental Impact
    environmental_metrics = {
        "carbon_reduction": ImpactMetric(before=0.0, after=plan.units * 0.8 if plan.units > 0 else 150.0, unit="tons CO2/yr", confidence=0.6),
        "green_space": ImpactMetric(before=0.15, after=0.15 + (0.02 if "green" in plan.description.lower() else 0.005), unit="ratio", confidence=0.7)
    }
    
    environmental_benefits = [
        f"Increased density reduces sprawl pressure on {neighborhood} periphery" if plan.units > 100 else f"Preserves existing neighborhood character",
        f"Green building features and sustainable design near {landmarks[0]}"
    ]
    
    return ComprehensiveImpact(
        housing=CategoryImpact(
            metrics=housing_metrics,
            benefits=housing_benefits,
            concerns=housing_concerns,
            mitigation_strategies=[
                f"Phased development timeline to minimize {main_streets[0]} disruption",
                f"Community benefits agreement with {neighborhood} residents"
            ]
        ),
        accessibility=CategoryImpact(
            metrics=accessibility_metrics,
            benefits=accessibility_benefits,
            concerns=[f"Increased pedestrian traffic on {main_streets[1]}", "Potential parking pressure"],
            mitigation_strategies=[f"Improved crosswalk safety at {main_streets[2]} intersections", "Transportation demand management"]
        ),
        equity=CategoryImpact(
            metrics=equity_metrics,
            benefits=equity_benefits,
            concerns=[f"Gentrification pressure in {neighborhood}", "Cultural displacement risk"],
            mitigation_strategies=[f"Community land trust options near {landmarks[1]}", "Local hiring requirements"]
        ),
        economic=CategoryImpact(
            metrics=economic_metrics,
            benefits=economic_benefits,
            concerns=["Construction cost escalation", f"Small business displacement on {main_streets[2]}"],
            mitigation_strategies=["Local business support fund", f"Temporary relocation assistance for {main_streets[3]} merchants"]
        ),
        environmental=CategoryImpact(
            metrics=environmental_metrics,
            benefits=environmental_benefits,
            concerns=["Construction period air quality", f"Stormwater management around {landmarks[3]}"],
            mitigation_strategies=[f"Green infrastructure integration along {main_streets[0]}", "LEED certification requirements"]
        ),
        overall_assessment=f"This {plan.type} development in {neighborhood} represents a {'moderate' if plan.units < 200 else 'significant'} intervention that balances community needs with growth pressures. Key considerations include coordination with {neighborhood_data['transport'][0]} improvements and {landmarks[0]} accessibility."
    )

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_urban_plan(request: PlanAnalysisRequest):
    """Generate comprehensive urban planning analysis with dynamic alternatives based on query intent."""
    
    # Simulate analysis time
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
        recommended = alternatives[2].title if len(alternatives) > 2 else alternatives[-1].title  # Highest density/transit focus
    else:
        recommended = alternatives[1].title if len(alternatives) > 1 else alternatives[0].title  # Balanced approach
    
    # Generate dynamic recommendation rationale
    rationale = f"Based on your query about {request.query.lower()}, this option best addresses "
    if intent["priority"] == "equity":
        rationale += "community needs and affordability concerns while preserving neighborhood character."
    elif intent["priority"] == "environmental":
        rationale += "sustainability goals and climate resilience while enhancing green infrastructure."
    elif intent["priority"] == "transit":
        rationale += "mobility and transit access while supporting walkable, car-free development."
    elif intent["priority"] == "economic":
        rationale += "local economic development and business opportunities while supporting community ownership."
    else:
        rationale += "multiple community priorities with a balanced approach to growth and preservation."
    
    # Generate comprehensive impact analysis for the recommended plan
    recommended_plan = next((alt for alt in alternatives if alt.title == recommended), alternatives[0])
    impact = generate_comprehensive_impact(neighborhood, recommended_plan)
    
    return AnalysisResponse(
        query=request.query,
        neighborhood=neighborhood.replace("_", " ").title(),
        alternatives=alternatives,
        recommended=recommended,
        rationale=rationale,
        impact=impact
    )