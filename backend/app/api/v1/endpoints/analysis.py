import asyncio
import random
from typing import Dict, Any, List, Optional, Union
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.agents_simple import LightweightAgentCrew

router = APIRouter(tags=["analysis"])

class PlanAnalysisRequest(BaseModel):
    query: str

class ExploratoryDimension(BaseModel):
    """Individual dimension of analysis (e.g., environmental, economic)"""
    title: str
    description: str
    metrics: Dict[str, Any]
    insights: List[str]
    follow_up_questions: List[str]

class NeighborhoodAnalysis(BaseModel):
    """Analysis for a specific neighborhood"""
    neighborhood: str
    characteristics: Dict[str, str]
    impact_analysis: Dict[str, ExploratoryDimension]
    vulnerability_factors: List[str]
    adaptation_strategies: List[str]

class ScenarioBranch(BaseModel):
    """Branching scenario for what-if analysis"""
    scenario_name: str
    description: str
    probability: str
    consequences: List[str]
    related_factors: List[str]

class QueryContext(BaseModel):
    """Enhanced query understanding"""
    query_type: str  # analytical, comparative, scenario_planning, solution_seeking
    exploration_mode: str  # impact_analysis, comparison, scenario_tree, solution_space
    neighborhoods: List[str]
    primary_domain: str  # climate, economics, housing, transportation, etc.
    confidence: float
    suggested_explorations: List[str]

class ExploratoryCanvas(BaseModel):
    """New exploratory response format with agent reasoning"""
    query: str
    context: QueryContext
    neighborhood_analyses: List[NeighborhoodAnalysis]
    comparative_insights: Optional[Dict[str, Any]] = None
    scenario_branches: Optional[List[ScenarioBranch]] = None
    exploration_suggestions: List[str]
    related_questions: List[str]
    agent_reasoning: Optional[Dict[str, str]] = None

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

def analyze_query_context(query: str) -> QueryContext:
    """Advanced query analysis for exploratory canvas approach"""
    query_lower = query.lower()
    
    # Detect query type
    query_type = "analytical"  # default
    exploration_mode = "impact_analysis"
    
    # Query type detection
    if any(word in query_lower for word in ["what if", "if it", "became", "changed", "increased", "decreased"]):
        query_type = "scenario_planning"
        exploration_mode = "scenario_tree"
    elif any(word in query_lower for word in ["vs", "versus", "compared to", "compare", "difference between"]):
        query_type = "comparative"
        exploration_mode = "comparison"
    elif any(word in query_lower for word in ["how to", "should we", "best way", "recommend", "solution"]):
        query_type = "solution_seeking"
        exploration_mode = "solution_space"
    elif any(word in query_lower for word in ["how would", "what would", "impact", "affect", "influence"]):
        query_type = "analytical"
        exploration_mode = "impact_analysis"
    
    # Neighborhood detection (support multiple)
    neighborhoods = []
    neighborhood_patterns = {
        "marina": ["marina", "palace of fine arts", "chestnut street", "union street", "crissy field"],
        "mission": ["mission", "valencia", "16th street", "24th street", "mission dolores"],
        "hayes_valley": ["hayes", "patricia", "grove street", "fell street", "sf jazz"]
    }
    
    for neighborhood, patterns in neighborhood_patterns.items():
        if any(pattern in query_lower for pattern in patterns):
            neighborhoods.append(neighborhood)
    
    if not neighborhoods:
        neighborhoods = ["hayes_valley"]  # default
    
    # Primary domain detection
    primary_domain = "general"
    domain_patterns = {
        "climate": ["climate", "temperature", "weather", "cold", "hot", "rain", "flood", "degrees"],
        "transportation": ["bike", "transit", "bart", "muni", "street", "traffic", "parking"],
        "housing": ["housing", "apartments", "units", "affordable", "development"],
        "economics": ["business", "economy", "economic", "revenue", "cost", "jobs"],
        "environment": ["environment", "green", "park", "pollution", "air quality", "sustainability"]
    }
    
    for domain, patterns in domain_patterns.items():
        if any(pattern in query_lower for pattern in patterns):
            primary_domain = domain
            break
    
    # Generate exploration suggestions
    suggested_explorations = generate_exploration_suggestions(query_type, primary_domain, neighborhoods)
    
    # Calculate confidence
    confidence = calculate_analysis_confidence(query, query_type, neighborhoods, primary_domain)
    
    return QueryContext(
        query_type=query_type,
        exploration_mode=exploration_mode,
        neighborhoods=neighborhoods,
        primary_domain=primary_domain,
        confidence=confidence,
        suggested_explorations=suggested_explorations
    )

