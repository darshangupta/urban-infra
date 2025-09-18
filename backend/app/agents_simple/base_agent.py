"""
Lightweight Agent System for Urban Planning
No heavy dependencies - just asyncio and httpx
"""

import asyncio
import httpx
import json
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod
from enum import Enum
import time

class QueryType(Enum):
    """Types of urban planning queries"""
    ANALYTICAL = "analytical"  # "How does X affect Y?"
    COMPARATIVE = "comparative"  # "X vs Y"
    SCENARIO_PLANNING = "scenario_planning"  # "What if...?"
    SOLUTION_SEEKING = "solution_seeking"  # "How can we...?"

class QueryDomain(Enum):
    """Primary domains for urban planning analysis"""
    TRANSPORTATION = "transportation"
    HOUSING = "housing" 
    CLIMATE = "climate"
    ECONOMICS = "economics"
    GENERAL = "general"

class QueryIntent(Enum):
    """Specific intent classifications"""
    IMPACT_ANALYSIS = "impact_analysis"
    COMPARISON = "comparison"
    PLANNING = "planning"
    RESEARCH = "research"

@dataclass
class QueryClassification:
    """Structured classification result from Interpreter Agent"""
    query_type: QueryType
    primary_domain: QueryDomain
    intent: QueryIntent
    neighborhoods: List[str]
    parameters: Dict[str, Any]  # Numbers, percentages, specific entities
    confidence: float
    comparative: bool = False  # Multiple neighborhoods detected
    
