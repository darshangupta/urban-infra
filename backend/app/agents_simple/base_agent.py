"""
Lightweight Agent System for Urban Planning
No heavy dependencies - just asyncio and httpx
"""

import asyncio
import httpx
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
import time

@dataclass
class AgentContext:
    """Shared context between agents"""
    query: str
    neighborhoods: List[str] = None
    primary_domain: str = None
    confidence: float = 0.0
    data: Dict[str, Any] = None
    reasoning: List[str] = None
    
    def __post_init__(self):
        if self.neighborhoods is None:
            self.neighborhoods = []
        if self.data is None:
            self.data = {}
        if self.reasoning is None:
            self.reasoning = []

class AgentTool:
    """Simple tool for making API calls"""
    
    def __init__(self, base_url: str = "http://localhost:8001/api/v1"):
        self.base_url = base_url
    
    async def call_api(self, endpoint: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
        """Make API call to neighborhood endpoints"""
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}/{endpoint}"
                
                if method == "GET":
                    response = await client.get(url)
                elif method == "POST":
                    response = await client.post(url, json=data)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"error": f"API call failed: {response.status_code}"}
                    
        except Exception as e:
            return {"error": f"Tool error: {str(e)}"}

class BaseAgent(ABC):
    """Base agent class"""
    
    def __init__(self, name: str, role: str, tools: List[AgentTool] = None):
        self.name = name
        self.role = role
        self.tools = tools or [AgentTool()]
        self.execution_log = []
    
    def log(self, message: str):
        """Log agent reasoning"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {self.name}: {message}"
        self.execution_log.append(log_entry)
        print(log_entry)  # For demo purposes
    
    @abstractmethod
    async def execute(self, context: AgentContext) -> AgentContext:
        """Execute agent's main task"""
        pass