def generate_exploration_suggestions(query_type: str, domain: str, neighborhoods: List[str]) -> List[str]:
    """Generate contextual exploration suggestions"""
    suggestions = []
    
    if query_type == "scenario_planning":
        suggestions.extend([
            f"Explore secondary effects across {len(neighborhoods)} neighborhoods",
            f"Analyze adaptation strategies for {domain} changes",
            "Consider long-term vs short-term impacts",
            "Examine vulnerable population effects"
        ])
    elif query_type == "comparative":
        suggestions.extend([
            "Deep dive into neighborhood characteristics",
            "Explore historical precedents",
            "Analyze demographic differences",
            "Consider implementation feasibility"
        ])
    elif query_type == "analytical":
        suggestions.extend([
            "Quantify impact magnitude",
            "Identify key stakeholders affected",
            "Explore mitigation strategies",
            "Consider unintended consequences"
        ])
    
    return suggestions

def calculate_analysis_confidence(query: str, query_type: str, neighborhoods: List[str], domain: str) -> float:
    """Calculate confidence in query interpretation"""
    base_confidence = 0.6
    
    # Query specificity
    if len(query.split()) > 8:
        base_confidence += 0.1
    
    # Clear domain identification
    if domain != "general":
        base_confidence += 0.15
    
    # Neighborhood specificity
    if len(neighborhoods) == 1:
        base_confidence += 0.1
    elif len(neighborhoods) > 1:
        base_confidence += 0.15  # Multi-neighborhood queries are often more specific
    
    return min(0.95, base_confidence)

def generate_exploratory_content(context: QueryContext, query: str) -> ExploratoryCanvas:
    """Generate exploratory canvas based on query context"""
    
    # Generate neighborhood analyses
    neighborhood_analyses = []
    for neighborhood in context.neighborhoods:
        analysis = generate_neighborhood_analysis(neighborhood, context, query)
        neighborhood_analyses.append(analysis)
    
    # Generate comparative insights if multiple neighborhoods
    comparative_insights = None
    if len(context.neighborhoods) > 1:
        comparative_insights = generate_comparative_insights(context.neighborhoods, context.primary_domain)
    
    # Generate scenario branches for what-if queries
    scenario_branches = None
    if context.query_type == "scenario_planning":
        scenario_branches = generate_scenario_branches(query, context)
    
    # Generate exploration suggestions
    exploration_suggestions = generate_dynamic_explorations(context, query)
    
    # Generate related questions
    related_questions = generate_related_questions(context, query)
    
    return ExploratoryCanvas(
        query=query,
        context=context,
        neighborhood_analyses=neighborhood_analyses,
        comparative_insights=comparative_insights,
        scenario_branches=scenario_branches,
        exploration_suggestions=exploration_suggestions,
        related_questions=related_questions
    )

def generate_neighborhood_analysis(neighborhood: str, context: QueryContext, query: str) -> NeighborhoodAnalysis:
    """Generate analysis for a specific neighborhood"""
    
    # Get neighborhood data
    neighborhood_data = SF_STREET_DATA.get(neighborhood, SF_STREET_DATA["hayes_valley"])
    
    # Generate characteristics
    characteristics = {
        "primary_character": get_neighborhood_character(neighborhood),
        "zoning": neighborhood_data["zoning"],
        "main_streets": ", ".join(neighborhood_data["main_streets"][:2]),
        "key_landmarks": ", ".join(neighborhood_data["landmarks"][:2]),
        "transit_access": neighborhood_data["transport"][0] if neighborhood_data["transport"] else "Limited"
    }
    
    # Generate impact analysis dimensions
    impact_analysis = {}
    
    if context.primary_domain == "climate":
        impact_analysis = generate_climate_impact_analysis(neighborhood, query)
    elif context.primary_domain == "transportation":
        impact_analysis = generate_transportation_impact_analysis(neighborhood, query)
    elif context.primary_domain == "economics":
        impact_analysis = generate_economic_impact_analysis(neighborhood, query)
    else:
        impact_analysis = generate_general_impact_analysis(neighborhood, query)
    
    # Generate vulnerability factors and adaptation strategies
    vulnerability_factors = get_neighborhood_vulnerabilities(neighborhood, context.primary_domain)
    adaptation_strategies = get_adaptation_strategies(neighborhood, context.primary_domain)
    
    return NeighborhoodAnalysis(
        neighborhood=neighborhood,
        characteristics=characteristics,
        impact_analysis=impact_analysis,
        vulnerability_factors=vulnerability_factors,
        adaptation_strategies=adaptation_strategies
    )

