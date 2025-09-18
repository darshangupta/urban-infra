"""
Agent 3: Evaluator Agent - Calculate before/after impact analysis for development scenarios
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from enum import Enum
import httpx

# Import will be handled by test files to avoid circular dependencies
# from .planner_agent import PlanningAlternatives, DevelopmentPlan


class ImpactCategory(str, Enum):
    """Types of impact analysis"""
    HOUSING = "housing"
    ACCESSIBILITY = "accessibility"  
    EQUITY = "equity"
    ECONOMIC = "economic"
    ENVIRONMENTAL = "environmental"


class ImpactSeverity(str, Enum):
    """Severity levels for impacts"""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


class ImpactMetric(BaseModel):
    """Individual impact measurement"""
    metric_name: str
    category: ImpactCategory
    current_value: float
    projected_value: float
    change_amount: float
    change_percentage: float
    severity: ImpactSeverity
    confidence: float  # 0.0 to 1.0
    description: str


class HousingImpact(BaseModel):
    """Housing-specific impact analysis"""
    current_units: int
    projected_units: int
    net_new_units: int
    affordable_units_added: int
    market_rate_units_added: int
    displacement_risk_score: float  # 0.0 to 1.0
    affordability_improvement: float  # percentage change
    population_capacity_change: int


class AccessibilityImpact(BaseModel):
    """Accessibility and transportation impact analysis"""
    walk_score_change: float
    transit_accessibility_change: float
    bike_infrastructure_impact: float
    parking_impact: int  # spaces added/removed
    traffic_impact_score: float  # 0.0 to 1.0 (higher = more congestion)
    amenity_access_improvement: float  # percentage


class EquityImpact(BaseModel):
    """Equity and social impact analysis"""
    gentrification_pressure_change: float  # -1.0 to 1.0
    demographic_stability_score: float  # 0.0 to 1.0
    cultural_preservation_impact: float
    economic_opportunity_change: float
    community_benefit_score: float


class EconomicImpact(BaseModel):
    """Economic impact analysis"""
    property_value_change_percentage: float
    tax_revenue_increase: float
    construction_jobs_created: int
    permanent_jobs_created: int
    local_business_impact_score: float  # -1.0 to 1.0
    cost_per_unit: float


class EnvironmentalImpact(BaseModel):
    """Environmental impact analysis"""
    green_space_change_sf: float
    stormwater_impact_score: float  # flood risk change
    carbon_footprint_change: float  # tons CO2 annually
    energy_efficiency_rating: float
    climate_resilience_score: float  # 0.0 to 1.0


class ComprehensiveImpact(BaseModel):
    """Complete impact analysis for a development plan"""
    plan_id: str
    plan_name: str
    
    # Detailed impact categories
    housing_impact: HousingImpact
    accessibility_impact: AccessibilityImpact
    equity_impact: EquityImpact
    economic_impact: EconomicImpact
    environmental_impact: EnvironmentalImpact
    
    # Summary metrics
    overall_impact_score: float  # -1.0 to 1.0
    confidence_level: float  # 0.0 to 1.0
    key_benefits: List[str]
    key_concerns: List[str]
    mitigation_strategies: List[str]


class ScenarioComparison(BaseModel):
    """Comparative analysis between development scenarios"""
    scenario_name: str
    baseline_description: str
    
    # Individual plan impacts
    plan_impacts: List[ComprehensiveImpact]
    
    # Comparative analysis
    recommended_plan_id: str
    comparison_rationale: str
    tradeoff_analysis: List[str]
    
    # Aggregate neighborhood effects
    cumulative_housing_impact: HousingImpact
    cumulative_equity_impact: EquityImpact
    
    # Implementation recommendations
    phasing_recommendations: List[str]
    policy_requirements: List[str]
    community_engagement_needs: List[str]
    
    # Quality metrics
    analysis_confidence: float
    data_completeness: float


class EvaluatorAgent:
    """Agent 3: Evaluates planning scenarios and calculates comprehensive impact analysis"""
    
    def __init__(self, api_base_url: str = "http://localhost:8000/api/v1"):
        self.api_base_url = api_base_url
        self.template_evaluators = self._load_template_evaluators()
    
    def _load_template_evaluators(self) -> Dict[str, Any]:
        """Load evaluation methods for different template types"""
        return {
            "Traffic Impact Analysis": self._evaluate_traffic_impact,
            "Business Impact Analysis": self._evaluate_business_impact,
            "Housing Development Analysis": self._evaluate_housing_impact,
            "Climate Impact Analysis": self._evaluate_climate_impact
        }
    
    def evaluate_template_analysis(self, template_analysis: Dict[str, Any], classification: Any) -> Dict[str, Any]:
        """
        ENHANCED: Evaluate template-driven analysis with comprehensive impact calculations
        
        Args:
            template_analysis: Output from PlannerAgent.generate_template_analysis()
            classification: QueryClassification from InterpreterAgent
            
        Returns:
            Comprehensive impact evaluation with KPIs, timeline, and recommendations
        """
        
        template_name = template_analysis.get('template_used', 'Generic Analysis')
        evaluator = self.template_evaluators.get(template_name, self._evaluate_generic)
        
        # Calculate detailed impacts using template-specific evaluator
        impact_evaluation = evaluator(template_analysis, classification)
        
        # Generate KPI dashboard
        kpi_dashboard = self._generate_kpi_dashboard(impact_evaluation, template_analysis)
        
        # Create implementation timeline
        implementation_timeline = self._generate_implementation_timeline(impact_evaluation, classification)
        
        # Calculate before/after metrics
        before_after_metrics = self._calculate_before_after_metrics(impact_evaluation, template_analysis)
        
        return {
            "evaluation_type": "template_driven",
            "template_evaluated": template_name,
            "query_classification": {
                "intent": classification.intent.value,
                "domain": classification.domain.value,
                "neighborhoods": classification.neighborhoods,
                "comparative": classification.comparative
            },
            "impact_evaluation": impact_evaluation,
            "kpi_dashboard": kpi_dashboard,
            "implementation_timeline": implementation_timeline,
            "before_after_metrics": before_after_metrics,
            "overall_confidence": impact_evaluation.get("confidence", 0.75),
            "key_recommendations": impact_evaluation.get("recommendations", [])
        }
    
    def _evaluate_traffic_impact(self, template_analysis: Dict[str, Any], classification: Any) -> Dict[str, Any]:
        """Evaluate traffic impact analysis with business effects"""
        
        neighborhood_analyses = template_analysis.get('neighborhood_analyses', {})
        evaluations = {}
        
        for neighborhood, analysis in neighborhood_analyses.items():
            factors = analysis.get('relevant_factors', [])
            metrics = analysis.get('metrics', {})
            
            # Calculate business impact from traffic changes
            if 'car_dependent_residents' in factors:
                # Marina-type: Traffic increase hurts businesses
                business_impact = -0.12 if 'increase' in str(classification.query_type.value) else 0.08
                customer_access_change = -0.15 if 'increase' in str(classification.query_type.value) else 0.10
            elif 'walkable_corridors' in factors:
                # Mission-type: Some traffic changes help pedestrian businesses
                business_impact = 0.08 if 'bike' in str(classification.parameters) else -0.05
                customer_access_change = 0.12 if 'bike' in str(classification.parameters) else -0.08
            else:
                business_impact = 0.02
                customer_access_change = 0.03
            
            evaluations[neighborhood] = {
                "business_revenue_impact_pct": business_impact,
                "customer_access_change_pct": customer_access_change,
                "adaptation_timeline_months": 6 if abs(business_impact) > 0.10 else 3,
                "mitigation_required": abs(business_impact) > 0.10,
                "confidence": 0.85
            }
        
        # Overall evaluation
        avg_business_impact = sum(e['business_revenue_impact_pct'] for e in evaluations.values()) / len(evaluations)
        
        return {
            "analysis_type": "traffic_impact_evaluation",
            "overall_business_impact_pct": avg_business_impact,
            "neighborhood_evaluations": evaluations,
            "total_mitigation_cost_estimate": 50000 * sum(1 for e in evaluations.values() if e['mitigation_required']),
            "confidence": 0.82,
            "recommendations": [
                "Implement business support fund for affected areas",
                "Phased implementation to minimize disruption",
                "Regular monitoring of business performance metrics"
            ]
        }
    
    def _evaluate_business_impact(self, template_analysis: Dict[str, Any], classification: Any) -> Dict[str, Any]:
        """Evaluate pure business impact analysis"""
        
        neighborhood_analyses = template_analysis.get('neighborhood_analyses', {})
        evaluations = {}
        
        for neighborhood, analysis in neighborhood_analyses.items():
            factors = analysis.get('relevant_factors', [])
            
            # Business type determines impact magnitude and adaptation
            if 'high_end_retail' in factors:
                revenue_volatility = 0.15  # Luxury retail more volatile
                adaptation_capacity = 0.8   # But better resources to adapt
            elif 'community_businesses' in factors:
                revenue_volatility = 0.08   # Community businesses more stable
                adaptation_capacity = 0.6   # But fewer resources
            else:
                revenue_volatility = 0.10
                adaptation_capacity = 0.7
            
            # Calculate impact based on query parameters
            base_impact = 0.05  # Default positive impact
            if classification.parameters.get('percentage'):
                # Scale impact by percentage change
                base_impact *= (1 + classification.parameters['percentage'])
            
            evaluations[neighborhood] = {
                "revenue_impact_pct": base_impact,
                "revenue_volatility": revenue_volatility,
                "adaptation_capacity": adaptation_capacity,
                "break_even_timeline_months": int(12 / adaptation_capacity),
                "support_programs_needed": adaptation_capacity < 0.7,
                "confidence": 0.78
            }
        
        return {
            "analysis_type": "business_impact_evaluation",
            "neighborhood_evaluations": evaluations,
            "average_revenue_impact_pct": sum(e['revenue_impact_pct'] for e in evaluations.values()) / len(evaluations),
            "businesses_needing_support": sum(1 for e in evaluations.values() if e['support_programs_needed']),
            "confidence": 0.76,
            "recommendations": [
                "Tailor support programs to neighborhood business types",
                "Monitor revenue impacts for first 12 months",
                "Provide adaptation resources for lower-capacity businesses"
            ]
        }
    
    def _evaluate_housing_impact(self, template_analysis: Dict[str, Any], classification: Any) -> Dict[str, Any]:
        """Evaluate housing development impact"""
        
        neighborhood_analyses = template_analysis.get('neighborhood_analyses', {})
        evaluations = {}
        
        for neighborhood, analysis in neighborhood_analyses.items():
            factors = analysis.get('relevant_factors', [])
            
            # Extract housing targets from classification
            target_units = classification.parameters.get('units', 100)
            
            # Displacement risk varies by neighborhood
            if 'displacement_pressure' in factors:
                displacement_risk = 0.7  # Mission - high risk
                community_benefit_multiplier = 1.5
            elif 'low_density_character' in factors:
                displacement_risk = 0.2  # Marina - low risk
                community_benefit_multiplier = 0.8
            else:
                displacement_risk = 0.4  # Hayes Valley - medium
                community_benefit_multiplier = 1.0
            
            # Calculate affordability requirements
            base_affordability = 0.20
            if 'transit_accessibility' in factors:
                base_affordability = 0.25  # Higher near transit
            
            affordable_units = int(target_units * base_affordability)
            community_benefit_cost = target_units * 5000 * community_benefit_multiplier  # $5k per unit base
            
            evaluations[neighborhood] = {
                "new_units": target_units,
                "affordable_units": affordable_units,
                "displacement_risk_score": displacement_risk,
                "community_benefit_cost": community_benefit_cost,
                "implementation_complexity": "high" if displacement_risk > 0.6 else "medium" if displacement_risk > 0.3 else "low",
                "community_engagement_months": 6 if displacement_risk > 0.6 else 3,
                "confidence": 0.80
            }
        
        total_units = sum(e['new_units'] for e in evaluations.values())
        total_affordable = sum(e['affordable_units'] for e in evaluations.values())
        total_benefit_cost = sum(e['community_benefit_cost'] for e in evaluations.values())
        
        return {
            "analysis_type": "housing_impact_evaluation",
            "total_new_units": total_units,
            "total_affordable_units": total_affordable,
            "overall_affordability_pct": total_affordable / total_units if total_units > 0 else 0,
            "total_community_benefit_cost": total_benefit_cost,
            "neighborhood_evaluations": evaluations,
            "confidence": 0.79,
            "recommendations": [
                "Prioritize anti-displacement measures in high-risk areas",
                "Secure community benefit funding early in process",
                "Implement robust community engagement timeline"
            ]
        }
    
    def _evaluate_climate_impact(self, template_analysis: Dict[str, Any], classification: Any) -> Dict[str, Any]:
        """Evaluate climate/environmental impact"""
        
        neighborhood_analyses = template_analysis.get('neighborhood_analyses', {})
        evaluations = {}
        
        for neighborhood, analysis in neighborhood_analyses.items():
            factors = analysis.get('relevant_factors', [])
            
            # Climate vulnerability assessment
            if 'waterfront_vulnerability' in factors:
                climate_vulnerability = 0.9  # Marina - very high
                adaptation_urgency = "immediate"
                base_adaptation_cost = 2000000  # $2M
            elif 'vulnerable_populations' in factors:
                climate_vulnerability = 0.7  # Mission - high social vulnerability
                adaptation_urgency = "high"
                base_adaptation_cost = 1500000  # $1.5M
            else:
                climate_vulnerability = 0.5  # Hayes Valley - moderate
                adaptation_urgency = "medium"
                base_adaptation_cost = 1000000  # $1M
            
            # Temperature impact from parameters
            temp_change = classification.parameters.get('temperature_change', -2)
            energy_impact = abs(temp_change) * 0.08  # 8% per degree change
            
            evaluations[neighborhood] = {
                "climate_vulnerability_score": climate_vulnerability,
                "adaptation_urgency": adaptation_urgency,
                "estimated_adaptation_cost": base_adaptation_cost,
                "energy_cost_impact_pct": energy_impact,
                "implementation_priority": 1 if adaptation_urgency == "immediate" else 2 if adaptation_urgency == "high" else 3,
                "confidence": 0.72
            }
        
        total_adaptation_cost = sum(e['estimated_adaptation_cost'] for e in evaluations.values())
        avg_energy_impact = sum(e['energy_cost_impact_pct'] for e in evaluations.values()) / len(evaluations)
        
        return {
            "analysis_type": "climate_impact_evaluation",
            "total_adaptation_investment": total_adaptation_cost,
            "average_energy_impact_pct": avg_energy_impact,
            "neighborhood_evaluations": evaluations,
            "highest_priority_neighborhood": min(evaluations.keys(), key=lambda k: evaluations[k]['implementation_priority']),
            "confidence": 0.74,
            "recommendations": [
                "Prioritize waterfront neighborhoods for immediate adaptation",
                "Develop neighborhood-specific resilience strategies",
                "Secure climate adaptation funding early"
            ]
        }
    
    def _evaluate_generic(self, template_analysis: Dict[str, Any], classification: Any) -> Dict[str, Any]:
        """Generic evaluation for unknown template types"""
        
        return {
            "analysis_type": "generic_evaluation",
            "note": "Generic evaluation applied - specific evaluator not available",
            "confidence": 0.60,
            "recommendations": [
                "Analysis completed with generic methodology",
                "Consider adding specific evaluator for this template type"
            ]
        }
    
    def _generate_kpi_dashboard(self, impact_evaluation: Dict[str, Any], template_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate KPI dashboard from impact evaluation"""
        
        analysis_type = impact_evaluation.get('analysis_type', 'generic')
        
        if analysis_type == "traffic_impact_evaluation":
            return {
                "primary_kpis": [
                    {
                        "name": "Business Impact",
                        "value": f"{impact_evaluation.get('overall_business_impact_pct', 0):+.1%}",
                        "status": "positive" if impact_evaluation.get('overall_business_impact_pct', 0) > 0 else "negative",
                        "description": "Average business revenue impact"
                    },
                    {
                        "name": "Mitigation Cost",
                        "value": f"${impact_evaluation.get('total_mitigation_cost_estimate', 0):,}",
                        "status": "neutral",
                        "description": "Estimated cost for business support programs"
                    }
                ],
                "implementation_kpis": [
                    {
                        "name": "Timeline",
                        "value": "6 months",
                        "status": "neutral",
                        "description": "Expected adaptation timeline"
                    }
                ]
            }
        
        elif analysis_type == "housing_impact_evaluation":
            return {
                "primary_kpis": [
                    {
                        "name": "New Units",
                        "value": str(impact_evaluation.get('total_new_units', 0)),
                        "status": "positive",
                        "description": "Total housing units created"
                    },
                    {
                        "name": "Affordability",
                        "value": f"{impact_evaluation.get('overall_affordability_pct', 0):.1%}",
                        "status": "positive" if impact_evaluation.get('overall_affordability_pct', 0) > 0.20 else "neutral",
                        "description": "Percentage of affordable housing"
                    },
                    {
                        "name": "Community Benefits",
                        "value": f"${impact_evaluation.get('total_community_benefit_cost', 0):,}",
                        "status": "neutral",
                        "description": "Investment in community benefit programs"
                    }
                ]
            }
        
        else:
            return {
                "primary_kpis": [
                    {
                        "name": "Confidence",
                        "value": f"{impact_evaluation.get('confidence', 0.6):.0%}",
                        "status": "neutral",
                        "description": "Analysis confidence level"
                    }
                ]
            }
    
    def _generate_implementation_timeline(self, impact_evaluation: Dict[str, Any], classification: Any) -> Dict[str, Any]:
        """Generate implementation timeline based on evaluation"""
        
        analysis_type = impact_evaluation.get('analysis_type', 'generic')
        
        if analysis_type == "traffic_impact_evaluation":
            return {
                "total_months": 12,
                "phases": [
                    {
                        "name": "Planning & Engagement",
                        "months": 3,
                        "activities": ["Business stakeholder meetings", "Support program design", "Baseline metrics collection"]
                    },
                    {
                        "name": "Implementation",
                        "months": 6,
                        "activities": ["Infrastructure changes", "Business support activation", "Impact monitoring"]
                    },
                    {
                        "name": "Evaluation & Optimization",
                        "months": 3,
                        "activities": ["Impact assessment", "Program adjustments", "Long-term planning"]
                    }
                ]
            }
        
        elif analysis_type == "housing_impact_evaluation":
            return {
                "total_months": 36,
                "phases": [
                    {
                        "name": "Community Engagement",
                        "months": 6,
                        "activities": ["Community meetings", "Anti-displacement planning", "Financing arrangements"]
                    },
                    {
                        "name": "Development",
                        "months": 24,
                        "activities": ["Construction", "Community benefit implementation", "Ongoing engagement"]
                    },
                    {
                        "name": "Occupancy & Monitoring",
                        "months": 6,
                        "activities": ["Resident move-in", "Community integration", "Long-term monitoring setup"]
                    }
                ]
            }
        
        else:
            return {
                "total_months": 12,
                "phases": [
                    {"name": "Planning", "months": 4, "activities": ["Analysis", "Stakeholder engagement"]},
                    {"name": "Implementation", "months": 6, "activities": ["Execute changes", "Monitor impacts"]},
                    {"name": "Evaluation", "months": 2, "activities": ["Assess outcomes", "Plan next steps"]}
                ]
            }
    
    def _calculate_before_after_metrics(self, impact_evaluation: Dict[str, Any], template_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate before/after comparison metrics"""
        
        analysis_type = impact_evaluation.get('analysis_type', 'generic')
        
        if analysis_type == "traffic_impact_evaluation":
            return {
                "business_revenue": {
                    "before": 100,  # Baseline index
                    "after": 100 + (impact_evaluation.get('overall_business_impact_pct', 0) * 100),
                    "change_pct": impact_evaluation.get('overall_business_impact_pct', 0)
                },
                "customer_access": {
                    "before": 100,
                    "after": 95,  # Estimated based on traffic changes
                    "change_pct": -0.05
                }
            }
        
        elif analysis_type == "housing_impact_evaluation":
            return {
                "housing_units": {
                    "before": 1000,  # Estimated baseline
                    "after": 1000 + impact_evaluation.get('total_new_units', 0),
                    "change_absolute": impact_evaluation.get('total_new_units', 0)
                },
                "affordable_housing_pct": {
                    "before": 0.15,  # Estimated baseline 15%
                    "after": impact_evaluation.get('overall_affordability_pct', 0.20),
                    "change_pct": impact_evaluation.get('overall_affordability_pct', 0.20) - 0.15
                }
            }
        
        else:
            return {
                "note": "Before/after metrics not available for this analysis type"
            }

    def evaluate_scenarios(self, planning_alternatives: Any) -> ScenarioComparison:
        """
        Main entry point: Convert planning alternatives into comprehensive impact analysis
        
        Args:
            planning_alternatives: PlanningAlternatives from Agent 2
            
        Returns:
            ScenarioComparison with detailed before/after impact analysis
        """
        # Step 1: Calculate housing impacts for each plan
        plan_impacts = []
        for plan in planning_alternatives.plans:
            housing_impact = self._calculate_housing_impact(plan, planning_alternatives.neighborhood)
            accessibility_impact = self._calculate_accessibility_impact(plan, planning_alternatives.neighborhood)
            equity_impact = self._calculate_equity_impact(plan, planning_alternatives.neighborhood)
            economic_impact = self._calculate_economic_impact(plan, planning_alternatives.neighborhood)
            environmental_impact = self._calculate_environmental_impact(plan, planning_alternatives.neighborhood)
            
            # Aggregate into comprehensive impact
            comprehensive_impact = self._synthesize_impacts(
                plan, housing_impact, accessibility_impact, equity_impact, 
                economic_impact, environmental_impact
            )
            plan_impacts.append(comprehensive_impact)
        
        # Step 2: Perform comparative analysis
        recommended_plan_id = self._determine_optimal_plan(plan_impacts, planning_alternatives.scenario_name)
        
        # Step 3: Calculate cumulative neighborhood effects
        cumulative_housing = self._calculate_cumulative_housing_impact(plan_impacts)
        cumulative_equity = self._calculate_cumulative_equity_impact(plan_impacts)
        
        # Step 4: Generate implementation recommendations
        phasing_recs = self._generate_phasing_recommendations(plan_impacts, recommended_plan_id)
        policy_reqs = self._identify_policy_requirements(plan_impacts, planning_alternatives.neighborhood)
        
        return ScenarioComparison(
            scenario_name=f"{planning_alternatives.scenario_name} Impact Analysis",
            baseline_description=f"Current conditions in {planning_alternatives.neighborhood}",
            plan_impacts=plan_impacts,
            recommended_plan_id=recommended_plan_id,
            comparison_rationale=self._generate_comparison_rationale(plan_impacts, recommended_plan_id),
            tradeoff_analysis=self._generate_tradeoff_analysis(plan_impacts),
            cumulative_housing_impact=cumulative_housing,
            cumulative_equity_impact=cumulative_equity,
            phasing_recommendations=phasing_recs,
            policy_requirements=policy_reqs,
            community_engagement_needs=self._identify_community_engagement_needs(plan_impacts),
            analysis_confidence=self._calculate_analysis_confidence(plan_impacts),
            data_completeness=self._assess_data_completeness(planning_alternatives.neighborhood)
        )
    
    def _calculate_housing_impact(self, plan: Any, neighborhood: str) -> HousingImpact:
        """Calculate housing and demographic impacts"""
        # Get current housing baseline from API
        try:
            with httpx.Client() as client:
                response = client.get(f"{self.api_base_url}/neighborhoods/{neighborhood}/unit-estimates")
                baseline_data = response.json() if response.status_code == 200 else {}
        except Exception:
            baseline_data = {}
            
        current_units = baseline_data.get("existing_units", 1000)  # Default estimate
        
        # Calculate displacement risk based on plan type and affordability
        displacement_risk = 0.1  # Base risk
        if plan.plan_type.value == "aggressive":
            displacement_risk += 0.3
        elif plan.plan_type.value == "innovative":
            displacement_risk += 0.1
            
        # Reduce risk with higher affordability
        if hasattr(plan, 'affordable_percentage') and plan.affordable_percentage:
            displacement_risk *= (1 - plan.affordable_percentage * 0.5)
        
        displacement_risk = min(displacement_risk, 1.0)
        
        # Calculate affordability improvement
        affordable_units = plan.affordable_units or 0
        affordability_improvement = (affordable_units / plan.total_units) * 100 if plan.total_units > 0 else 0
        
        return HousingImpact(
            current_units=current_units,
            projected_units=current_units + plan.total_units,
            net_new_units=plan.total_units,
            affordable_units_added=affordable_units,
            market_rate_units_added=plan.total_units - affordable_units,
            displacement_risk_score=displacement_risk,
            affordability_improvement=affordability_improvement,
            population_capacity_change=plan.total_units * 2  # Assume 2 people per unit
        )
    
    def _calculate_accessibility_impact(self, plan: Any, neighborhood: str) -> AccessibilityImpact:
        """Calculate accessibility and transportation impacts"""
        # Neighborhood-specific accessibility baselines
        baseline_walk_scores = {
            "Hayes Valley": 85,
            "Marina District": 70,
            "Mission District": 88
        }
        
        baseline_walk_score = baseline_walk_scores.get(neighborhood, 75)
        
        # Calculate walk score improvement based on plan type and ground floor commercial
        walk_score_change = 0
        if hasattr(plan, 'ground_floor_commercial_sf') and plan.ground_floor_commercial_sf:
            walk_score_change += min(plan.ground_floor_commercial_sf / 1000, 5)  # Up to 5 points
        
        # Plan type impacts on walkability
        plan_type_walk_impact = {
            "conservative": 0.5,
            "moderate": 1.0, 
            "aggressive": 1.5,
            "innovative": 3.0  # Innovative plans prioritize walkability
        }
        
        walk_score_change += plan_type_walk_impact.get(plan.plan_type.value, 0)
        
        # Neighborhood-specific walkability potential
        if neighborhood == "Marina District":
            # More room for improvement in Marina
            walk_score_change *= 1.5
        elif neighborhood == "Hayes Valley":
            # Already walkable, harder to improve significantly
            walk_score_change *= 0.8
            
        # Transit accessibility based on neighborhood and plan characteristics
        transit_baselines = {
            "Hayes Valley": 0.9,  # Excellent BART access
            "Marina District": 0.4,  # Limited transit
            "Mission District": 0.8   # Good transit
        }
        
        base_transit = transit_baselines.get(neighborhood, 0.6)
        
        # Transit change varies by plan size and type
        transit_change = 0
        if plan.total_units > 50:  # Large developments may justify new transit
            transit_change = 0.15
        elif plan.total_units > 20:
            transit_change = 0.08
        elif plan.total_units > 10:
            transit_change = 0.03
        
        # Plan type affects transit improvements
        if plan.plan_type.value == "aggressive":
            transit_change += 0.05
        elif plan.plan_type.value == "innovative":
            transit_change += 0.1
        
        # Marina District has more potential for transit improvements
        if neighborhood == "Marina District":
            transit_change *= 1.5
        
        # Bike infrastructure varies significantly by plan type
        bike_impact_by_type = {
            "conservative": 0.5,
            "moderate": 1.0,
            "aggressive": 1.5,
            "innovative": 3.0
        }
        
        bike_infrastructure_impact = bike_impact_by_type.get(plan.plan_type.value, 0.5)
        
        # Parking varies by plan type and neighborhood
        if hasattr(plan, 'parking_spaces'):
            parking_impact = plan.parking_spaces
        else:
            # Parking ratios vary by plan type and neighborhood transit access
            if neighborhood == "Hayes Valley":  # High transit, less parking needed
                parking_ratios = {"conservative": 0.8, "moderate": 0.6, "aggressive": 0.4, "innovative": 0.3}
            elif neighborhood == "Marina District":  # Low transit, more parking needed
                parking_ratios = {"conservative": 1.2, "moderate": 1.0, "aggressive": 0.8, "innovative": 0.6}
            else:  # Mission District - moderate transit
                parking_ratios = {"conservative": 1.0, "moderate": 0.7, "aggressive": 0.5, "innovative": 0.4}
            
            parking_ratio = parking_ratios.get(plan.plan_type.value, 0.5)
            parking_impact = int(plan.total_units * parking_ratio)
        
        # Traffic impact varies by density and neighborhood
        base_traffic = min(plan.total_units / 100, 0.8)
        
        # Adjust for neighborhood characteristics
        if neighborhood == "Hayes Valley":
            # Excellent transit reduces traffic impact
            base_traffic *= 0.7
        elif neighborhood == "Marina District":
            # Limited transit increases traffic impact
            base_traffic *= 1.3
        
        traffic_impact_score = min(base_traffic, 0.8)
        
        return AccessibilityImpact(
            walk_score_change=round(walk_score_change, 1),
            transit_accessibility_change=round(transit_change, 3),
            bike_infrastructure_impact=bike_infrastructure_impact,
            parking_impact=parking_impact,
            traffic_impact_score=traffic_impact_score,
            amenity_access_improvement=walk_score_change * 2  # Correlation with amenities
        )
    
    def _calculate_equity_impact(self, plan: Any, neighborhood: str) -> EquityImpact:
        """Calculate equity and social justice impacts"""
        # Gentrification pressure varies by neighborhood
        gentrification_baselines = {
            "Hayes Valley": 0.7,  # Already gentrifying
            "Marina District": 0.3,  # Stable affluent area
            "Mission District": 0.8   # High gentrification pressure
        }
        
        base_pressure = gentrification_baselines.get(neighborhood, 0.5)
        
        # Plan type affects gentrification pressure
        pressure_multipliers = {
            "conservative": 0.8,
            "moderate": 1.0,
            "aggressive": 1.3,
            "innovative": 0.9  # Often includes anti-displacement measures
        }
        
        pressure_change = (pressure_multipliers[plan.plan_type.value] - 1.0) * base_pressure
        
        # Affordability reduces gentrification pressure
        affordable_percentage = getattr(plan, 'affordable_percentage', 0) or 0
        if affordable_percentage > 0.2:  # 20%+ affordability
            pressure_change -= 0.2
        
        # Community benefit score based on plan characteristics
        community_benefit = 0.5  # Base score
        if plan.plan_type.value == "innovative":
            community_benefit += 0.3
        if affordable_percentage > 0.25:
            community_benefit += 0.2
            
        return EquityImpact(
            gentrification_pressure_change=pressure_change,
            demographic_stability_score=max(0.9 - abs(pressure_change) * 0.8, 0.3),
            cultural_preservation_impact=-abs(pressure_change) * 0.5,
            economic_opportunity_change=plan.total_units / 100,  # More units = more local economy
            community_benefit_score=min(community_benefit, 1.0)
        )
    
    def _calculate_economic_impact(self, plan: Any, neighborhood: str) -> EconomicImpact:
        """Calculate economic and fiscal impacts"""
        # Neighborhood-specific property value impacts
        property_value_multipliers = {
            "Hayes Valley": 1.2,  # High-value area
            "Marina District": 1.5,  # Highest-value area  
            "Mission District": 1.0   # Mixed-value area
        }
        
        base_multiplier = property_value_multipliers.get(neighborhood, 1.1)
        property_value_change = (plan.total_units / 100) * base_multiplier
        
        # Construction and permanent job creation
        construction_jobs = plan.total_units * 2  # Rule of thumb: 2 construction jobs per unit
        
        permanent_jobs = 0
        if hasattr(plan, 'ground_floor_commercial_sf') and plan.ground_floor_commercial_sf:
            permanent_jobs = int(plan.ground_floor_commercial_sf / 500)  # 1 job per 500 sf
        
        # Tax revenue (rough estimate)
        avg_unit_value = 800000  # SF average
        tax_revenue = plan.total_units * avg_unit_value * 0.012  # 1.2% effective tax rate
        
        # Cost per unit estimates
        cost_per_unit_estimates = {
            "conservative": 400000,
            "moderate": 500000,
            "aggressive": 600000,
            "innovative": 550000
        }
        
        cost_per_unit = cost_per_unit_estimates[plan.plan_type.value]
        
        return EconomicImpact(
            property_value_change_percentage=property_value_change,
            tax_revenue_increase=tax_revenue,
            construction_jobs_created=construction_jobs,
            permanent_jobs_created=permanent_jobs,
            local_business_impact_score=0.3 if permanent_jobs > 5 else 0.1,
            cost_per_unit=cost_per_unit
        )
    
    def _calculate_environmental_impact(self, plan: Any, neighborhood: str) -> EnvironmentalImpact:
        """Calculate environmental and climate impacts"""
        # Neighborhood-specific environmental factors
        flood_risk_factors = {
            "Hayes Valley": 0.1,
            "Marina District": 0.8,  # High flood risk
            "Mission District": 0.2
        }
        
        base_flood_risk = flood_risk_factors.get(neighborhood, 0.3)
        
        # Stormwater impact based on development density
        stormwater_impact = (plan.far - 1.0) * 0.2  # Higher FAR = more impervious surface
        
        # Carbon footprint (rough estimate)
        # Denser development typically has lower per-unit carbon footprint
        carbon_per_unit = max(5 - plan.far, 2)  # 2-5 tons CO2 per unit annually
        carbon_footprint_change = plan.total_units * carbon_per_unit
        
        # Climate resilience varies by plan type
        resilience_scores = {
            "conservative": 0.6,
            "moderate": 0.7,
            "aggressive": 0.6,
            "innovative": 0.9  # Often includes climate features
        }
        
        climate_resilience = resilience_scores[plan.plan_type.value]
        
        return EnvironmentalImpact(
            green_space_change_sf=-(plan.lot_area_sf * 0.3),  # Development typically reduces green space
            stormwater_impact_score=min(base_flood_risk + stormwater_impact, 1.0),
            carbon_footprint_change=carbon_footprint_change,
            energy_efficiency_rating=0.8 if plan.plan_type.value == "innovative" else 0.6,
            climate_resilience_score=climate_resilience
        )
    
    def _synthesize_impacts(self, plan: Any, housing: HousingImpact, accessibility: AccessibilityImpact,
                          equity: EquityImpact, economic: EconomicImpact, 
                          environmental: EnvironmentalImpact) -> ComprehensiveImpact:
        """Synthesize all impacts into comprehensive analysis"""
        
        # Calculate overall impact score (weighted average)
        impact_components = [
            housing.affordability_improvement / 100 * 0.3,  # Housing: 30%
            accessibility.walk_score_change / 10 * 0.2,      # Accessibility: 20%
            equity.community_benefit_score * 0.25,           # Equity: 25%
            min(economic.property_value_change_percentage / 10, 0.5) * 0.15,  # Economic: 15%
            environmental.climate_resilience_score * 0.1     # Environmental: 10%
        ]
        
        overall_score = sum(impact_components)
        
        # Generate key benefits and concerns
        benefits = []
        concerns = []
        
        if housing.net_new_units > 5:  # Lowered threshold
            benefits.append(f"Adds {housing.net_new_units} housing units to neighborhood")
        if housing.affordable_units_added > 0:  # Any affordable units
            benefits.append(f"Includes {housing.affordable_units_added} affordable units")
        if accessibility.walk_score_change > 0:  # Any walkability improvement
            benefits.append(f"Improves walkability by {accessibility.walk_score_change:.1f} points")
        if economic.permanent_jobs_created > 0:
            benefits.append(f"Creates {economic.permanent_jobs_created} permanent jobs")
        if economic.construction_jobs_created > 10:
            benefits.append(f"Creates {economic.construction_jobs_created} construction jobs")
        
        if housing.displacement_risk_score > 0.3:  # Lowered threshold
            concerns.append(f"Moderate displacement risk ({housing.displacement_risk_score:.1%})")
        if equity.gentrification_pressure_change > 0.1:  # Lowered threshold
            concerns.append("May accelerate gentrification pressures")
        if environmental.stormwater_impact_score > 0.5:  # Lowered threshold
            concerns.append("Increases flood risk and stormwater management burden")
        if accessibility.traffic_impact_score > 0.3:  # Lowered threshold
            concerns.append("May increase local traffic congestion")
        if economic.cost_per_unit > 500000:
            concerns.append(f"High development cost per unit (${economic.cost_per_unit:,.0f})")
        
        # Ensure we always have some benefits/concerns
        if not benefits:
            benefits.append("Provides new housing opportunities in transit-rich area")
        if not concerns:
            concerns.append("Standard development review and approval process required")
        
        # Mitigation strategies
        mitigation = []
        if housing.displacement_risk_score > 0.4:
            mitigation.append("Implement right of first refusal for existing tenants")
        if housing.displacement_risk_score > 0.2:
            mitigation.append("Include community land trust opportunities")
        if environmental.stormwater_impact_score > 0.6:
            mitigation.append("Include green infrastructure and stormwater management")
        if accessibility.traffic_impact_score > 0.5:
            mitigation.append("Encourage transit use and limit parking provision")
        if economic.cost_per_unit > 500000:
            mitigation.append("Explore value capture and inclusionary zoning")
        
        # Ensure we always have some mitigation strategies
        if not mitigation:
            mitigation.append("Follow standard community engagement and approval processes")
            mitigation.append("Monitor and evaluate project impacts during implementation")
        
        return ComprehensiveImpact(
            plan_id=plan.plan_id,
            plan_name=plan.name,
            housing_impact=housing,
            accessibility_impact=accessibility,
            equity_impact=equity,
            economic_impact=economic,
            environmental_impact=environmental,
            overall_impact_score=overall_score,
            confidence_level=0.75,  # TODO: Calculate based on data availability
            key_benefits=benefits,
            key_concerns=concerns,
            mitigation_strategies=mitigation
        )
    
    def _determine_optimal_plan(self, plan_impacts: List[ComprehensiveImpact], scenario_name: str) -> str:
        """Determine the optimal plan based on comprehensive impact analysis"""
        # Weight factors for plan selection
        weights = {
            "overall_impact_score": 0.4,
            "housing_benefit": 0.25,
            "equity_score": 0.2,
            "feasibility": 0.15
        }
        
        best_plan_id = ""
        best_score = -999
        
        for impact in plan_impacts:
            score = (
                impact.overall_impact_score * weights["overall_impact_score"] +
                impact.housing_impact.affordability_improvement / 100 * weights["housing_benefit"] +
                impact.equity_impact.community_benefit_score * weights["equity_score"] +
                impact.confidence_level * weights["feasibility"]
            )
            
            if score > best_score:
                best_score = score
                best_plan_id = impact.plan_id
        
        return best_plan_id
    
    def _generate_comparison_rationale(self, plan_impacts: List[ComprehensiveImpact], recommended_id: str) -> str:
        """Generate rationale for plan recommendation"""
        recommended_plan = next((p for p in plan_impacts if p.plan_id == recommended_id), None)
        if not recommended_plan:
            return "Unable to determine optimal plan"
            
        rationale_parts = []
        
        # Housing benefits
        if recommended_plan.housing_impact.affordable_units_added > 0:
            rationale_parts.append(f"provides {recommended_plan.housing_impact.affordable_units_added} affordable units")
        
        # Equity considerations  
        if recommended_plan.equity_impact.community_benefit_score > 0.7:
            rationale_parts.append("maximizes community benefits")
        
        # Overall impact
        if recommended_plan.overall_impact_score > 0.5:
            rationale_parts.append("achieves strong overall positive impact")
        
        return f"Recommended plan {' and '.join(rationale_parts)} while maintaining feasibility"
    
    def _generate_tradeoff_analysis(self, plan_impacts: List[ComprehensiveImpact]) -> List[str]:
        """Generate tradeoff analysis between plans"""
        if len(plan_impacts) < 2:
            return ["Insufficient plans for tradeoff analysis"]
        
        tradeoffs = []
        
        # Housing vs displacement tradeoffs
        max_units = max(p.housing_impact.net_new_units for p in plan_impacts)
        max_displacement = max(p.housing_impact.displacement_risk_score for p in plan_impacts)
        
        if max_units > 0 and max_displacement > 0.3:
            tradeoffs.append(f"Higher unit counts (up to {max_units}) correlate with increased displacement risk (up to {max_displacement:.1%})")
        
        # Economic vs equity tradeoffs
        property_changes = [p.economic_impact.property_value_change_percentage for p in plan_impacts]
        equity_scores = [p.equity_impact.community_benefit_score for p in plan_impacts]
        
        if max(property_changes) > 5 and min(equity_scores) < 0.5:
            tradeoffs.append("Plans with higher property value increases may have lower community benefit scores")
        
        # Environmental vs density tradeoffs
        environmental_scores = [p.environmental_impact.climate_resilience_score for p in plan_impacts]
        densities = [p.housing_impact.net_new_units for p in plan_impacts]
        
        if max(densities) > 30 and min(environmental_scores) < 0.6:
            tradeoffs.append("Higher density development may compromise environmental performance")
        
        return tradeoffs or ["Plans show complementary rather than competing benefits"]
    
    def _calculate_cumulative_housing_impact(self, plan_impacts: List[ComprehensiveImpact]) -> HousingImpact:
        """Calculate cumulative housing impact across all plans"""
        if not plan_impacts:
            return HousingImpact(
                current_units=0, projected_units=0, net_new_units=0,
                affordable_units_added=0, market_rate_units_added=0,
                displacement_risk_score=0, affordability_improvement=0,
                population_capacity_change=0
            )
        
        # Take the maximum impact (assuming only one plan would be implemented)
        max_impact_plan = max(plan_impacts, key=lambda p: p.housing_impact.net_new_units)
        return max_impact_plan.housing_impact
    
    def _calculate_cumulative_equity_impact(self, plan_impacts: List[ComprehensiveImpact]) -> EquityImpact:
        """Calculate cumulative equity impact"""
        if not plan_impacts:
            return EquityImpact(
                gentrification_pressure_change=0, demographic_stability_score=0.5,
                cultural_preservation_impact=0, economic_opportunity_change=0,
                community_benefit_score=0.5
            )
        
        # Take the plan with highest community benefit score
        best_equity_plan = max(plan_impacts, key=lambda p: p.equity_impact.community_benefit_score)
        return best_equity_plan.equity_impact
    
    def _generate_phasing_recommendations(self, plan_impacts: List[ComprehensiveImpact], recommended_id: str) -> List[str]:
        """Generate implementation phasing recommendations"""
        recommended_plan = next((p for p in plan_impacts if p.plan_id == recommended_id), None)
        if not recommended_plan:
            return ["Unable to generate phasing recommendations"]
        
        phases = []
        
        # Phase 1: Community engagement and planning
        phases.append("Phase 1: Community engagement and environmental review (6-12 months)")
        
        # Phase 2: Construction considerations
        if recommended_plan.housing_impact.net_new_units > 50:
            phases.append("Phase 2: Phased construction to minimize community disruption (18-36 months)")
        else:
            phases.append("Phase 2: Construction and development (12-18 months)")
        
        # Phase 3: Community integration
        if recommended_plan.equity_impact.community_benefit_score > 0.7:
            phases.append("Phase 3: Community integration and benefit realization (6-12 months)")
        
        return phases
    
    def _identify_policy_requirements(self, plan_impacts: List[ComprehensiveImpact], neighborhood: str) -> List[str]:
        """Identify policy requirements for implementation"""
        policies = []
        
        # Check if any plans require variances
        needs_variances = any("variances" in str(p.plan_id) for p in plan_impacts)
        if needs_variances:
            policies.append("Zoning variances or conditional use permits required")
        
        # Environmental requirements
        high_environmental_impact = any(p.environmental_impact.stormwater_impact_score > 0.6 for p in plan_impacts)
        if high_environmental_impact:
            policies.append("Environmental Impact Report (EIR) likely required")
        
        # Affordability requirements
        affordable_plans = any(p.housing_impact.affordable_units_added > 10 for p in plan_impacts)
        if affordable_plans:
            policies.append("Compliance with inclusionary housing requirements")
        
        return policies or ["Standard planning approvals sufficient"]
    
    def _identify_community_engagement_needs(self, plan_impacts: List[ComprehensiveImpact]) -> List[str]:
        """Identify community engagement requirements"""
        engagement_needs = []
        
        # High displacement risk requires more engagement
        high_displacement = any(p.housing_impact.displacement_risk_score > 0.5 for p in plan_impacts)
        if high_displacement:
            engagement_needs.append("Extensive tenant protection and relocation assistance planning")
        
        # Large developments need neighborhood input
        large_development = any(p.housing_impact.net_new_units > 30 for p in plan_impacts)
        if large_development:
            engagement_needs.append("Neighborhood design review and community input sessions")
        
        # Equity impacts require community partnerships
        equity_focused = any(p.equity_impact.community_benefit_score > 0.7 for p in plan_impacts)
        if equity_focused:
            engagement_needs.append("Community benefit agreement negotiations")
        
        return engagement_needs or ["Standard community notification process"]
    
    def _calculate_analysis_confidence(self, plan_impacts: List[ComprehensiveImpact]) -> float:
        """Calculate overall confidence in the analysis"""
        if not plan_impacts:
            return 0.5
        
        # Average confidence across all plan analyses
        return sum(p.confidence_level for p in plan_impacts) / len(plan_impacts)
    
    def _assess_data_completeness(self, neighborhood: str) -> float:
        """Assess data completeness for the analysis"""
        # In practice, this would check API data availability
        # For now, return reasonable estimates by neighborhood
        completeness_scores = {
            "Hayes Valley": 0.85,
            "Marina District": 0.75, 
            "Mission District": 0.90
        }
        
        return completeness_scores.get(neighborhood, 0.8)