class InterpreterAgent(BaseAgent):
    """Agent 1: Understands queries and gathers context"""
    
    def __init__(self):
        super().__init__("Interpreter", "Query Understanding & Context Gathering")
    
    async def execute(self, context: AgentContext) -> AgentContext:
        """Analyze query and gather neighborhood data"""
        self.log(f"Analyzing query: '{context.query}'")
        
        # GUARDRAIL: Validate query first
        if not self._is_valid_urban_planning_query(context.query):
            context.confidence = 0.1
            context.neighborhoods = ["Mission"]  # Default fallback
            context.primary_domain = "general"
            context.data["validation_error"] = "Query does not appear to be related to urban planning"
            self.log("❌ Query validation failed - not urban planning related")
            context.reasoning.extend(self.execution_log)
            return context
        
        # Step 1: Extract neighborhoods
        neighborhoods = self._extract_neighborhoods(context.query)
        context.neighborhoods = neighborhoods
        self.log(f"Identified neighborhoods: {neighborhoods}")
        
        # Step 2: Determine domain
        domain = self._classify_domain(context.query)
        context.primary_domain = domain
        self.log(f"Primary domain: {domain}")
        
        # Step 3: Gather neighborhood data using tools
        await self._gather_neighborhood_data(context)
        
        # Step 4: Set confidence
        context.confidence = self._calculate_confidence(context)
        self.log(f"Analysis confidence: {context.confidence:.2f}")
        
        context.reasoning.extend(self.execution_log)
        return context
    
    def _extract_neighborhoods(self, query: str) -> List[str]:
        """Extract neighborhood names from query"""
        query_lower = query.lower()
        neighborhoods = []
        
        neighborhood_map = {
            "mission": "Mission",
            "marina": "Marina", 
            "hayes": "Hayes Valley",
            "hayes valley": "Hayes Valley"
        }
        
        for key, name in neighborhood_map.items():
            if key in query_lower:
                neighborhoods.append(name)
        
        # Default to Mission if none found
        if not neighborhoods:
            neighborhoods = ["Mission"]
            
        return neighborhoods
    
    def _classify_domain(self, query: str) -> str:
        """Classify the primary planning domain"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["climate", "temperature", "flood", "environment"]):
            return "climate"
        elif any(word in query_lower for word in ["housing", "units", "development", "density"]):
            return "housing"
        elif any(word in query_lower for word in ["bike", "transit", "transport", "walkable", "cars", "traffic", "vehicles", "parking", "congestion", "mobility", "commute", "driving"]):
            return "transportation"
        elif any(word in query_lower for word in ["business", "economic", "revenue", "jobs"]):
            return "economics"
        else:
            return "general"
    
    async def _gather_neighborhood_data(self, context: AgentContext):
        """Use tools to gather neighborhood data"""
        for neighborhood in context.neighborhoods:
            self.log(f"Gathering data for {neighborhood}...")
            
            # Call neighborhood API
            neighborhood_key = neighborhood.lower().replace(" ", "_")
            zoning_data = await self.tools[0].call_api(f"neighborhoods/{neighborhood_key}/zoning")
            
            if "error" not in zoning_data:
                context.data[neighborhood] = {
                    "zoning": zoning_data,
                    "characteristics": self._get_neighborhood_characteristics(neighborhood)
                }
                self.log(f"✓ Data gathered for {neighborhood}")
            else:
                self.log(f"⚠ Could not gather data for {neighborhood}: {zoning_data.get('error', 'Unknown error')}")
    
    def _get_neighborhood_characteristics(self, neighborhood: str) -> Dict[str, str]:
        """Get basic neighborhood characteristics"""
        characteristics = {
            "Mission": {"density": "high", "transit": "excellent", "character": "diverse"},
            "Marina": {"density": "low", "transit": "limited", "character": "affluent"},
            "Hayes Valley": {"density": "medium", "transit": "excellent", "character": "gentrifying"}
        }
        return characteristics.get(neighborhood, {"density": "unknown", "transit": "unknown", "character": "unknown"})
    
    def _is_valid_urban_planning_query(self, query: str) -> bool:
        """GUARDRAIL: Check if query is related to urban planning"""
        if not query or len(query.strip()) < 3:
            return False
        
        # Clean the query
        query_clean = query.strip().lower()
        
        # Check for random characters/gibberish
        if len([c for c in query_clean if c.isalpha()]) < len(query_clean) * 0.6:
            return False
        
        # Urban planning keywords
        urban_keywords = [
            # Core urban planning
            "housing", "development", "zoning", "neighborhood", "building", "density",
            "transit", "transportation", "walkable", "bike", "pedestrian", "planning",
            
            # SF neighborhoods
            "mission", "marina", "hayes", "valley", "francisco", "sf",
            
            # Infrastructure  
            "infrastructure", "utilities", "water", "sewer", "street", "road",
            "park", "green", "space", "public", "community",
            
            # Policy/Planning
            "affordable", "gentrification", "displacement", "equity", "policy",
            "permit", "approval", "variance", "height", "setback",
            
            # Environmental
            "climate", "flood", "sea level", "temperature", "environmental",
            "sustainability", "energy", "solar", "green building",
            
            # Economic
            "cost", "price", "value", "economic", "business", "commercial",
            "retail", "office", "mixed use",
            
            # Questions words that might indicate planning queries
            "what if", "how would", "where should", "can we", "should we",
            "impact", "effect", "affect", "change", "improve", "add", "build"
        ]
        
        # Check if query contains urban planning concepts
        has_urban_context = any(keyword in query_clean for keyword in urban_keywords)
        
        # Check for question structure
        has_question_structure = any(q in query_clean for q in ["?", "what", "how", "where", "when", "why", "can", "should", "would"])
        
        return has_urban_context or has_question_structure
    
    def _calculate_confidence(self, context: AgentContext) -> float:
        """Calculate confidence based on data availability"""
        if not context.neighborhoods:
            return 0.3
        
        data_score = len([n for n in context.neighborhoods if n in context.data]) / len(context.neighborhoods)
        domain_score = 0.9 if context.primary_domain != "general" else 0.6
        
        return (data_score * 0.6 + domain_score * 0.4)

class PlannerAgent(BaseAgent):
    """Agent 2: Generates feasible scenarios"""
    
    def __init__(self):
        super().__init__("Planner", "Scenario Generation & Validation")
    
    async def execute(self, context: AgentContext) -> AgentContext:
        """Generate planning scenarios based on context"""
        self.log(f"Generating scenarios for {context.primary_domain} in {context.neighborhoods}")
        
        # Generate scenarios based on domain
        scenarios = await self._generate_scenarios(context)
        context.data["scenarios"] = scenarios
        
        # Validate scenarios with tools
        await self._validate_scenarios(context)
        
        context.reasoning.extend(self.execution_log)
        return context
    
    async def _generate_scenarios(self, context: AgentContext) -> List[Dict[str, Any]]:
        """Generate domain-specific scenarios"""
        if context.primary_domain == "housing":
            return await self._housing_scenarios(context)
        elif context.primary_domain == "climate":
            return await self._climate_scenarios(context)
        elif context.primary_domain == "transportation":
            return await self._transportation_scenarios(context)
        else:
            return await self._general_scenarios(context)
    
    async def _housing_scenarios(self, context: AgentContext) -> List[Dict[str, Any]]:
        """Generate housing development scenarios"""
        scenarios = []
        
        for neighborhood in context.neighborhoods:
            self.log(f"Creating housing scenario for {neighborhood}")
            
            # Get zoning constraints
            neighborhood_data = context.data.get(neighborhood, {})
            zoning = neighborhood_data.get("zoning", {})
            
            scenario = {
                "neighborhood": neighborhood,
                "type": "housing_development",
                "description": f"Affordable housing development in {neighborhood}",
                "parameters": {
                    "units": 50 if neighborhood == "Mission" else 30,
                    "affordability": "30% affordable" if neighborhood == "Mission" else "20% affordable",
                    "height": "4 stories" if neighborhood == "Mission" else "3 stories"
                },
                "feasibility": "pending_validation"
            }
            scenarios.append(scenario)
        
        return scenarios
    
    async def _climate_scenarios(self, context: AgentContext) -> List[Dict[str, Any]]:
        """Generate climate adaptation scenarios"""
        scenarios = []
        
        for neighborhood in context.neighborhoods:
            scenario = {
                "neighborhood": neighborhood,
                "type": "climate_adaptation",
                "description": f"Climate resilience measures for {neighborhood}",
                "parameters": {
                    "flood_protection": "elevated development" if neighborhood == "Marina" else "drainage improvements",
                    "heat_mitigation": "green infrastructure",
                    "community_resilience": "emergency preparedness hubs"
                },
                "feasibility": "high"
            }
            scenarios.append(scenario)
        
        return scenarios
    
    async def _transportation_scenarios(self, context: AgentContext) -> List[Dict[str, Any]]:
        """Generate detailed transportation scenarios with traffic analysis"""
        scenarios = []
        query_lower = context.query.lower()
        
        # Detect specific transportation impacts
        is_car_increase = any(word in query_lower for word in ["cars", "vehicles", "traffic"]) and any(word in query_lower for word in ["increase", "more", "additional", "%"])
        is_parking_query = "parking" in query_lower
        is_congestion_query = "congestion" in query_lower
        
        for neighborhood in context.neighborhoods:
            if is_car_increase:
                scenario = await self._generate_traffic_impact_scenario(neighborhood, context)
            elif is_parking_query:
                scenario = await self._generate_parking_scenario(neighborhood, context)
            elif is_congestion_query:
                scenario = await self._generate_congestion_scenario(neighborhood, context)
            else:
                scenario = await self._generate_general_mobility_scenario(neighborhood, context)
            
            scenarios.append(scenario)
        
        return scenarios
    
    async def _generate_traffic_impact_scenario(self, neighborhood: str, context: AgentContext) -> Dict[str, Any]:
        """Generate detailed traffic impact analysis"""
        # Extract percentage if mentioned
        query_lower = context.query.lower()
        percentage = 10  # Default
        if "%" in query_lower:
            import re
            match = re.search(r'(\d+)%', query_lower)
            if match:
                percentage = int(match.group(1))
        
        # Neighborhood-specific traffic data
        traffic_data = {
            "Marina": {
                "current_daily_vehicles": 15000,
                "parking_spaces": 2800,
                "peak_congestion_points": ["Marina Blvd/Fillmore", "Lombard/Broderick"],
                "access_routes": ["Marina Blvd", "Lombard St", "Union St"],
                "constraints": ["Limited peninsula access", "Tourist traffic", "Event parking (Marina Green)"],
                "environmental_factors": ["Waterfront air quality", "Residential noise sensitivity"]
            },
            "Mission": {
                "current_daily_vehicles": 25000,
                "parking_spaces": 1800,
                "peak_congestion_points": ["Mission/16th", "Mission/24th", "Valencia/16th"],
                "access_routes": ["Mission St", "Valencia St", "16th St", "24th St"],
                "constraints": ["Dense street grid", "Limited parking", "Heavy transit use"],
                "environmental_factors": ["Air quality in corridor", "Pedestrian safety"]
            },
            "Hayes Valley": {
                "current_daily_vehicles": 12000,
                "parking_spaces": 1200,
                "peak_congestion_points": ["Market/Gough", "Fell/Octavia"],
                "access_routes": ["Market St", "Fell St", "Oak St", "Hayes St"],
                "constraints": ["Transit-first policy", "Limited street parking", "Event traffic (venues)"],
                "environmental_factors": ["Central location air quality", "Mixed-use noise levels"]
            }
        }
        
        data = traffic_data.get(neighborhood, traffic_data["Mission"])
        
        # Calculate impacts
        additional_vehicles = int(data["current_daily_vehicles"] * (percentage / 100))
        current_parking = data["parking_spaces"]
        additional_parking_needed = int(additional_vehicles * 0.6)  # Assume 60% need parking
        parking_deficit = max(0, additional_parking_needed - (current_parking * 0.1))  # 10% current availability
        
        scenario = {
            "neighborhood": neighborhood,
            "type": "traffic_impact_analysis",
            "description": f"{percentage}% increase in vehicle traffic analysis for {neighborhood}",
            "quantitative_impacts": {
                "additional_daily_vehicles": additional_vehicles,
                "new_daily_total": data["current_daily_vehicles"] + additional_vehicles,
                "additional_parking_demand": additional_parking_needed,
                "parking_deficit": parking_deficit,
                "congestion_increase": f"{percentage * 1.5:.1f}%" if neighborhood == "Marina" else f"{percentage * 1.2:.1f}%"
            },
            "specific_impacts": {
                "congestion_points": data["peak_congestion_points"],
                "capacity_strain": data["access_routes"][:2],  # Most impacted routes
                "parking_pressure": f"Need {additional_parking_needed} additional spaces, deficit of {parking_deficit}",
                "environmental": f"Air quality: +{percentage * 0.8:.1f}% emissions, Noise: +{percentage * 0.6:.1f}% peak levels"
            },
            "neighborhood_constraints": data["constraints"],
            "mitigation_strategies": self._get_traffic_mitigation_strategies(neighborhood, percentage),
            "timeline_impacts": {
                "immediate": "Increased congestion during peak hours",
                "short_term": "Parking availability decreases, local air quality impacts",
                "long_term": "Infrastructure wear, potential resident displacement due to noise/pollution"
            },
            "feasibility": "concerning" if parking_deficit > 200 else "manageable"
        }
        
        return scenario
    
    def _get_traffic_mitigation_strategies(self, neighborhood: str, percentage: int) -> List[str]:
        """Get neighborhood-specific traffic mitigation strategies"""
        base_strategies = [
            "Implement dynamic parking pricing",
            "Expand car-sharing programs",
            "Improve alternative transportation incentives"
        ]
        
        if neighborhood == "Marina":
            return base_strategies + [
                "Shuttle service to Union Square/downtown",
                "Park-and-ride facility outside neighborhood",
                "Time-restricted access during events",
                "Enhanced bike path to Presidio/Crissy Field"
            ]
        elif neighborhood == "Mission":
            return base_strategies + [
                "Expand BART/Muni capacity",
                "Protected bike lanes on Mission/Valencia",
                "Pedestrian-only zones during peak hours",
                "Residential parking permits"
            ]
        else:  # Hayes Valley
            return base_strategies + [
                "Leverage existing excellent transit",
                "Bike-share station expansion",
                "Event coordination with venues",
                "Smart traffic signals"
            ]
    
    async def _generate_parking_scenario(self, neighborhood: str, context: AgentContext) -> Dict[str, Any]:
        """Generate parking-specific analysis"""
        return {
            "neighborhood": neighborhood,
            "type": "parking_analysis",
            "description": f"Parking capacity and management analysis for {neighborhood}",
            "feasibility": "high"
        }
    
    async def _generate_congestion_scenario(self, neighborhood: str, context: AgentContext) -> Dict[str, Any]:
        """Generate congestion-specific analysis"""
        return {
            "neighborhood": neighborhood,
            "type": "congestion_analysis", 
            "description": f"Traffic congestion impact analysis for {neighborhood}",
            "feasibility": "high"
        }
    
    async def _generate_general_mobility_scenario(self, neighborhood: str, context: AgentContext) -> Dict[str, Any]:
        """Generate general mobility analysis"""
        return {
            "neighborhood": neighborhood,
            "type": "mobility_enhancement",
            "description": f"General transportation improvements for {neighborhood}",
            "feasibility": "high"
        }
    
    async def _general_scenarios(self, context: AgentContext) -> List[Dict[str, Any]]:
        """Generate general planning scenarios"""
        return [{
            "neighborhood": neighborhood,
            "type": "general_improvement",
            "description": f"Comprehensive neighborhood improvements for {neighborhood}",
            "parameters": {"approach": "community-driven planning"},
            "feasibility": "medium"
        } for neighborhood in context.neighborhoods]
    
    async def _validate_scenarios(self, context: AgentContext):
        """Validate scenarios using neighborhood APIs"""
        scenarios = context.data.get("scenarios", [])
        
        for scenario in scenarios:
            if scenario["type"] == "housing_development":
                self.log(f"Validating housing scenario for {scenario['neighborhood']}...")
                
                # Call validation API
                validation_data = {
                    "far": 2.5,
                    "height_ft": 45,
                    "lot_area_sf": 3000,
                    "num_units": scenario["parameters"]["units"]
                }
                
                neighborhood_key = scenario["neighborhood"].lower().replace(" ", "_")
                result = await self.tools[0].call_api(
                    f"neighborhoods/{neighborhood_key}/validate-proposal",
                    method="POST",
                    data=validation_data
                )
                
                if "error" not in result:
                    scenario["validation"] = result
                    scenario["feasibility"] = "validated"
                    self.log(f"✓ Scenario validated for {scenario['neighborhood']}")
                else:
                    scenario["feasibility"] = "needs_revision"
                    self.log(f"⚠ Validation issues for {scenario['neighborhood']}")

class EvaluatorAgent(BaseAgent):
    """Agent 3: Assesses impacts and generates insights"""
    
    def __init__(self):
        super().__init__("Evaluator", "Impact Assessment & Insights")
    
    async def execute(self, context: AgentContext) -> AgentContext:
        """Evaluate scenarios and generate comprehensive insights"""
        self.log("Evaluating scenario impacts and generating insights")
        
        # Assess impacts for each scenario
        await self._assess_impacts(context)
        
        # Generate comparative insights
        await self._generate_comparative_insights(context)
        
        # Generate follow-up questions
        context.data["follow_up_questions"] = self._generate_follow_up_questions(context)
        
        # Final confidence assessment
        context.confidence = self._update_confidence(context)
        
        context.reasoning.extend(self.execution_log)
        return context
    
    async def _assess_impacts(self, context: AgentContext):
        """Assess impacts for each scenario"""
        scenarios = context.data.get("scenarios", [])
        
        for scenario in scenarios:
            self.log(f"Assessing impacts for {scenario['neighborhood']} {scenario['type']}")
            
            impacts = {
                "economic": self._assess_economic_impact(scenario, context),
                "social": self._assess_social_impact(scenario, context),
                "environmental": self._assess_environmental_impact(scenario, context)
            }
            
            scenario["impacts"] = impacts
            self.log(f"✓ Impact assessment completed for {scenario['neighborhood']}")
    
    def _assess_economic_impact(self, scenario: Dict, context: AgentContext) -> Dict[str, str]:
        """Assess economic impacts"""
        neighborhood = scenario["neighborhood"]
        
        if scenario["type"] == "housing_development":
            return {
                "description": f"Housing development in {neighborhood} would create construction jobs and increase property tax revenue",
                "magnitude": "medium_positive",
                "confidence": "high"
            }
        elif scenario["type"] == "transportation_improvement":
            return {
                "description": f"Transportation improvements in {neighborhood} would increase property values and business accessibility",
                "magnitude": "medium_positive", 
                "confidence": "high"
            }
        else:
            return {
                "description": f"Economic impact varies by specific implementation in {neighborhood}",
                "magnitude": "neutral_to_positive",
                "confidence": "medium"
            }
    
    def _assess_social_impact(self, scenario: Dict, context: AgentContext) -> Dict[str, str]:
        """Assess social/equity impacts"""
        neighborhood = scenario["neighborhood"]
        
        if neighborhood == "Mission" and scenario["type"] == "housing_development":
            return {
                "description": "High displacement risk but also addresses housing shortage for existing community",
                "magnitude": "mixed",
                "confidence": "high"
            }
        elif neighborhood == "Marina":
            return {
                "description": "Lower displacement risk due to existing affluence, but may increase exclusivity",
                "magnitude": "low_negative",
                "confidence": "medium"
            }
        else:
            return {
                "description": f"Social impacts depend on community engagement and implementation approach",
                "magnitude": "neutral",
                "confidence": "medium"
            }
    
    def _assess_environmental_impact(self, scenario: Dict, context: AgentContext) -> Dict[str, str]:
        """Assess environmental impacts"""
        if scenario["type"] == "climate_adaptation":
            return {
                "description": "Direct positive environmental impact through resilience measures",
                "magnitude": "high_positive",
                "confidence": "high"
            }
        elif scenario["type"] == "transportation_improvement":
            return {
                "description": "Reduced car dependency and emissions through improved mobility options",
                "magnitude": "medium_positive",
                "confidence": "high"
            }
        else:
            return {
                "description": "Environmental impact depends on green building standards and implementation",
                "magnitude": "neutral_to_positive",
                "confidence": "medium"
            }
    
    async def _generate_comparative_insights(self, context: AgentContext):
        """Generate insights comparing different neighborhoods"""
        if len(context.neighborhoods) > 1:
            self.log("Generating comparative insights across neighborhoods")
            
            insights = {
                "neighborhood_differences": [],
                "implementation_priorities": [],
                "equity_considerations": []
            }
            
            # Compare neighborhood characteristics
            for neighborhood in context.neighborhoods:
                neighborhood_data = context.data.get(neighborhood, {})
                characteristics = neighborhood_data.get("characteristics", {})
                
                insights["neighborhood_differences"].append({
                    "neighborhood": neighborhood,
                    "key_characteristics": characteristics,
                    "planning_approach": self._recommend_approach(neighborhood, characteristics)
                })
            
            context.data["comparative_insights"] = insights
    
    def _recommend_approach(self, neighborhood: str, characteristics: Dict) -> str:
        """Recommend planning approach based on characteristics"""
        if characteristics.get("character") == "diverse" and characteristics.get("density") == "high":
            return "Community-controlled development with strong anti-displacement measures"
        elif characteristics.get("character") == "affluent" and characteristics.get("density") == "low":
            return "Climate resilience focus with managed density increases"
        elif characteristics.get("character") == "gentrifying":
            return "Balanced growth with inclusionary housing requirements"
        else:
            return "Context-specific community engagement and planning"
    
    def _generate_follow_up_questions(self, context: AgentContext) -> List[str]:
        """Generate relevant follow-up questions"""
        questions = []
        
        if context.primary_domain == "housing":
            questions.extend([
                "What specific community benefits should be included?",
                "How can displacement be prevented during construction?",
                "What financing mechanisms would support affordability?"
            ])
        elif context.primary_domain == "climate":
            questions.extend([
                "How would extreme weather events affect implementation?",
                "What community preparedness measures are needed?",
                "How do we ensure equitable access to resilience measures?"
            ])
        elif context.primary_domain == "transportation":
            questions.extend([
                "How would changes affect local businesses?",
                "What safety measures are needed for new infrastructure?",
                "How do we ensure accessibility for all mobility levels?"
            ])
        
        return questions
    
    def _update_confidence(self, context: AgentContext) -> float:
        """Update overall confidence based on complete analysis"""
        scenarios = context.data.get("scenarios", [])
        validated_scenarios = [s for s in scenarios if s.get("feasibility") == "validated"]
        
        if not scenarios:
            return 0.3
        
        validation_score = len(validated_scenarios) / len(scenarios)
        data_completeness = 0.9 if context.data else 0.5
        
        return min(0.95, (context.confidence * 0.4 + validation_score * 0.4 + data_completeness * 0.2))

# Main orchestrator
class LightweightAgentCrew:
    """Orchestrates the 3-agent workflow"""
    
    def __init__(self):
        self.agents = [
            InterpreterAgent(),
            PlannerAgent(), 
            EvaluatorAgent()
        ]
    
    async def execute(self, query: str) -> AgentContext:
        """Execute the full 3-agent workflow"""
        context = AgentContext(query=query)
        
        print(f"\n🚀 Starting agent crew analysis for: '{query}'")
        print("=" * 60)
        
        # Execute agents sequentially
        for agent in self.agents:
            print(f"\n🤖 Executing {agent.name} ({agent.role})")
            print("-" * 40)
            context = await agent.execute(context)
            await asyncio.sleep(0.5)  # Brief pause between agents
        
        print("\n✅ Agent crew analysis complete!")
        print("=" * 60)
        
        return context