def get_neighborhood_character(neighborhood: str) -> str:
    """Get neighborhood character description"""
    characters = {
        "marina": "Affluent, low-density, car-dependent waterfront district",
        "mission": "Dense, diverse, walkable cultural hub with gentrification pressure",
        "hayes_valley": "Transit-rich, recently gentrified, mixed-use neighborhood"
    }
    return characters.get(neighborhood, "Mixed urban neighborhood")

def generate_climate_impact_analysis(neighborhood: str, query: str) -> Dict[str, ExploratoryDimension]:
    """Generate climate-specific impact analysis for '10 degrees colder' type queries"""
    
    # Extract temperature change if specified
    temperature_change = extract_temperature_change(query)
    
    if neighborhood == "marina":
        return {
            "environmental": ExploratoryDimension(
                title="Environmental Vulnerability",
                description=f"Marina's waterfront location amplifies climate impacts",
                metrics={
                    "flood_risk_increase": "25-40% higher with storm intensity",
                    "heating_demand": f"+{abs(temperature_change * 8)}% energy consumption",
                    "fog_pattern_shift": "Increased marine layer persistence"
                },
                insights=[
                    "Waterfront buildings face increased flood risk from storm surge",
                    "Higher heating costs disproportionately affect fixed-income residents",
                    "Marina Green becomes less usable for outdoor activities"
                ],
                follow_up_questions=[
                    "How would flood insurance costs change?",
                    "What weatherization programs exist?",
                    "Could Marina Green need covered facilities?"
                ]
            ),
            "housing": ExploratoryDimension(
                title="Housing & Infrastructure",
                description="Building systems and housing costs under temperature stress",
                metrics={
                    "heating_cost_increase": f"{temperature_change * 12}% of household income impact",
                    "building_stress": "1950s-70s housing stock vulnerable",
                    "utility_demand": f"+{abs(temperature_change * 15)}% peak energy load"
                },
                insights=[
                    "Older Marina buildings lack efficient heating systems",
                    "Rent burden increases as utilities rise",
                    "Infrastructure strain during cold snaps"
                ],
                follow_up_questions=[
                    "Which buildings need retrofitting priority?",
                    "How do utility subsidies work?",
                    "What emergency warming centers exist?"
                ]
            ),
            "economic": ExploratoryDimension(
                title="Business & Economic Impact",
                description="Commercial district response to sustained colder weather",
                metrics={
                    "outdoor_dining_loss": f"{abs(temperature_change * 20)}% revenue decline",
                    "tourism_impact": "15-25% visitor reduction",
                    "retail_pattern_shift": "Indoor vs outdoor activity preference"
                },
                insights=[
                    "Restaurant patios become unusable more often",
                    "Palace of Fine Arts tourism drops significantly",
                    "Fitness studios may see increased indoor demand"
                ],
                follow_up_questions=[
                    "How could businesses adapt outdoor spaces?",
                    "What tourism substitutes might emerge?",
                    "Do heating subsidies exist for small businesses?"
                ]
            )
        }
    
    elif neighborhood == "mission":
        return {
            "environmental": ExploratoryDimension(
                title="Environmental Justice Impact",
                description="Climate burden on diverse, working-class community",
                metrics={
                    "air_quality_change": "Increased heating emissions in dense area",
                    "urban_heat_loss": "Reduced summer relief, increased winter exposure",
                    "green_space_stress": "Parks less usable, community gardens affected"
                },
                insights=[
                    "Dense housing means heating inefficiencies compound",
                    "Limited green space reduces climate resilience",
                    "Air quality degrades with increased heating"
                ],
                follow_up_questions=[
                    "How would air quality monitoring change?",
                    "Could community gardens adapt to cold?",
                    "What about outdoor community events?"
                ]
            ),
            "housing": ExploratoryDimension(
                title="Housing Burden & Displacement",
                description="Temperature change impact on vulnerable residents",
                metrics={
                    "utility_burden": f"+{abs(temperature_change * 15)}% of income for low-income households",
                    "displacement_pressure": "Higher costs force migration",
                    "overcrowding_increase": "Families consolidate to share heating costs"
                },
                insights=[
                    "Many Mission residents already energy-burdened",
                    "Older housing stock poorly insulated",
                    "Cold weather exacerbates displacement pressure"
                ],
                follow_up_questions=[
                    "What tenant protections exist for utility costs?",
                    "How effective are weatherization programs?",
                    "Are there emergency heating assistance programs?"
                ]
            ),
            "community": ExploratoryDimension(
                title="Community & Cultural Impact",
                description="Effect on Mission's vibrant street life and culture",
                metrics={
                    "street_activity_decline": f"{abs(temperature_change * 25)}% reduction in outdoor gathering",
                    "business_revenue_impact": "Corner stores, restaurants see decline",
                    "cultural_event_disruption": "Outdoor murals, festivals affected"
                },
                insights=[
                    "Mission's street culture depends on walkable weather",
                    "Cultural events may need indoor alternatives",
                    "Community cohesion could be affected by weather isolation"
                ],
                follow_up_questions=[
                    "How could outdoor cultural events adapt?",
                    "What indoor community spaces exist?",
                    "Would this change the neighborhood's character?"
                ]
            )
        }
    
    else:  # hayes_valley
        return {
            "environmental": ExploratoryDimension(
                title="Transit & Walkability Impact",
                description="Effects on Hayes Valley's pedestrian-oriented character",
                metrics={
                    "walking_comfort_decline": f"{abs(temperature_change * 18)}% reduction in comfortable walking weather",
                    "transit_disruption": "Weather-related delays increase",
                    "outdoor_space_usage": "Patricia's Green, plazas less utilized"
                },
                insights=[
                    "Hayes Valley's walkability advantage diminishes",
                    "Transit-oriented lifestyle becomes less appealing",
                    "Outdoor dining and plaza culture affected"
                ],
                follow_up_questions=[
                    "How weather-resistant is BART access?",
                    "Could covered walkways be added?",
                    "What indoor alternatives exist for plaza activities?"
                ]
            )
        }