@dataclass 
class AgentContext:
    """Enhanced shared context between agents"""
    query: str
    classification: Optional[QueryClassification] = None
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
    """Enhanced Agent 1: Intelligent query classification and context gathering"""
    
    def __init__(self):
        super().__init__("Interpreter", "Intelligent Query Classification & Context Gathering")
    
    async def execute(self, context: AgentContext) -> AgentContext:
        """Intelligently analyze and classify query"""
        self.log(f"🧠 Analyzing query: '{context.query}'")
        
        # GUARDRAIL: Validate query first
        if not self._is_valid_urban_planning_query(context.query):
            context.confidence = 0.1
            context.neighborhoods = []  # No fallback - be explicit about unknown
            context.primary_domain = "general"
            context.data["validation_error"] = "Query does not appear to be related to urban planning"
            self.log("❌ Query validation failed - not urban planning related")
            context.reasoning.extend(self.execution_log)
            return context
        
        # Step 1: Intelligent classification
        classification = self._classify_query(context.query)
        context.classification = classification
        context.neighborhoods = classification.neighborhoods
        context.primary_domain = classification.primary_domain.value
        self.log(f"🎯 Classification: {classification.query_type.value} | {classification.primary_domain.value}")
        self.log(f"🏘️ Neighborhoods: {classification.neighborhoods}")
        self.log(f"📊 Parameters: {classification.parameters}")
        
        # Step 2: Gather neighborhood data (only if neighborhoods detected)
        if classification.neighborhoods:
            await self._gather_neighborhood_data(context)
        else:
            self.log("⚠️ No specific neighborhoods detected - skipping data gathering")
        
        # Step 3: Set confidence based on classification quality
        context.confidence = classification.confidence
        self.log(f"🎲 Classification confidence: {context.confidence:.2f}")
        
        context.reasoning.extend(self.execution_log)
        return context
    
    def _classify_query(self, query: str) -> QueryClassification:
        """Intelligently classify the query using contextual analysis"""
        query_lower = query.lower()
        
        # Extract neighborhoods with context awareness
        neighborhoods = self._extract_neighborhoods_intelligent(query_lower)
        
        # Determine query type based on structure and intent
        query_type = self._determine_query_type(query_lower)
        
        # Classify domain with context
        domain = self._classify_domain_intelligent(query_lower)
        
        # Extract parameters (numbers, percentages, etc.)
        parameters = self._extract_parameters(query_lower)
        
        # Determine intent
        intent = self._determine_intent(query_lower, query_type)
        
        # Calculate confidence based on multiple factors
        confidence = self._calculate_classification_confidence(
            query_lower, neighborhoods, query_type, domain, parameters
        )
        
        return QueryClassification(
            query_type=query_type,
            primary_domain=domain,
            intent=intent,
            neighborhoods=neighborhoods,
            parameters=parameters,
            confidence=confidence,
            comparative=len(neighborhoods) > 1 or "vs" in query_lower or "versus" in query_lower
        )
    
    def _extract_neighborhoods_intelligent(self, query_lower: str) -> List[str]:
        """Intelligent neighborhood extraction with context clues"""
        neighborhoods = []
        
        # Direct neighborhood name matching
        neighborhood_patterns = {
            "mission": ["Mission", "Mission District", "Mission Bay"],
            "marina": ["Marina", "Marina District"], 
            "hayes": ["Hayes Valley", "Hayes"],
            "castro": ["Castro", "Castro District"],
            "nob hill": ["Nob Hill"],
            "soma": ["SOMA", "South of Market"],
            "richmond": ["Richmond", "Richmond District"],
            "sunset": ["Sunset", "Sunset District"]
        }
        
        for pattern, names in neighborhood_patterns.items():
            if pattern in query_lower:
                neighborhoods.extend(names[:1])  # Take first name only
        
        # Context clues and landmarks
        landmark_mapping = {
            "bart": ["Mission", "Hayes Valley"],  # BART accessible neighborhoods
            "palace of fine arts": ["Marina"],
            "mission dolores": ["Mission"],
            "fillmore": ["Marina"],
            "valencia": ["Mission"],
            "chestnut": ["Marina"],
            "union square": ["Hayes Valley"],  # Transit accessible
            "crissy field": ["Marina"],
            "dolores park": ["Mission"]
        }
        
        for landmark, related_neighborhoods in landmark_mapping.items():
            if landmark in query_lower and not neighborhoods:
                neighborhoods.extend(related_neighborhoods[:1])
                break
        
        # Remove duplicates while preserving order
        unique_neighborhoods = []
        for n in neighborhoods:
            if n not in unique_neighborhoods:
                unique_neighborhoods.append(n)
        
        return unique_neighborhoods
    
    def _determine_query_type(self, query_lower: str) -> QueryType:
        """Determine the type of query based on structure"""
        if any(phrase in query_lower for phrase in ["what if", "if we", "suppose", "imagine"]):
            return QueryType.SCENARIO_PLANNING
        elif any(phrase in query_lower for phrase in [" vs ", " versus ", "compare", "difference between"]):
            return QueryType.COMPARATIVE
        elif any(phrase in query_lower for phrase in ["how can", "how to", "how should", "what should"]):
            return QueryType.SOLUTION_SEEKING
        else:
            return QueryType.ANALYTICAL
    
    def _classify_domain_intelligent(self, query_lower: str) -> QueryDomain:
        """Intelligent domain classification with context"""
        domain_indicators = {
            QueryDomain.TRANSPORTATION: [
                "bike", "transit", "transport", "walkable", "cars", "traffic", 
                "vehicles", "parking", "congestion", "mobility", "commute", "driving",
                "bus", "bart", "muni", "subway", "bicycle", "pedestrian", "road"
            ],
            QueryDomain.HOUSING: [
                "housing", "units", "development", "density", "affordable", 
                "residential", "apartments", "condos", "homes", "rent", "displacement"
            ],
            QueryDomain.CLIMATE: [
                "climate", "temperature", "flood", "environment", "sea level",
                "weather", "degrees", "warming", "cooling", "storm", "rain"
            ],
            QueryDomain.ECONOMICS: [
                "business", "economic", "revenue", "jobs", "cost", "price",
                "commercial", "retail", "economy", "income", "tax", "value"
            ]
        }
        
        domain_scores = {}
        for domain, keywords in domain_indicators.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                domain_scores[domain] = score
        
        if domain_scores:
            return max(domain_scores.items(), key=lambda x: x[1])[0]
        else:
            return QueryDomain.GENERAL
    
    def _extract_parameters(self, query_lower: str) -> Dict[str, Any]:
        """Extract numerical parameters, percentages, and entities"""
        parameters = {}
        
        # Extract percentages
        percentage_matches = re.findall(r'(\d+(?:\.\d+)?)%', query_lower)
        if percentage_matches:
            parameters["percentages"] = [float(p) for p in percentage_matches]
        
        # Extract numbers with context
        number_matches = re.findall(r'(\d+(?:\.\d+)?)\s*(degrees?|units?|dollars?|years?|percent)', query_lower)
        for value, unit in number_matches:
            parameters[f"value_{unit}"] = float(value)
        
        # Extract time periods
        time_patterns = ["years?", "months?", "decades?", "by \d+"]
        for pattern in time_patterns:
            matches = re.findall(pattern, query_lower)
            if matches:
                parameters["time_period"] = matches[0]
        
        return parameters
    
    def _determine_intent(self, query_lower: str, query_type: QueryType) -> QueryIntent:
        """Determine specific intent based on query type and content"""
        if query_type == QueryType.COMPARATIVE:
            return QueryIntent.COMPARISON
        elif query_type == QueryType.SCENARIO_PLANNING:
            return QueryIntent.PLANNING
        elif any(word in query_lower for word in ["impact", "affect", "effect", "influence"]):
            return QueryIntent.IMPACT_ANALYSIS
        else:
            return QueryIntent.RESEARCH
    
    def _calculate_classification_confidence(
        self, query_lower: str, neighborhoods: List[str], 
        query_type: QueryType, domain: QueryDomain, parameters: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for classification"""
        confidence = 0.0
        
        # Base confidence for having neighborhoods
        if neighborhoods:
            confidence += 0.4
        
        # Confidence for clear domain classification
        if domain != QueryDomain.GENERAL:
            confidence += 0.3
        
        # Confidence for clear query structure
        query_structure_indicators = ["what if", "how would", "compare", "vs", "affect"]
        if any(indicator in query_lower for indicator in query_structure_indicators):
            confidence += 0.2
        
        # Confidence for having parameters
        if parameters:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
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
    """Enhanced Agent 2: Template-driven scenario generation"""
    
    def __init__(self):
        super().__init__("Planner", "Template-Driven Analysis Generation")
    
    async def execute(self, context: AgentContext) -> AgentContext:
        """Generate template-driven analysis based on classification"""
        classification = context.classification
        if not classification:
            self.log("❌ No classification found - cannot generate analysis")
            return context
            
        self.log(f"🎯 Generating analysis for {classification.query_type.value} | {classification.primary_domain.value}")
        
        # Handle empty neighborhoods gracefully
        if not classification.neighborhoods:
            self.log("⚠️ No specific neighborhoods detected - generating general analysis")
            analysis = await self._generate_general_analysis(context)
        else:
            # Generate template-driven analysis
            analysis = await self._generate_template_analysis(context)
        
        context.data["template_analysis"] = analysis
        self.log(f"✅ Generated {len(analysis.get('scenarios', []))} scenarios")
        
        context.reasoning.extend(self.execution_log)
        return context
    
    async def _generate_template_analysis(self, context: AgentContext) -> Dict[str, Any]:
        """Generate template-driven analysis based on classification"""
        classification = context.classification
        
        # Select template based on domain and query type
        template = self._select_analysis_template(classification)
        
        # Generate scenarios for each neighborhood
        scenarios = []
        for neighborhood in classification.neighborhoods:
            scenario = await self._generate_neighborhood_scenario(
                neighborhood, classification, template, context
            )
            scenarios.append(scenario)
        
        # Generate comparative analysis if multiple neighborhoods
        comparative_analysis = {}
        if classification.comparative and len(classification.neighborhoods) > 1:
            comparative_analysis = self._generate_comparative_analysis(
                classification.neighborhoods, classification, context
            )
        
        return {
            "template_type": template["name"],
            "scenarios": scenarios,
            "comparative_analysis": comparative_analysis,
            "implementation_timeline": self._generate_implementation_timeline(classification),
            "confidence": classification.confidence
        }
    
    async def _generate_general_analysis(self, context: AgentContext) -> Dict[str, Any]:
        """Generate general analysis when no specific neighborhoods detected"""
        classification = context.classification
        
        return {
            "template_type": "general_planning",
            "scenarios": [{
                "type": "general_recommendation",
                "description": f"General {classification.primary_domain.value} planning recommendations",
                "scope": "citywide",
                "considerations": [
                    "Requires neighborhood-specific analysis",
                    "Consider local context and constraints",
                    "Engage community stakeholders"
                ]
            }],
            "comparative_analysis": {},
            "implementation_timeline": {"immediate": "Conduct neighborhood-specific assessment"},
            "confidence": 0.3  # Low confidence for general analysis
        }
    
    def _select_analysis_template(self, classification: QueryClassification) -> Dict[str, Any]:
        """Select appropriate analysis template"""
        templates = {
            ("transportation", "comparative"): {
                "name": "transportation_comparative",
                "focus": "mobility_impact_comparison",
                "metrics": ["accessibility", "congestion", "business_impact"],
                "scenarios": ["current_state", "proposed_changes", "alternatives"]
            },
            ("transportation", "scenario_planning"): {
                "name": "transportation_scenario",
                "focus": "traffic_impact_analysis", 
                "metrics": ["vehicle_counts", "parking_demand", "air_quality"],
                "scenarios": ["baseline", "implementation", "long_term"]
            },
            ("housing", "comparative"): {
                "name": "housing_comparative",
                "focus": "development_impact_comparison",
                "metrics": ["displacement_risk", "affordability", "density"],
                "scenarios": ["current_housing", "proposed_development", "alternatives"]
            },
            ("climate", "scenario_planning"): {
                "name": "climate_scenario",
                "focus": "environmental_impact_analysis",
                "metrics": ["temperature_effects", "vulnerability", "adaptation"],
                "scenarios": ["current_climate", "projected_changes", "mitigation"]
            }
        }
        
        key = (classification.primary_domain.value, classification.query_type.value)
        return templates.get(key, {
            "name": "general_analysis",
            "focus": "multi_factor_assessment",
            "metrics": ["impact", "feasibility", "community_benefit"],
            "scenarios": ["current", "proposed", "alternative"]
        })
    
    async def _generate_neighborhood_scenario(
        self, neighborhood: str, classification: QueryClassification, 
        template: Dict[str, Any], context: AgentContext
    ) -> Dict[str, Any]:
        """Generate scenario for specific neighborhood"""
        
        # Get neighborhood characteristics from context
        neighborhood_data = context.data.get(neighborhood, {})
        characteristics = neighborhood_data.get("characteristics", {})
        
        # Generate scenario based on template and neighborhood
        scenario = {
            "neighborhood": neighborhood,
            "template": template["name"],
            "analysis_type": template["focus"],
            "current_conditions": self._get_current_conditions(neighborhood, classification),
            "projected_impacts": self._calculate_projected_impacts(
                neighborhood, classification, template
            ),
            "implementation_considerations": self._get_implementation_considerations(
                neighborhood, classification
            ),
            "metrics": self._generate_neighborhood_metrics(neighborhood, template, classification)
        }
        
        self.log(f"📋 Generated {template['name']} scenario for {neighborhood}")
        return scenario
    
    def _get_current_conditions(self, neighborhood: str, classification: QueryClassification) -> Dict[str, Any]:
        """Get baseline conditions for neighborhood"""
        baseline_data = {
            "Marina": {
                "transportation": {"car_dependency": "high", "transit_access": "limited", "walkability": "medium"},
                "housing": {"density": "low", "affordability": "low", "character": "single_family"},
                "climate": {"flood_risk": "high", "heat_vulnerability": "low", "air_quality": "good"}
            },
            "Mission": {
                "transportation": {"car_dependency": "medium", "transit_access": "excellent", "walkability": "high"},
                "housing": {"density": "high", "affordability": "medium", "character": "mixed_use"},
                "climate": {"flood_risk": "low", "heat_vulnerability": "medium", "air_quality": "moderate"}
            },
            "Hayes Valley": {
                "transportation": {"car_dependency": "low", "transit_access": "excellent", "walkability": "high"},
                "housing": {"density": "medium", "affordability": "low", "character": "transit_oriented"},
                "climate": {"flood_risk": "low", "heat_vulnerability": "low", "air_quality": "good"}
            }
        }
        
        return baseline_data.get(neighborhood, {}).get(classification.primary_domain.value, {})
    
    def _calculate_projected_impacts(
        self, neighborhood: str, classification: QueryClassification, template: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate projected impacts based on template and parameters"""
        impacts = {}
        
        # Extract parameters from classification
        parameters = classification.parameters
        
        if classification.primary_domain == QueryDomain.TRANSPORTATION:
            if "percentages" in parameters:
                percentage = parameters["percentages"][0]
                impacts = {
                    "traffic_change": f"+{percentage}%",
                    "parking_demand": f"+{percentage * 0.6:.1f}%",
                    "air_quality": f"+{percentage * 0.8:.1f}% emissions"
                }
        
        elif classification.primary_domain == QueryDomain.CLIMATE:
            if "value_degrees" in parameters:
                degrees = parameters["value_degrees"]
                impacts = {
                    "temperature_change": f"{degrees:.1f}°F",
                    "energy_demand": f"+{degrees * 3:.1f}% heating",
                    "infrastructure_stress": "medium" if degrees < 15 else "high"
                }
        
        return impacts
    
    def _get_implementation_considerations(self, neighborhood: str, classification: QueryClassification) -> List[str]:
        """Get neighborhood-specific implementation considerations"""
        considerations = {
            "Marina": [
                "Limited public transit access",
                "Flood zone constraints",
                "Community resistance to density",
                "Parking availability challenges"
            ],
            "Mission": [
                "Displacement risk management",
                "Cultural preservation requirements", 
                "Existing transit infrastructure",
                "Community engagement protocols"
            ],
            "Hayes Valley": [
                "Transit-first policy compliance",
                "Event coordination requirements",
                "Mixed-use development standards",
                "Walkability enhancement opportunities"
            ]
        }
        
        return considerations.get(neighborhood, ["General urban planning considerations"])
    
    def _generate_neighborhood_metrics(
        self, neighborhood: str, template: Dict[str, Any], classification: QueryClassification
    ) -> Dict[str, Any]:
        """Generate quantitative metrics for scenario"""
        base_metrics = {
            "confidence": classification.confidence,
            "complexity": "medium",
            "timeline": "2-5 years",
            "cost_estimate": "moderate"
        }
        
        # Add template-specific metrics
        for metric in template.get("metrics", []):
            if metric == "accessibility":
                base_metrics["accessibility_score"] = 0.8 if neighborhood == "Hayes Valley" else 0.6
            elif metric == "displacement_risk":
                base_metrics["displacement_risk"] = 0.7 if neighborhood == "Mission" else 0.3
        
        return base_metrics
    
    def _generate_comparative_analysis(
        self, neighborhoods: List[str], classification: QueryClassification, context: AgentContext
    ) -> Dict[str, Any]:
        """Generate cross-neighborhood comparative analysis"""
        return {
            "comparison_type": "multi_neighborhood",
            "key_differences": [
                f"Transit access varies: {', '.join(neighborhoods)}",
                f"Different community characteristics across neighborhoods",
                f"Varying implementation complexity by area"
            ],
            "coordination_opportunities": [
                "Shared infrastructure investments",
                "Policy consistency across neighborhoods",
                "Cross-neighborhood pilot programs"
            ],
            "priority_ranking": neighborhoods,  # Could be more sophisticated
            "synergy_potential": "medium"
        }
    
    def _generate_implementation_timeline(self, classification: QueryClassification) -> Dict[str, str]:
        """Generate implementation timeline based on classification"""
        if classification.query_type == QueryType.SCENARIO_PLANNING:
            return {
                "immediate": "Feasibility assessment and community engagement",
                "short_term": "Pilot program implementation (6-18 months)",
                "medium_term": "Full implementation and monitoring (2-5 years)",
                "long_term": "Evaluation and iteration (5+ years)"
            }
        else:
            return {
                "immediate": "Detailed analysis and stakeholder consultation",
                "short_term": "Policy development and approval process",
                "medium_term": "Implementation and early monitoring",
                "long_term": "Long-term impact assessment"
            }
    
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
        """Evaluate template analysis and generate comprehensive insights"""
        classification = context.classification
        if not classification:
            self.log("❌ No classification found - cannot evaluate analysis")
            return context
            
        self.log(f"🎯 Evaluating {classification.query_type.value} analysis for {len(classification.neighborhoods)} neighborhoods")
        
        # Get template analysis from PlannerAgent
        template_analysis = context.data.get("template_analysis", {})
        if not template_analysis:
            self.log("⚠️ No template analysis found - using fallback scenarios")
            await self._assess_impacts(context)  # Fallback for old scenarios
        else:
            # Enhanced evaluation using template analysis
            await self._evaluate_template_analysis(context, template_analysis)
        
        # Generate comparative insights
        await self._generate_comparative_insights(context)
        
        # Generate KPI dashboard
        context.data["kpi_dashboard"] = self._generate_kpi_dashboard(context, template_analysis)
        
        # Generate follow-up questions
        context.data["follow_up_questions"] = self._generate_follow_up_questions(context)
        
        # Final confidence assessment
        context.confidence = self._update_confidence(context)
        
        self.log(f"✅ Impact evaluation completed with confidence: {context.confidence:.1f}")
        context.reasoning.extend(self.execution_log)
        return context
    
    async def _evaluate_template_analysis(self, context: AgentContext, template_analysis: Dict[str, Any]):
        """Enhanced evaluation using template analysis from PlannerAgent"""
        template_type = template_analysis.get("template_type", "unknown")
        scenarios = template_analysis.get("scenarios", [])
        comparative_analysis = template_analysis.get("comparative_analysis", {})
        
        self.log(f"📊 Evaluating {template_type} template with {len(scenarios)} scenarios")
        
        # Enhanced impact assessment for each scenario
        evaluated_scenarios = []
        for scenario in scenarios:
            evaluated_scenario = await self._deep_impact_assessment(scenario, context, template_type)
            evaluated_scenarios.append(evaluated_scenario)
            self.log(f"✓ Deep impact assessment completed for {scenario.get('neighborhood', 'unknown')}")
        
        # Store enhanced scenarios
        context.data["evaluated_scenarios"] = evaluated_scenarios
        
        # Evaluate comparative analysis if present
        if comparative_analysis and len(scenarios) > 1:
            context.data["comparative_evaluation"] = self._evaluate_comparative_analysis(
                comparative_analysis, evaluated_scenarios, context
            )
    
    async def _deep_impact_assessment(self, scenario: Dict[str, Any], context: AgentContext, template_type: str) -> Dict[str, Any]:
        """Perform deep impact assessment on template-generated scenario"""
        neighborhood = scenario.get("neighborhood", "unknown")
        analysis_type = scenario.get("analysis_type", "unknown")
        
        # Extract key components for evaluation
        current_conditions = scenario.get("current_conditions", {})
        projected_impacts = scenario.get("projected_impacts", {})
        implementation_considerations = scenario.get("implementation_considerations", [])
        metrics = scenario.get("metrics", {})
        
        # Enhanced impact assessment
        enhanced_impacts = {
            "before_after_analysis": self._calculate_before_after_metrics(
                current_conditions, projected_impacts, neighborhood
            ),
            "implementation_complexity": self._assess_implementation_complexity(
                implementation_considerations, neighborhood
            ),
            "equity_assessment": self._assess_equity_implications(
                scenario, neighborhood, context.classification
            ),
            "uncertainty_factors": self._identify_uncertainty_factors(
                scenario, template_type, neighborhood
            ),
            "success_indicators": self._define_success_indicators(
                analysis_type, neighborhood, projected_impacts
            )
        }
        
        # Combine original scenario with enhanced evaluation
        evaluated_scenario = {
            **scenario,
            "enhanced_impacts": enhanced_impacts,
            "evaluation_confidence": metrics.get("confidence", 0.7),
            "evaluation_timestamp": "template_analysis_based"
        }
        
        return evaluated_scenario
    
    def _calculate_before_after_metrics(self, current: Dict, projected: Dict, neighborhood: str) -> Dict[str, Any]:
        """Calculate quantitative before/after metrics"""
        metrics = {
            "baseline_metrics": current,
            "projected_metrics": projected,
            "change_indicators": {}
        }
        
        # Calculate specific changes based on available data
        if "traffic_change" in projected:
            metrics["change_indicators"]["traffic"] = {
                "direction": "increase" if "+" in str(projected["traffic_change"]) else "decrease",
                "magnitude": projected["traffic_change"],
                "significance": "medium"
            }
        
        if "accessibility_score" in projected:
            baseline_accessibility = 0.6 if neighborhood == "Marina" else 0.8
            change = float(projected.get("accessibility_score", baseline_accessibility)) - baseline_accessibility
            metrics["change_indicators"]["accessibility"] = {
                "direction": "improvement" if change > 0 else "decline",
                "magnitude": f"{change:+.1f}",
                "significance": "high" if abs(change) > 0.2 else "medium"
            }
        
        return metrics
    
    def _assess_implementation_complexity(self, considerations: List[str], neighborhood: str) -> Dict[str, Any]:
        """Assess implementation complexity and challenges"""
        complexity_factors = {
            "regulatory_complexity": "medium",
            "community_engagement_needs": "high" if neighborhood == "Mission" else "medium",
            "technical_challenges": "medium",
            "coordination_requirements": "high" if len(considerations) > 3 else "medium"
        }
        
        # Risk factors based on considerations
        risk_factors = []
        for consideration in considerations:
            if "resistance" in consideration.lower():
                risk_factors.append("community_opposition")
            elif "flood" in consideration.lower():
                risk_factors.append("environmental_constraints")
            elif "displacement" in consideration.lower():
                risk_factors.append("equity_concerns")
        
        return {
            "complexity_factors": complexity_factors,
            "risk_factors": risk_factors,
            "estimated_timeline": "2-4 years" if len(risk_factors) > 2 else "1-3 years",
            "mitigation_strategies": [f"Address {factor}" for factor in risk_factors]
        }
    
    def _assess_equity_implications(self, scenario: Dict, neighborhood: str, classification: QueryClassification) -> Dict[str, Any]:
        """Assess equity and displacement implications"""
        equity_score = 0.7  # baseline
        
        # Neighborhood-specific equity considerations
        if neighborhood == "Mission":
            equity_score = 0.4  # High displacement risk
            primary_concerns = ["displacement", "cultural_preservation", "affordability"]
        elif neighborhood == "Marina":
            equity_score = 0.8  # Lower displacement risk but potential exclusivity
            primary_concerns = ["accessibility", "equity_of_access"]
        else:  # Hayes Valley
            equity_score = 0.6  # Moderate gentrification pressure
            primary_concerns = ["affordability", "transit_equity"]
        
        return {
            "equity_score": equity_score,
            "primary_concerns": primary_concerns,
            "vulnerable_populations": self._identify_vulnerable_populations(neighborhood),
            "mitigation_recommendations": self._generate_equity_mitigations(neighborhood, primary_concerns)
        }
    
    def _identify_uncertainty_factors(self, scenario: Dict, template_type: str, neighborhood: str) -> List[Dict[str, Any]]:
        """Identify key uncertainty factors in the analysis"""
        uncertainties = []
        
        # Template-specific uncertainties
        if "transportation" in template_type:
            uncertainties.append({
                "factor": "behavior_change",
                "description": "Actual adoption of new transportation options",
                "impact": "high",
                "mitigation": "Pilot program with phased implementation"
            })
        
        if "housing" in template_type:
            uncertainties.append({
                "factor": "market_conditions",
                "description": "Real estate market changes affecting development feasibility",
                "impact": "medium",
                "mitigation": "Flexible financing mechanisms"
            })
        
        # Neighborhood-specific uncertainties
        if neighborhood == "Marina":
            uncertainties.append({
                "factor": "climate_impacts",
                "description": "Sea level rise affecting long-term viability",
                "impact": "high",
                "mitigation": "Adaptive management approach"
            })
        
        return uncertainties
    
    def _define_success_indicators(self, analysis_type: str, neighborhood: str, projected_impacts: Dict) -> List[Dict[str, Any]]:
        """Define measurable success indicators"""
        indicators = []
        
        # Universal indicators
        indicators.append({
            "indicator": "community_satisfaction",
            "target": ">75% positive feedback",
            "measurement": "Annual community survey",
            "timeline": "ongoing"
        })
        
        # Analysis-type specific indicators
        if "transportation" in analysis_type:
            indicators.extend([
                {
                    "indicator": "mode_shift",
                    "target": "15% reduction in single-occupancy vehicle trips",
                    "measurement": "Traffic count analysis",
                    "timeline": "2 years post-implementation"
                },
                {
                    "indicator": "business_impact",
                    "target": "Maintain or increase local business revenue",
                    "measurement": "Business survey and sales tax data",
                    "timeline": "quarterly"
                }
            ])
        
        return indicators
    
    def _identify_vulnerable_populations(self, neighborhood: str) -> List[str]:
        """Identify vulnerable populations by neighborhood"""
        populations = {
            "Mission": ["long-term_residents", "low_income_families", "latino_community", "artists_creators"],
            "Marina": ["seniors", "families_with_children", "people_with_disabilities"],
            "Hayes Valley": ["existing_tenants", "local_workers", "transit_dependent_residents"]
        }
        return populations.get(neighborhood, ["general_community"])
    
    def _generate_equity_mitigations(self, neighborhood: str, concerns: List[str]) -> List[str]:
        """Generate specific equity mitigation strategies"""
        mitigations = []
        
        for concern in concerns:
            if concern == "displacement":
                mitigations.extend([
                    "Right to return policies for existing residents",
                    "Community land trust development",
                    "Tenant protection and relocation assistance"
                ])
            elif concern == "affordability":
                mitigations.extend([
                    "Deed-restricted affordable housing",
                    "Community benefits district funding",
                    "Local hiring requirements"
                ])
            elif concern == "cultural_preservation":
                mitigations.extend([
                    "Cultural business preservation zones", 
                    "Community arts and cultural programming",
                    "Multilingual community engagement"
                ])
        
        return list(set(mitigations))  # Remove duplicates
    
    def _evaluate_comparative_analysis(self, comparative_analysis: Dict, evaluated_scenarios: List[Dict], context: AgentContext) -> Dict[str, Any]:
        """Evaluate the comparative analysis from PlannerAgent"""
        neighborhoods = [scenario.get("neighborhood") for scenario in evaluated_scenarios]
        
        return {
            "cross_neighborhood_insights": {
                "implementation_priority": self._rank_implementation_priority(evaluated_scenarios),
                "resource_sharing_opportunities": self._identify_resource_sharing(evaluated_scenarios),
                "policy_coordination_needs": self._assess_policy_coordination(evaluated_scenarios)
            },
            "equity_comparison": {
                "relative_benefits": self._compare_equity_benefits(evaluated_scenarios),
                "displacement_risk_ranking": self._rank_displacement_risk(evaluated_scenarios),
                "community_readiness": self._assess_community_readiness(evaluated_scenarios)
            },
            "implementation_sequence": self._recommend_implementation_sequence(evaluated_scenarios)
        }
    
    def _rank_implementation_priority(self, scenarios: List[Dict]) -> List[Dict[str, Any]]:
        """Rank scenarios by implementation priority"""
        ranked = []
        
        for scenario in scenarios:
            neighborhood = scenario.get("neighborhood", "")
            complexity = scenario.get("enhanced_impacts", {}).get("implementation_complexity", {})
            equity = scenario.get("enhanced_impacts", {}).get("equity_assessment", {})
            
            # Simple priority scoring
            priority_score = 0.0
            if equity.get("equity_score", 0) < 0.5:  # High equity need
                priority_score += 0.4
            if len(complexity.get("risk_factors", [])) < 3:  # Lower complexity
                priority_score += 0.3
            if scenario.get("evaluation_confidence", 0) > 0.7:  # High confidence
                priority_score += 0.3
            
            ranked.append({
                "neighborhood": neighborhood,
                "priority_score": priority_score,
                "rationale": self._generate_priority_rationale(scenario, priority_score)
            })
        
        return sorted(ranked, key=lambda x: x["priority_score"], reverse=True)
    
    def _generate_priority_rationale(self, scenario: Dict, score: float) -> str:
        """Generate rationale for priority ranking"""
        neighborhood = scenario.get("neighborhood", "")
        if score > 0.7:
            return f"{neighborhood}: High priority due to equity needs and implementation readiness"
        elif score > 0.4:
            return f"{neighborhood}: Medium priority with balanced considerations"
        else:
            return f"{neighborhood}: Lower priority, requires more preparation"
    
    def _generate_kpi_dashboard(self, context: AgentContext, template_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate KPI dashboard for visualizing analysis results"""
        evaluated_scenarios = context.data.get("evaluated_scenarios", [])
        comparative_evaluation = context.data.get("comparative_evaluation", {})
        
        # Extract key metrics across all scenarios
        kpi_metrics = {
            "overview": {
                "total_scenarios": len(evaluated_scenarios),
                "neighborhoods_analyzed": len(set(s.get("neighborhood") for s in evaluated_scenarios)),
                "analysis_confidence": context.confidence,
                "template_type": template_analysis.get("template_type", "unknown")
            },
            "equity_metrics": self._calculate_equity_kpis(evaluated_scenarios),
            "implementation_metrics": self._calculate_implementation_kpis(evaluated_scenarios),
            "impact_summary": self._calculate_impact_summary_kpis(evaluated_scenarios),
            "visualization_data": self._prepare_visualization_data(evaluated_scenarios, comparative_evaluation)
        }
        
        return kpi_metrics
    
    def _calculate_equity_kpis(self, scenarios: List[Dict]) -> Dict[str, Any]:
        """Calculate equity-focused KPIs"""
        if not scenarios:
            return {"equity_scores": [], "displacement_risks": [], "vulnerable_population_count": 0}
        
        equity_scores = []
        displacement_risks = []
        vulnerable_populations = set()
        
        for scenario in scenarios:
            enhanced_impacts = scenario.get("enhanced_impacts", {})
            equity_assessment = enhanced_impacts.get("equity_assessment", {})
            
            equity_scores.append(equity_assessment.get("equity_score", 0.5))
            
            # Map equity score to displacement risk
            equity_score = equity_assessment.get("equity_score", 0.5)
            if equity_score < 0.5:
                displacement_risks.append("high")
            elif equity_score < 0.7:
                displacement_risks.append("medium")
            else:
                displacement_risks.append("low")
            
            # Collect vulnerable populations
            vuln_pops = equity_assessment.get("vulnerable_populations", [])
            vulnerable_populations.update(vuln_pops)
        
        return {
            "average_equity_score": sum(equity_scores) / len(equity_scores) if equity_scores else 0,
            "equity_score_range": [min(equity_scores), max(equity_scores)] if equity_scores else [0, 0],
            "displacement_risk_distribution": {
                "high": displacement_risks.count("high"),
                "medium": displacement_risks.count("medium"),
                "low": displacement_risks.count("low")
            },
            "vulnerable_population_count": len(vulnerable_populations),
            "vulnerable_populations": list(vulnerable_populations)
        }
    
    def _calculate_implementation_kpis(self, scenarios: List[Dict]) -> Dict[str, Any]:
        """Calculate implementation-focused KPIs"""
        if not scenarios:
            return {"complexity_distribution": {}, "timeline_distribution": {}, "confidence_scores": []}
        
        complexity_levels = []
        timelines = []
        confidence_scores = []
        risk_factors_all = []
        
        for scenario in scenarios:
            enhanced_impacts = scenario.get("enhanced_impacts", {})
            implementation = enhanced_impacts.get("implementation_complexity", {})
            
            # Collect complexity data
            complexity_factors = implementation.get("complexity_factors", {})
            avg_complexity = self._average_complexity_score(complexity_factors)
            complexity_levels.append(avg_complexity)
            
            # Collect timeline data
            timeline = implementation.get("estimated_timeline", "unknown")
            timelines.append(timeline)
            
            # Collect confidence scores
            confidence = scenario.get("evaluation_confidence", 0.5)
            confidence_scores.append(confidence)
            
            # Collect risk factors
            risk_factors = implementation.get("risk_factors", [])
            risk_factors_all.extend(risk_factors)
        
        return {
            "average_complexity": sum(complexity_levels) / len(complexity_levels) if complexity_levels else 0,
            "timeline_distribution": self._count_timeline_distribution(timelines),
            "average_confidence": sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0,
            "common_risk_factors": self._count_risk_factors(risk_factors_all),
            "implementation_readiness": "high" if sum(confidence_scores) / len(confidence_scores) > 0.7 else "medium"
        }
    
    def _calculate_impact_summary_kpis(self, scenarios: List[Dict]) -> Dict[str, Any]:
        """Calculate impact summary KPIs"""
        if not scenarios:
            return {"positive_impacts": 0, "negative_impacts": 0, "mixed_impacts": 0}
        
        impact_types = []
        uncertainty_levels = []
        success_indicator_count = 0
        
        for scenario in scenarios:
            enhanced_impacts = scenario.get("enhanced_impacts", {})
            
            # Count success indicators
            success_indicators = enhanced_impacts.get("success_indicators", [])
            success_indicator_count += len(success_indicators)
            
            # Assess uncertainty levels
            uncertainty_factors = enhanced_impacts.get("uncertainty_factors", [])
            uncertainty_level = len(uncertainty_factors)
            uncertainty_levels.append(uncertainty_level)
            
            # Assess overall impact direction
            equity_score = enhanced_impacts.get("equity_assessment", {}).get("equity_score", 0.5)
            if equity_score > 0.7:
                impact_types.append("positive")
            elif equity_score < 0.4:
                impact_types.append("negative")
            else:
                impact_types.append("mixed")
        
        return {
            "impact_distribution": {
                "positive": impact_types.count("positive"),
                "negative": impact_types.count("negative"),
                "mixed": impact_types.count("mixed")
            },
            "average_uncertainty": sum(uncertainty_levels) / len(uncertainty_levels) if uncertainty_levels else 0,
            "total_success_indicators": success_indicator_count,
            "overall_impact_trend": max(set(impact_types), key=impact_types.count) if impact_types else "unknown"
        }
    
    def _prepare_visualization_data(self, scenarios: List[Dict], comparative_evaluation: Dict) -> Dict[str, Any]:
        """Prepare data for frontend visualizations"""
        viz_data = {
            "neighborhood_comparison": [],
            "equity_vs_complexity": [],
            "timeline_chart": [],
            "risk_matrix": []
        }
        
        for scenario in scenarios:
            neighborhood = scenario.get("neighborhood", "unknown")
            enhanced_impacts = scenario.get("enhanced_impacts", {})
            
            # Neighborhood comparison data
            equity_score = enhanced_impacts.get("equity_assessment", {}).get("equity_score", 0.5)
            complexity = enhanced_impacts.get("implementation_complexity", {})
            complexity_score = self._average_complexity_score(complexity.get("complexity_factors", {}))
            
            viz_data["neighborhood_comparison"].append({
                "neighborhood": neighborhood,
                "equity_score": equity_score,
                "complexity_score": complexity_score,
                "confidence": scenario.get("evaluation_confidence", 0.5)
            })
            
            # Equity vs Complexity scatter plot data
            viz_data["equity_vs_complexity"].append({
                "x": complexity_score,
                "y": equity_score,
                "label": neighborhood,
                "size": scenario.get("evaluation_confidence", 0.5) * 100
            })
            
            # Timeline chart data
            timeline = complexity.get("estimated_timeline", "unknown")
            viz_data["timeline_chart"].append({
                "neighborhood": neighborhood,
                "timeline": timeline,
                "priority": self._map_timeline_to_priority(timeline)
            })
        
        return viz_data
    
    def _average_complexity_score(self, complexity_factors: Dict[str, str]) -> float:
        """Convert complexity factors to numerical score"""
        if not complexity_factors:
            return 0.5
        
        score_mapping = {"low": 0.2, "medium": 0.5, "high": 0.8}
        scores = [score_mapping.get(level, 0.5) for level in complexity_factors.values()]
        return sum(scores) / len(scores) if scores else 0.5
    
    def _count_timeline_distribution(self, timelines: List[str]) -> Dict[str, int]:
        """Count timeline distribution"""
        timeline_counts = {}
        for timeline in timelines:
            timeline_counts[timeline] = timeline_counts.get(timeline, 0) + 1
        return timeline_counts
    
    def _count_risk_factors(self, risk_factors: List[str]) -> Dict[str, int]:
        """Count common risk factors"""
        risk_counts = {}
        for risk in risk_factors:
            risk_counts[risk] = risk_counts.get(risk, 0) + 1
        return risk_counts
    
    def _map_timeline_to_priority(self, timeline: str) -> int:
        """Map timeline string to priority number"""
        if "1-3" in timeline:
            return 1  # High priority
        elif "2-4" in timeline:
            return 2  # Medium priority
        else:
            return 3  # Lower priority
    
    # Missing helper methods for comparative evaluation
    def _identify_resource_sharing(self, scenarios: List[Dict]) -> List[str]:
        """Identify resource sharing opportunities"""
        opportunities = []
        neighborhoods = [s.get("neighborhood") for s in scenarios]
        
        if "Marina" in neighborhoods and "Hayes Valley" in neighborhoods:
            opportunities.append("Shared climate resilience infrastructure")
        if "Mission" in neighborhoods and "Hayes Valley" in neighborhoods:
            opportunities.append("Transit-oriented development coordination")
        if len(neighborhoods) > 2:
            opportunities.append("Cross-neighborhood pilot program")
        
        return opportunities
    
    def _assess_policy_coordination(self, scenarios: List[Dict]) -> List[str]:
        """Assess policy coordination needs"""
        coordination_needs = []
        
        # Check if multiple scenarios involve similar domains
        analysis_types = [s.get("analysis_type", "") for s in scenarios]
        if len(set(analysis_types)) < len(analysis_types):
            coordination_needs.append("Consistent policy framework across neighborhoods")
        
        coordination_needs.extend([
            "Citywide impact assessment",
            "Resource allocation coordination",
            "Timeline synchronization"
        ])
        
        return coordination_needs
    
    def _compare_equity_benefits(self, scenarios: List[Dict]) -> Dict[str, str]:
        """Compare equity benefits across scenarios"""
        benefits = {}
        
        for scenario in scenarios:
            neighborhood = scenario.get("neighborhood", "")
            equity_assessment = scenario.get("enhanced_impacts", {}).get("equity_assessment", {})
            equity_score = equity_assessment.get("equity_score", 0.5)
            
            if equity_score > 0.7:
                benefits[neighborhood] = "high_benefit"
            elif equity_score > 0.4:
                benefits[neighborhood] = "medium_benefit"
            else:
                benefits[neighborhood] = "requires_attention"
        
        return benefits
    
    def _rank_displacement_risk(self, scenarios: List[Dict]) -> List[Dict[str, Any]]:
        """Rank scenarios by displacement risk"""
        ranked = []
        
        for scenario in scenarios:
            neighborhood = scenario.get("neighborhood", "")
            equity_score = scenario.get("enhanced_impacts", {}).get("equity_assessment", {}).get("equity_score", 0.5)
            
            # Lower equity score = higher displacement risk
            risk_level = "high" if equity_score < 0.4 else "medium" if equity_score < 0.7 else "low"
            
            ranked.append({
                "neighborhood": neighborhood,
                "risk_level": risk_level,
                "equity_score": equity_score
            })
        
        return sorted(ranked, key=lambda x: x["equity_score"])
    
    def _assess_community_readiness(self, scenarios: List[Dict]) -> Dict[str, str]:
        """Assess community readiness for implementation"""
        readiness = {}
        
        for scenario in scenarios:
            neighborhood = scenario.get("neighborhood", "")
            implementation = scenario.get("enhanced_impacts", {}).get("implementation_complexity", {})
            risk_factors = implementation.get("risk_factors", [])
            
            if "community_opposition" in risk_factors:
                readiness[neighborhood] = "low"
            elif len(risk_factors) > 2:
                readiness[neighborhood] = "medium"
            else:
                readiness[neighborhood] = "high"
        
        return readiness
    
    def _recommend_implementation_sequence(self, scenarios: List[Dict]) -> List[Dict[str, Any]]:
        """Recommend implementation sequence"""
        # Get priority ranking
        priority_ranking = self._rank_implementation_priority(scenarios)
        
        # Convert to sequence with timing
        sequence = []
        for i, item in enumerate(priority_ranking):
            sequence.append({
                "phase": i + 1,
                "neighborhood": item["neighborhood"],
                "timing": f"Phase {i + 1}",
                "rationale": item["rationale"],
                "dependencies": "Previous phase completion" if i > 0 else "None"
            })
        
        return sequence

    async def _assess_impacts(self, context: AgentContext):
        """FALLBACK: Assess impacts for each scenario (legacy method)"""
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