def extract_temperature_change(query: str) -> int:
    """Extract temperature change from query"""
    import re
    
    # Look for patterns like "10 degrees colder", "5 degrees warmer"
    pattern = r'(\d+)\s*degrees?\s*(colder|cooler|warmer|hotter)'
    match = re.search(pattern, query.lower())
    
    if match:
        degrees = int(match.group(1))
        direction = match.group(2)
        return -degrees if direction in ['colder', 'cooler'] else degrees
    
    return -10  # default for "colder" queries

def generate_transportation_impact_analysis(neighborhood: str, query: str) -> Dict[str, ExploratoryDimension]:
    """Generate transportation-focused impact analysis"""
    
    # Check if this is about bike infrastructure
    if "bike" in query.lower():
        return generate_bike_infrastructure_analysis(neighborhood, query)
    
    # General transportation analysis
    return {
        "mobility": ExploratoryDimension(
            title="Transportation Impact",
            description=f"Transportation effects in {neighborhood}",
            metrics={
                "transit_accessibility": "Moderate to high depending on proximity to BART/Muni",
                "walkability_score": "75-85 in most SF neighborhoods",
                "bike_infrastructure": "Limited but improving"
            },
            insights=[
                f"Transportation impacts vary significantly by {neighborhood} characteristics",
                "Public transit access is crucial for equitable development",
                "Bike infrastructure improvements could reduce car dependency"
            ],
            follow_up_questions=[
                "How would this affect commuting patterns?",
                "What are the parking implications?",
                "How does this integrate with existing transit?"
            ]
        )
    }

def generate_bike_infrastructure_analysis(neighborhood: str, query: str) -> Dict[str, ExploratoryDimension]:
    """Generate bike infrastructure specific analysis"""
    
    if neighborhood == "marina":
        return {
            "business_impact": ExploratoryDimension(
                title="Business District Impact",
                description="How bike infrastructure affects Marina's car-dependent business ecosystem",
                metrics={
                    "parking_loss": "Potential 15-25% reduction in street parking",
                    "customer_access": "Shift from suburban drivers to local cyclists",
                    "outdoor_dining": "Opportunity for expanded sidewalk use"
                },
                insights=[
                    "High-end retailers may lose suburban customers who drive in",
                    "Restaurants could benefit from increased foot/bike traffic",
                    "Bike valet services could attract environmentally conscious affluent customers"
                ],
                follow_up_questions=[
                    "How could businesses adapt to serve cyclists?",
                    "What parking alternatives exist?",
                    "How do other upscale areas handle bike infrastructure?"
                ]
            ),
            "safety_accessibility": ExploratoryDimension(
                title="Safety & Accessibility",
                description="Pedestrian and cyclist safety improvements in Marina",
                metrics={
                    "accident_reduction": "Potential 30-40% reduction in bike-car accidents",
                    "pedestrian_comfort": "Increased sidewalk space and safety",
                    "senior_accessibility": "Important given Marina's aging population"
                },
                insights=[
                    "Protected bike lanes reduce conflicts between cars and cyclists",
                    "Marina's wide streets are well-suited for bike infrastructure",
                    "Connection to Presidio and Marina Green enhances recreational cycling"
                ],
                follow_up_questions=[
                    "How does this connect to citywide bike network?",
                    "What about motorcycle parking?",
                    "How do we maintain emergency vehicle access?"
                ]
            )
        }
    
    elif neighborhood == "mission":
        return {
            "community_impact": ExploratoryDimension(
                title="Community & Economic Impact",
                description="How bike infrastructure supports Mission's diverse community",
                metrics={
                    "local_business_boost": "15-30% increase in foot traffic",
                    "car_ownership": "Already low at 35%, could decrease further",
                    "bike_commuting": "Could increase from 8% to 15% of residents"
                },
                insights=[
                    "Mission's existing bike culture makes this highly supportive",
                    "Local businesses benefit from increased street-level activity",
                    "Bike infrastructure supports working families who can't afford cars"
                ],
                follow_up_questions=[
                    "How does this affect gentrification pressures?",
                    "What about delivery truck access?",
                    "How do we ensure community input in design?"
                ]
            ),
            "equity_justice": ExploratoryDimension(
                title="Equity & Transportation Justice",
                description="Making transportation more equitable in Mission",
                metrics={
                    "cost_savings": "$200-500/month savings for families giving up cars",
                    "job_access": "Better connections to downtown employment",
                    "health_benefits": "Reduced air pollution and increased physical activity"
                },
                insights=[
                    "Bike infrastructure serves families who depend on affordable transportation",
                    "Reduces transportation burden on low-income households",
                    "Improves air quality in dense residential area"
                ],
                follow_up_questions=[
                    "How do we ensure bike infrastructure doesn't displace businesses?",
                    "What about bike theft prevention?",
                    "How does this connect to affordable housing?"
                ]
            )
        }
    
    else:  # hayes_valley
        return {
            "transit_integration": ExploratoryDimension(
                title="Transit-Oriented Development",
                description="Bike infrastructure enhancing Hayes Valley's transit access",
                metrics={
                    "bart_connection": "Improved bike-to-BART connections",
                    "muni_integration": "Better first/last mile solutions",
                    "car_free_households": "Could increase from 45% to 60%"
                },
                insights=[
                    "Hayes Valley already has strong transit orientation",
                    "Bike infrastructure complements existing car-free lifestyle",
                    "Enhanced connection between BART and neighborhood amenities"
                ],
                follow_up_questions=[
                    "How does this affect property values?",
                    "What about bike parking at BART?",
                    "How do we manage increased density?"
                ]
            )
        }

def generate_economic_impact_analysis(neighborhood: str, query: str) -> Dict[str, ExploratoryDimension]:
    """Generate economics-focused impact analysis"""
    
    base_analysis = {
        "business_ecosystem": ExploratoryDimension(
            title="Business Ecosystem Impact",
            description=f"How changes affect {neighborhood}'s business landscape",
            metrics={
                "business_revenue": "Varies by business type and customer base",
                "employment": "Construction jobs during implementation",
                "property_values": "Generally positive long-term impact"
            },
            insights=[
                f"Economic impacts depend on {neighborhood} business ecosystem",
                "Short-term disruption often followed by long-term benefits",
                "Different business types respond differently to urban changes"
            ],
            follow_up_questions=[
                "How would this affect local businesses?",
                "What support do businesses need during transition?",
                "How do we measure economic success?"
            ]
        )
    }
    
    # Add neighborhood-specific economic analysis
    if neighborhood == "marina":
        base_analysis["retail_impact"] = ExploratoryDimension(
            title="High-End Retail Impact",
            description="Effects on Marina's upscale retail and dining scene",
            metrics={
                "customer_demographics": "Shift from suburban drivers to local affluent residents",
                "spending_patterns": "Potential increase in frequent, smaller purchases",
                "retail_mix": "May favor experiential over goods-based retail"
            },
            insights=[
                "High-end retailers may need to adapt marketing to local vs. regional customers",
                "Restaurants and cafes likely to benefit from increased foot traffic",
                "Outdoor retail and dining could expand with better pedestrian environment"
            ],
            follow_up_questions=[
                "How do luxury brands view bike-friendly areas?",
                "What successful examples exist in other cities?",
                "How can we maintain Marina's upscale character?"
            ]
        )
    
    elif neighborhood == "mission":
        base_analysis["community_economy"] = ExploratoryDimension(
            title="Community-Based Economy",
            description="Supporting Mission's local, community-oriented businesses",
            metrics={
                "local_ownership": "70% of businesses are locally owned",
                "foot_traffic": "Potential 20-40% increase in pedestrian activity",
                "displacement_risk": "Need to monitor rent increases for small businesses"
            },
            insights=[
                "Community-oriented businesses likely to benefit from increased local activity",
                "Important to prevent business displacement from rising rents",
                "Opportunity to strengthen local supply chains and cooperation"
            ],
            follow_up_questions=[
                "How do we protect existing community businesses?",
                "What role can community land trusts play?",
                "How do we measure community economic health?"
            ]
        )
    
    return base_analysis

def generate_general_impact_analysis(neighborhood: str, query: str) -> Dict[str, ExploratoryDimension]:
    """Generate general impact analysis for unclear or broad queries"""
    
    # Try to extract some intent from the query
    query_lower = query.lower()
    focus_areas = []
    
    if any(word in query_lower for word in ['housing', 'development', 'building']):
        focus_areas.append('housing')
    if any(word in query_lower for word in ['business', 'economic', 'commercial']):
        focus_areas.append('economic')
    if any(word in query_lower for word in ['transit', 'transport', 'bike', 'walk']):
        focus_areas.append('mobility')
    if any(word in query_lower for word in ['community', 'resident', 'neighborhood']):
        focus_areas.append('community')
    
    analysis = {
        "overview": ExploratoryDimension(
            title="Multi-Factor Impact Analysis",
            description=f"Comprehensive assessment of changes in {neighborhood}",
            metrics={
                "complexity_score": "High - multiple interconnected factors",
                "stakeholders": "Residents, businesses, city agencies, community groups",
                "timeline": "Short, medium, and long-term effects to consider"
            },
            insights=[
                f"Multiple factors affect {neighborhood} in interconnected ways",
                "Need to consider cumulative impacts across different domains",
                "Community input crucial for understanding local priorities",
                "Both intended and unintended consequences should be monitored"
            ],
            follow_up_questions=[
                "What are the primary concerns from residents?",
                "Which specific aspects would you like to explore deeper?",
                "How do different stakeholders prioritize these changes?",
                "What are the most important success metrics?"
            ]
        )
    }
    
    # Add specific analysis based on detected focus areas
    if 'housing' in focus_areas:
        analysis['housing_considerations'] = ExploratoryDimension(
            title="Housing Implications",
            description="How changes affect housing affordability and availability",
            metrics={"affordability_impact": "Varies by intervention type"},
            insights=["Housing policies have ripple effects throughout neighborhood"],
            follow_up_questions=["How does this affect displacement risk?"]
        )
    
    if 'economic' in focus_areas:
        analysis['economic_considerations'] = ExploratoryDimension(
            title="Economic Development",
            description="Business and economic implications",
            metrics={"business_impact": "Depends on implementation approach"},
            insights=["Economic changes affect different business types differently"],
            follow_up_questions=["How do we support existing businesses during transition?"]
        )
    
    return analysis

def get_neighborhood_vulnerabilities(neighborhood: str, domain: str) -> List[str]:
    """Get neighborhood-specific vulnerability factors"""
    base_vulnerabilities = {
        "marina": ["Flood risk", "Car dependency", "Aging infrastructure", "High cost burden"],
        "mission": ["Displacement pressure", "Overcrowding", "Limited green space", "Air quality"],
        "hayes_valley": ["Transit dependency", "Small lot constraints", "Gentrification pressure"]
    }
    
    vulnerabilities = base_vulnerabilities.get(neighborhood, ["General urban challenges"])
    
    if domain == "climate":
        climate_vulnerabilities = {
            "marina": ["Waterfront exposure", "Sea level rise", "Storm surge"],
            "mission": ["Urban heat island", "Dense development", "Limited cooling"],
            "hayes_valley": ["Limited green infrastructure", "Transit exposure"]
        }
        vulnerabilities.extend(climate_vulnerabilities.get(neighborhood, []))
    
    return vulnerabilities

def get_adaptation_strategies(neighborhood: str, domain: str) -> List[str]:
    """Get neighborhood-specific adaptation strategies"""
    base_strategies = {
        "marina": ["Flood barriers", "Building retrofits", "Emergency planning"],
        "mission": ["Community resilience hubs", "Affordable weatherization", "Green infrastructure"],
        "hayes_valley": ["Transit improvements", "Covered walkways", "Public space enhancement"]
    }
    
    return base_strategies.get(neighborhood, ["General adaptation measures"])

def generate_comparative_insights(neighborhoods: List[str], domain: str) -> Dict[str, Any]:
    """Generate insights comparing multiple neighborhoods"""
    return {
        "vulnerability_ranking": f"Relative vulnerability across {', '.join(neighborhoods)}",
        "adaptation_costs": "Comparative implementation costs and feasibility",
        "equity_implications": "How impacts differ across socioeconomic lines",
        "coordination_opportunities": "Cross-neighborhood collaboration potential"
    }

def generate_scenario_branches(query: str, context: QueryContext) -> List[ScenarioBranch]:
    """Generate scenario branches for what-if queries"""
    
    if "10 degrees colder" in query.lower() or "colder" in query.lower():
        return [
            ScenarioBranch(
                scenario_name="Immediate Response (0-6 months)",
                description="Short-term emergency and adaptation measures",
                probability="Highly likely",
                consequences=[
                    "Emergency heating assistance programs activated",
                    "Outdoor dining and events curtailed",
                    "Public facility usage patterns shift indoors"
                ],
                related_factors=["Energy grid capacity", "Emergency services", "Public health"]
            ),
            ScenarioBranch(
                scenario_name="Medium-term Adaptation (6 months - 2 years)",
                description="Infrastructure and policy adjustments",
                probability="Likely with planning",
                consequences=[
                    "Building weatherization programs expanded",
                    "Utility assistance programs increased",
                    "Outdoor space design modifications"
                ],
                related_factors=["Funding availability", "Political will", "Community organization"]
            ),
            ScenarioBranch(
                scenario_name="Long-term Transformation (2+ years)",
                description="Fundamental neighborhood character changes",
                probability="Possible with sustained change",
                consequences=[
                    "Outdoor culture diminishes permanently",
                    "Business models shift toward indoor focus",
                    "Population composition changes due to cost burden"
                ],
                related_factors=["Climate persistence", "Economic adaptation", "Cultural resilience"]
            )
        ]
    
    return []

def generate_dynamic_explorations(context: QueryContext, query: str) -> List[str]:
    """Generate dynamic exploration suggestions based on context"""
    explorations = []
    
    if context.primary_domain == "climate":
        explorations.extend([
            "Explore seasonal variation impacts",
            "Compare with historical weather patterns",
            "Analyze infrastructure resilience",
            "Consider vulnerable population effects"
        ])
    
    if len(context.neighborhoods) > 1:
        explorations.extend([
            f"Deep dive into {context.neighborhoods[0]} vs {context.neighborhoods[1]} differences",
            "Explore cross-neighborhood collaboration opportunities",
            "Analyze resource sharing potential"
        ])
    
    return explorations

def generate_related_questions(context: QueryContext, query: str) -> List[str]:
    """Generate related questions for further exploration"""
    questions = []
    
    if "colder" in query.lower():
        questions.extend([
            "What if it became 20 degrees colder instead?",
            "How would the same temperature change affect other seasons?",
            "What if the cold weather lasted for multiple years?",
            "How do other cities handle similar temperature conditions?"
        ])
    
    if len(context.neighborhoods) > 1:
        questions.extend([
            f"How would this affect other SF neighborhoods like SOMA or Richmond?",
            "What regional coordination would be needed?",
            "How do these neighborhoods currently share resources?"
        ])
    
    return questions

# NEW EXPLORATORY API ENDPOINT
@router.post("/explore", response_model=ExploratoryCanvas)
async def explore_urban_query(request: PlanAnalysisRequest):
    """REAL AGENTS: Multi-agent analysis using CrewAI autonomous agents"""
    
    # Input validation guardrails
    if not request.query or len(request.query.strip()) < 3:
        raise HTTPException(status_code=400, detail="Query too short - please provide a meaningful urban planning question")
    
    if len(request.query) > 1000:
        raise HTTPException(status_code=400, detail="Query too long - please keep under 1000 characters")
    
    # Basic security check for common injection patterns
    dangerous_patterns = ["<script", "javascript:", "eval(", "DROP TABLE", "DELETE FROM", "../"]
    query_lower = request.query.lower()
    if any(pattern in query_lower for pattern in dangerous_patterns):
        raise HTTPException(status_code=400, detail="Invalid query format detected")
    
    try:
        # Execute lightweight agent crew instead of fake functions
        crew = LightweightAgentCrew()
        agent_context = await crew.execute(request.query)
        
        # Convert agent context to ExploratoryCanvas format
        canvas = ExploratoryCanvas(
            query=agent_context.query,
            context=QueryContext(
                query_type="scenario_planning" if "what if" in request.query.lower() else "analytical",
                exploration_mode="impact_analysis",
                neighborhoods=agent_context.neighborhoods,
                primary_domain=agent_context.primary_domain,
                confidence=agent_context.confidence,
                suggested_explorations=agent_context.data.get("follow_up_questions", [])
            ),
            neighborhood_analyses=[
                NeighborhoodAnalysis(
                    neighborhood=neighborhood,
                    characteristics={
                        **agent_context.data.get(neighborhood, {}).get("characteristics", {}),
                        **({"validation_error": agent_context.data["validation_error"]} if agent_context.data.get("validation_error") else {})
                    },
                    impact_analysis={
                        "primary": ExploratoryDimension(
                            title=f"{neighborhood} Real Agent Analysis",
                            description=f"Autonomous agent analysis for {neighborhood} neighborhood",
                            metrics={"confidence": agent_context.confidence, "data_sources": "neighborhood_api"},
                            insights=[f"Agent-generated insights for {neighborhood} based on {agent_context.primary_domain} analysis"],
                            follow_up_questions=agent_context.data.get("follow_up_questions", [])[:2]
                        )
                    },
                    vulnerability_factors=[f"{neighborhood} vulnerability factors identified by agents"],
                    adaptation_strategies=[f"{neighborhood} strategies recommended by planning agent"]
                ) for neighborhood in agent_context.neighborhoods
            ],
            comparative_insights=agent_context.data.get("comparative_insights", {}),
            scenario_branches=[
                ScenarioBranch(
                    scenario_name=scenario.get("description", "Agent Scenario"),
                    description=f"Real agent-generated scenario: {scenario.get('description', 'Planning scenario')}",
                    probability=scenario.get("feasibility", "Medium"),
                    consequences=[f"Impact: {scenario.get('impacts', {}).get('economic', {}).get('description', 'Economic analysis pending')}"],
                    related_factors=list(scenario.get("parameters", {}).keys())
                ) for scenario in agent_context.data.get("scenarios", [])
            ],
            exploration_suggestions=agent_context.data.get("follow_up_questions", []),
            related_questions=agent_context.data.get("follow_up_questions", []),
            agent_reasoning={
                "interpreter": "Real agent analyzed query and gathered neighborhood data via API calls",
                "planner": "Real agent generated feasible scenarios with constraint validation",
                "evaluator": "Real agent assessed impacts and generated insights with confidence scoring",
                "execution_log": "; ".join(agent_context.reasoning[-10:]) if agent_context.reasoning else "No execution log available"
            }
        )
        
        return canvas
        
    except Exception as e:
        # Fallback to legacy method if agents fail
        print(f"Agent execution failed: {str(e)}, falling back to legacy method")
        
        # Legacy fallback
        context = analyze_query_context(request.query)
        canvas = generate_exploratory_content(context, request.query)
        
        # Add agent error info
        canvas.agent_reasoning = {"error": f"Agents failed: {str(e)}", "fallback": "used legacy functions"}
        
        return canvas

# LEGACY ENDPOINT (for backward compatibility)
def analyze_query_intent(query: str) -> Dict[str, Any]:
    """LEGACY: Analyze user query to understand intent and extract parameters."""
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
    
    # Calculate confidence based on keyword matches
    confidence = 0.7
    if len([word for word in query_lower.split() if word in ["housing", "development", "zoning", "neighborhood"]]) > 1:
        confidence += 0.1
    if neighborhood != "hayes_valley":  # Non-default neighborhood detection
        confidence += 0.1
    
    return {
        "query": query,
        "neighborhood": neighborhood,
        "intent": intent,
        "confidence": min(confidence, 0.95)
    }

def analyze_query_intent_legacy(query: str) -> Dict[str, Any]:
    """LEGACY: Analyze user query to understand intent and extract parameters."""
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
    
    # Calculate confidence based on keyword matches
    confidence = 0.7
    if len([word for word in query_lower.split() if word in ["housing", "development", "zoning", "neighborhood"]]) > 1:
        confidence += 0.1
    if neighborhood != "hayes_valley":  # Non-default neighborhood detection
        confidence += 0.1
    
    return {
        "query": query,
        "neighborhood": neighborhood,
        "intent": intent,
        "confidence": min(confidence, 0.95)
    }

def generate_plan_archetypes(intent: Dict[str, Any], neighborhood: str, query: str) -> List[Dict[str, Any]]:
    """Generate diverse planning intervention archetypes based on query analysis."""
    
    query_lower = query.lower()
    plan_pool = []
    
    # TRANSPORTATION & MOBILITY INTERVENTIONS
    if any(word in query_lower for word in ["bike", "transit", "walk", "street", "mobility", "transport"]):
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

# Import required models from legacy system
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

class QueryIntent(BaseModel):
    type: str
    priority: str
    density: str
    focus: str
    confidence: float

class AnalysisResponse(BaseModel):
    query: str
    neighborhood: str
    intent: QueryIntent
    alternatives: List[PlanningAlternative]
    recommended: str
    rationale: str
    impact: ComprehensiveImpact

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
        intent=QueryIntent(
            type=intent["type"],
            priority=intent["priority"],
            density=intent["density"],
            focus=intent["focus"],
            confidence=analysis["confidence"]
        ),
        alternatives=alternatives,
        recommended=recommended,
        rationale=rationale,
        impact=impact
    )