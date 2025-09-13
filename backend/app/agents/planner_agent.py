"""
Agent 2: Planner Agent - Generate feasible development scenarios from research briefs
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from enum import Enum
# Import will be handled by test files to avoid circular dependencies
# from .research_agent import ResearchBrief, PlanningIntent
import httpx


class PlanFeasibility(str, Enum):
    """Plan feasibility assessment"""
    FULLY_COMPLIANT = "fully_compliant"
    REQUIRES_VARIANCES = "requires_variances"
    NEEDS_REZONING = "needs_rezoning"
    NOT_FEASIBLE = "not_feasible"


class PlanType(str, Enum):
    """Types of planning scenarios"""
    CONSERVATIVE = "conservative"  # Minimal changes, high feasibility
    MODERATE = "moderate"         # Balanced approach
    AGGRESSIVE = "aggressive"     # Maximum density/impact
    INNOVATIVE = "innovative"     # Creative solutions


class DevelopmentPlan(BaseModel):
    """Individual development scenario with specific parameters"""
    plan_id: str
    plan_type: PlanType
    name: str
    description: str
    
    # Core development parameters
    far: float
    height_ft: int
    total_units: int
    lot_area_sf: int
    
    # Specific requirements
    affordable_units: Optional[int] = None
    affordable_percentage: Optional[float] = None
    parking_spaces: Optional[int] = None
    ground_floor_commercial_sf: Optional[int] = None
    
    # Feasibility assessment
    feasibility: PlanFeasibility
    zoning_compliance: str
    required_variances: List[str] = []
    estimated_cost: Optional[int] = None  # rough cost estimate
    
    # Planning rationale
    design_rationale: List[str]
    policy_alignment: List[str]
    
    # Constraint validation results
    violations: List[str] = []
    compliance_score: float = 0.0  # 0.0 to 1.0


class PlanningAlternatives(BaseModel):
    """Complete set of planning alternatives for a scenario"""
    scenario_name: str
    original_query: str
    neighborhood: str
    planning_intent: str  # PlanningIntent enum as string
    
    # Generated plans
    plans: List[DevelopmentPlan]
    recommended_plan_id: str
    
    # Comparative analysis
    feasibility_summary: str
    tradeoffs_analysis: List[str]
    
    # Planning context
    zoning_opportunities: List[str]
    regulatory_challenges: List[str]
    community_considerations: List[str]
    
    # Metadata
    generation_confidence: float  # 0.0 to 1.0
    planning_notes: List[str]


class PlannerAgent:
    """Agent 2: Generate feasible development scenarios from research briefs"""
    
    def __init__(self):
        """Initialize planner agent with API clients"""
        self.api_base = "http://localhost:8001/api/v1"
        
    def generate_scenarios(self, research_brief: Any) -> PlanningAlternatives:
        """
        Main entry point: Convert research brief into feasible planning alternatives
        
        Args:
            research_brief: Comprehensive research from Agent 1
            
        Returns:
            PlanningAlternatives: Multiple feasible development scenarios
        """
        # Step 1: Generate candidate development plans
        candidate_plans = self._generate_candidate_plans(research_brief)
        
        # Step 2: Validate each plan against zoning constraints
        validated_plans = []
        neighborhood_key = research_brief.neighborhood.name
        
        for plan in candidate_plans:
            validated_plan = self._validate_plan_feasibility(plan, neighborhood_key)
            validated_plans.append(validated_plan)
        
        # Step 3: Optimize and rank plans
        optimized_plans = self._optimize_plans(validated_plans, research_brief)
        
        # Step 4: Generate comparative analysis
        analysis = self._generate_comparative_analysis(optimized_plans, research_brief)
        
        # Step 5: Extract planning context
        planning_context = self._extract_planning_context(research_brief)
        
        # Step 6: Determine recommended plan (highest scoring)
        recommended_plan_id = optimized_plans[0].plan_id if optimized_plans else "none"
        
        # Step 7: Generate scenario name
        scenario_name = f"{research_brief.neighborhood.display_name} {research_brief.intent.replace('_', ' ').title()}"
        
        # Step 8: Calculate generation confidence
        generation_confidence = self._calculate_generation_confidence(optimized_plans, research_brief)
        
        # Step 9: Generate planning notes
        planning_notes = self._generate_planning_notes(optimized_plans, research_brief)
        
        return PlanningAlternatives(
            scenario_name=scenario_name,
            original_query=research_brief.original_query,
            neighborhood=research_brief.neighborhood.display_name,
            planning_intent=str(research_brief.intent),
            plans=optimized_plans,
            recommended_plan_id=recommended_plan_id,
            feasibility_summary=analysis["feasibility_summary"],
            tradeoffs_analysis=analysis["tradeoffs_analysis"],
            zoning_opportunities=planning_context["zoning_opportunities"],
            regulatory_challenges=planning_context["regulatory_challenges"],
            community_considerations=planning_context["community_considerations"],
            generation_confidence=generation_confidence,
            planning_notes=planning_notes
        )
    
    def _calculate_generation_confidence(self, plans: List[DevelopmentPlan], research_brief: Any) -> float:
        """Calculate confidence in the generated planning alternatives"""
        if not plans:
            return 0.0
        
        confidence = 0.8  # Base confidence
        
        # Boost confidence based on plan quality
        avg_compliance = sum(p.compliance_score for p in plans) / len(plans)
        confidence += (avg_compliance - 0.5) * 0.2  # Up to +0.2 for high compliance
        
        # Boost confidence if we have variety in feasibility
        feasibility_types = set(p.feasibility for p in plans)
        if len(feasibility_types) > 1:
            confidence += 0.1
        
        # Reduce confidence for API validation errors
        validation_errors = sum(1 for p in plans if any("error" in v.lower() for v in p.violations))
        confidence -= validation_errors * 0.1
        
        return max(0.1, min(1.0, confidence))
    
    def _generate_planning_notes(self, plans: List[DevelopmentPlan], research_brief: Any) -> List[str]:
        """Generate planning notes highlighting key assumptions and recommendations"""
        notes = []
        
        if not plans:
            notes.append("No feasible plans could be generated for this scenario")
            return notes
        
        # Note about plan validation
        if any("error" in str(p.violations).lower() for p in plans):
            notes.append("Some plans could not be fully validated against zoning constraints")
        
        # Note about neighborhood characteristics
        neighborhood = research_brief.neighborhood
        notes.append(f"Analysis based on {neighborhood.display_name} {neighborhood.zoning.zone_type} zoning")
        
        # Note about constraints
        if len(research_brief.major_constraints) > 2:
            notes.append(f"Multiple constraints identified: {', '.join(research_brief.major_constraints[:2])}")
        
        # Note about high-performing plans
        top_plan = plans[0]  # Optimized list has best plan first
        if top_plan.compliance_score > 0.9:
            notes.append(f"Recommended plan ({top_plan.name}) achieves high compliance with minimal variances")
        elif top_plan.compliance_score < 0.6:
            notes.append("All scenarios require significant variances or rezoning - consider revising targets")
        
        # Note about affordability
        affordable_plans = [p for p in plans if p.affordable_percentage and p.affordable_percentage > 0.25]
        if affordable_plans:
            notes.append(f"{len(affordable_plans)} plans exceed 25% affordability through innovative financing")
        
        return notes
    
    def _generate_candidate_plans(self, research_brief: Any) -> List[DevelopmentPlan]:
        """Generate 3-5 candidate development plans with varying approaches"""
        plans = []
        
        # Extract key parameters from research brief
        neighborhood = research_brief.neighborhood
        target_metrics = research_brief.target_metrics
        intent = research_brief.intent
        
        # Base parameters for plan generation
        base_lot_area = 3000  # Typical SF lot size for new development
        zoning = neighborhood.zoning
        
        # Generate different scenario types
        
        # 1. Conservative Plan - Minimum viable approach
        conservative_plan = self._generate_conservative_plan(
            neighborhood, target_metrics, intent, base_lot_area
        )
        plans.append(conservative_plan)
        
        # 2. Moderate Plan - Balanced approach
        moderate_plan = self._generate_moderate_plan(
            neighborhood, target_metrics, intent, base_lot_area
        )
        plans.append(moderate_plan)
        
        # 3. Aggressive Plan - Maximum feasible development
        aggressive_plan = self._generate_aggressive_plan(
            neighborhood, target_metrics, intent, base_lot_area
        )
        plans.append(aggressive_plan)
        
        # 4. Intent-specific innovative plan
        if intent in ["anti_displacement", "climate_resilience", "walkability_improvement"]:
            innovative_plan = self._generate_innovative_plan(
                neighborhood, target_metrics, intent, base_lot_area
            )
            plans.append(innovative_plan)
        
        return plans
    
    def _validate_plan_feasibility(self, plan: DevelopmentPlan, neighborhood_key: str) -> DevelopmentPlan:
        """Validate plan against zoning constraints using API"""
        try:
            # Prepare proposal data for validation API
            proposal_data = {
                "far": plan.far,
                "height_ft": plan.height_ft,
                "lot_area_sf": plan.lot_area_sf,
                "num_units": plan.total_units
            }
            
            # Call our constraint validation API
            with httpx.Client() as client:
                response = client.post(
                    f"{self.api_base}/neighborhoods/{neighborhood_key}/validate-proposal",
                    json=proposal_data,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    validation_result = response.json()
                    
                    # Update plan with validation results
                    updated_plan = plan.copy(deep=True)
                    
                    # Convert violation objects to readable strings
                    raw_violations = validation_result.get("violations", [])
                    updated_plan.violations = []
                    
                    for violation in raw_violations:
                        if isinstance(violation, dict):
                            rule = violation.get("rule", "Unknown")
                            current = violation.get("current_value", "N/A")
                            max_allowed = violation.get("max_allowed", "N/A")
                            violation_str = f"{rule}: {current} exceeds limit of {max_allowed}"
                            updated_plan.violations.append(violation_str)
                        else:
                            updated_plan.violations.append(str(violation))
                    
                    # Determine feasibility based on validation
                    is_valid = validation_result.get("is_valid", False)
                    violation_count = len(updated_plan.violations)
                    
                    if is_valid and violation_count == 0:
                        updated_plan.feasibility = PlanFeasibility.FULLY_COMPLIANT
                        updated_plan.compliance_score = 1.0
                    elif violation_count <= 2:  # Minor violations
                        updated_plan.feasibility = PlanFeasibility.REQUIRES_VARIANCES
                        updated_plan.compliance_score = max(0.7, 1.0 - (violation_count * 0.1))
                    elif violation_count <= 4:  # Major violations
                        updated_plan.feasibility = PlanFeasibility.NEEDS_REZONING
                        updated_plan.compliance_score = max(0.4, 1.0 - (violation_count * 0.15))
                    else:  # Severe violations
                        updated_plan.feasibility = PlanFeasibility.NOT_FEASIBLE
                        updated_plan.compliance_score = min(0.3, 1.0 - (violation_count * 0.2))
                    
                    # Update zoning compliance description
                    if updated_plan.violations:
                        violation_summary = ", ".join(updated_plan.violations[:2])
                        if len(updated_plan.violations) > 2:
                            violation_summary += f" +{len(updated_plan.violations)-2} more"
                        updated_plan.zoning_compliance = f"Violations: {violation_summary}"
                    else:
                        updated_plan.zoning_compliance = "Fully compliant with zoning requirements"
                    
                    return updated_plan
                    
                else:
                    # API call failed - return original plan with warning
                    plan.violations = [f"API validation failed: HTTP {response.status_code}"]
                    plan.compliance_score = 0.5  # Unknown compliance
                    return plan
                    
        except httpx.TimeoutException:
            plan.violations = ["Validation timeout - constraint checking unavailable"]
            plan.compliance_score = 0.5
            return plan
            
        except Exception as e:
            plan.violations = [f"Validation error: {str(e)}"]
            plan.compliance_score = 0.5
            return plan
    
    def _optimize_plans(self, plans: List[DevelopmentPlan], research_brief: Any) -> List[DevelopmentPlan]:
        """Rank and optimize plans based on feasibility and policy alignment"""
        
        # Calculate optimization scores for each plan
        scored_plans = []
        for plan in plans:
            score = self._calculate_plan_score(plan, research_brief)
            scored_plans.append((plan, score))
        
        # Sort by score (highest first)
        scored_plans.sort(key=lambda x: x[1], reverse=True)
        
        # Return optimized plans in ranked order
        return [plan for plan, score in scored_plans]
    
    def _calculate_plan_score(self, plan: DevelopmentPlan, research_brief: Any) -> float:
        """Calculate optimization score for plan based on multiple criteria"""
        score = 0.0
        
        # 1. Compliance Score (40% weight)
        compliance_weight = 0.4
        score += plan.compliance_score * compliance_weight
        
        # 2. Target Achievement Score (30% weight) 
        target_weight = 0.3
        target_score = self._calculate_target_achievement_score(plan, research_brief)
        score += target_score * target_weight
        
        # 3. Policy Alignment Score (20% weight)
        policy_weight = 0.2
        policy_score = self._calculate_policy_alignment_score(plan, research_brief)
        score += policy_score * policy_weight
        
        # 4. Innovation Score (10% weight)
        innovation_weight = 0.1
        innovation_score = self._calculate_innovation_score(plan, research_brief)
        score += innovation_score * innovation_weight
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _calculate_target_achievement_score(self, plan: DevelopmentPlan, research_brief: Any) -> float:
        """Score how well plan achieves target metrics"""
        score = 0.0
        target_metrics = research_brief.target_metrics
        
        # Units target achievement
        if target_metrics.units:
            units_ratio = plan.total_units / target_metrics.units
            # Score peaks at 1.0 for exact match, decreases for over/under
            if units_ratio <= 1.0:
                units_score = units_ratio  # Reward getting close to target
            else:
                units_score = 1.0 / units_ratio  # Penalize excessive units
            score += units_score * 0.5
        else:
            score += 0.5  # Default if no target specified
        
        # Affordability target achievement
        if target_metrics.affordability_pct:
            if plan.affordable_percentage >= target_metrics.affordability_pct:
                affordability_score = 1.0  # Full score for meeting/exceeding
            else:
                affordability_score = plan.affordable_percentage / target_metrics.affordability_pct
            score += affordability_score * 0.5
        else:
            # Reward any affordability when none specified
            score += min(plan.affordable_percentage * 2, 0.5)
        
        return min(score, 1.0)
    
    def _calculate_policy_alignment_score(self, plan: DevelopmentPlan, research_brief: Any) -> float:
        """Score alignment with planning intent and policies"""
        score = 0.0
        intent = str(research_brief.intent)
        
        # Intent-specific scoring
        if intent == "housing_development":
            # Reward high unit count and affordability
            score += min(plan.total_units / 30.0, 0.5)  # Up to 0.5 for units
            score += min(plan.affordable_percentage * 2, 0.5)  # Up to 0.5 for affordability
        
        elif intent == "anti_displacement":
            # Reward high affordability and community benefits
            score += min(plan.affordable_percentage * 2.5, 0.7)  # High weight on affordability
            if "community" in plan.name.lower() or plan.plan_type.value == "innovative":
                score += 0.3  # Bonus for community-focused plans
        
        elif intent == "climate_resilience": 
            # Reward climate-adaptive features
            if "climate" in plan.name.lower() or "elevated" in plan.description.lower():
                score += 0.5
            if plan.plan_type.value == "innovative":
                score += 0.3
            score += 0.2  # Base score for any plan in climate context
        
        elif intent == "walkability_improvement":
            # Reward mixed-use and pedestrian features
            if plan.ground_floor_commercial_sf and plan.ground_floor_commercial_sf > 1000:
                score += 0.4  # Reward substantial ground floor commercial
            if plan.parking_spaces < plan.total_units * 0.5:  # Low parking ratio
                score += 0.3  # Reward walkability-supporting parking
            score += 0.3  # Base score
        
        elif intent == "transit_improvement":
            # Reward density near transit
            if plan.parking_spaces < plan.total_units * 0.7:  # Transit-supportive parking
                score += 0.4
            score += min(plan.total_units / 25.0, 0.6)  # Reward density
        
        else:
            score = 0.5  # Default score for other intents
        
        return min(score, 1.0)
    
    def _calculate_innovation_score(self, plan: DevelopmentPlan, research_brief: Any) -> float:
        """Score plan innovation and creative solutions"""
        score = 0.0
        
        # Plan type innovation scoring
        if plan.plan_type == PlanType.INNOVATIVE:
            score += 0.6
        elif plan.plan_type == PlanType.AGGRESSIVE:
            score += 0.4
        elif plan.plan_type == PlanType.MODERATE:
            score += 0.2
        # Conservative gets 0.0 for innovation
        
        # Design rationale complexity
        unique_rationale_count = len(set(plan.design_rationale))
        score += min(unique_rationale_count / 10.0, 0.3)  # Up to 0.3 for diverse rationale
        
        # Variance requirements as innovation indicator
        if len(plan.required_variances) > 0:
            score += min(len(plan.required_variances) / 5.0, 0.1)  # Small bonus for creative variances
        
        return min(score, 1.0)
    
    def _generate_comparative_analysis(self, plans: List[DevelopmentPlan], 
                                     research_brief: Any) -> Dict[str, Any]:
        """Generate comparative analysis and tradeoffs between plans"""
        
        if not plans:
            return {
                "feasibility_summary": "No plans generated",
                "tradeoffs_analysis": []
            }
        
        # Generate feasibility summary
        feasibility_counts = {}
        for plan in plans:
            feasibility = plan.feasibility.value
            feasibility_counts[feasibility] = feasibility_counts.get(feasibility, 0) + 1
        
        feasibility_summary = f"Generated {len(plans)} plans: "
        summary_parts = []
        for feasibility, count in feasibility_counts.items():
            summary_parts.append(f"{count} {feasibility.replace('_', ' ')}")
        feasibility_summary += ", ".join(summary_parts)
        
        # Generate tradeoffs analysis
        tradeoffs = []
        
        # Unit count tradeoffs
        unit_counts = [p.total_units for p in plans]
        min_units, max_units = min(unit_counts), max(unit_counts)
        if max_units > min_units:
            tradeoffs.append(f"Unit count ranges from {min_units} to {max_units} - higher density requires more variances")
        
        # Affordability tradeoffs
        affordability_pcts = [p.affordable_percentage for p in plans if p.affordable_percentage]
        if affordability_pcts:
            min_afford, max_afford = min(affordability_pcts), max(affordability_pcts)
            if max_afford > min_afford:
                tradeoffs.append(f"Affordability ranges from {min_afford:.0%} to {max_afford:.0%} - higher affordability may need subsidies")
        
        # Compliance tradeoffs
        compliance_scores = [p.compliance_score for p in plans]
        min_compliance, max_compliance = min(compliance_scores), max(compliance_scores)
        if max_compliance > min_compliance + 0.1:  # Significant difference
            tradeoffs.append(f"Compliance varies from {min_compliance:.0%} to {max_compliance:.0%} - high compliance limits development potential")
        
        # Plan type tradeoffs
        plan_types = list(set(p.plan_type.value for p in plans))
        if len(plan_types) > 2:
            tradeoffs.append("Conservative plans ensure approval but limit impact; innovative plans maximize benefits but increase risk")
        
        # Parking tradeoffs
        parking_ratios = [p.parking_spaces / p.total_units for p in plans if p.total_units > 0]
        if parking_ratios:
            min_parking, max_parking = min(parking_ratios), max(parking_ratios)
            if max_parking > min_parking + 0.2:  # Significant difference
                tradeoffs.append("Lower parking supports walkability but may require variances and face community resistance")
        
        return {
            "feasibility_summary": feasibility_summary,
            "tradeoffs_analysis": tradeoffs
        }
    
    def _generate_conservative_plan(self, neighborhood, target_metrics, intent, lot_area) -> DevelopmentPlan:
        """Generate conservative plan with minimal risk and high feasibility"""
        zoning = neighborhood.zoning
        
        # Conservative approach: Use 70% of max allowable parameters
        far = min(zoning.max_far * 0.7, 2.0)
        height = min(zoning.max_height_ft * 0.8, zoning.max_height_ft - 5)
        
        # Calculate units based on conservative density
        total_units = max(int(lot_area * far / 800), target_metrics.units or 10)  # ~800 sq ft per unit
        affordable_units = int(total_units * (zoning.affordable_housing_req or 0.15))
        
        return DevelopmentPlan(
            plan_id=f"{neighborhood.name}_conservative_001",
            plan_type=PlanType.CONSERVATIVE,
            name=f"Conservative {neighborhood.display_name} Development",
            description="Low-risk approach prioritizing zoning compliance and community acceptance",
            far=far,
            height_ft=int(height),
            total_units=total_units,
            lot_area_sf=lot_area,
            affordable_units=affordable_units,
            affordable_percentage=affordable_units / total_units if total_units > 0 else 0,
            parking_spaces=int(total_units * max(zoning.min_parking * 0.8, 0.5)),
            ground_floor_commercial_sf=500 if zoning.ground_floor_commercial else 0,
            feasibility=PlanFeasibility.FULLY_COMPLIANT,
            zoning_compliance=f"{zoning.zone_type} fully compliant",
            required_variances=[],
            design_rationale=[
                "Prioritizes zoning compliance",
                "Conservative density for community acceptance",
                "Meets minimum affordability requirements"
            ],
            policy_alignment=[
                "Full zoning compliance",
                "Community-scale development",
                "Standard inclusionary housing"
            ],
            compliance_score=0.95
        )
    
    def _generate_moderate_plan(self, neighborhood, target_metrics, intent, lot_area) -> DevelopmentPlan:
        """Generate moderate plan balancing ambition with feasibility"""
        zoning = neighborhood.zoning
        
        # Moderate approach: Use 85-95% of max allowable parameters
        far = min(zoning.max_far * 0.9, zoning.max_far)
        height = min(zoning.max_height_ft * 0.95, zoning.max_height_ft)
        
        # Target the requested unit count or calculate based on moderate density
        target_units = target_metrics.units or int(lot_area * far / 700)  # ~700 sq ft per unit
        total_units = min(target_units, int(lot_area * far / 600))  # Max density check
        
        # Enhanced affordability based on intent
        affordability_boost = 1.2 if str(intent) in ["anti_displacement", "housing_development"] else 1.0
        affordable_pct = min((zoning.affordable_housing_req or 0.20) * affordability_boost, 0.30)
        affordable_units = int(total_units * affordable_pct)
        
        # Parking reduction potential
        parking_reduction = 0.7 if neighborhood.spatial.transit_access == "excellent" else 0.9
        parking_spaces = int(total_units * zoning.min_parking * parking_reduction)
        
        variances = []
        if parking_reduction < 0.9:
            variances.append("parking_reduction")
        
        feasibility = PlanFeasibility.REQUIRES_VARIANCES if variances else PlanFeasibility.FULLY_COMPLIANT
        
        return DevelopmentPlan(
            plan_id=f"{neighborhood.name}_moderate_001",
            plan_type=PlanType.MODERATE,
            name=f"Moderate {neighborhood.display_name} Development",
            description="Balanced approach optimizing units while maintaining neighborhood character",
            far=far,
            height_ft=int(height),
            total_units=total_units,
            lot_area_sf=lot_area,
            affordable_units=affordable_units,
            affordable_percentage=affordable_pct,
            parking_spaces=parking_spaces,
            ground_floor_commercial_sf=1000 if zoning.ground_floor_commercial else 0,
            feasibility=feasibility,
            zoning_compliance=f"{zoning.zone_type} compliant" + (" with variances" if variances else ""),
            required_variances=variances,
            design_rationale=[
                "Balanced density and community fit",
                "Enhanced affordability targets",
                "Transit-oriented parking optimization" if variances else "Standard parking provision"
            ],
            policy_alignment=[
                "SF Planning Code alignment",
                "Enhanced inclusionary housing",
                "Transit-supportive design" if variances else "Standard zoning compliance"
            ],
            compliance_score=0.85 if variances else 0.90
        )
    
    def _generate_aggressive_plan(self, neighborhood, target_metrics, intent, lot_area) -> DevelopmentPlan:
        """Generate aggressive plan maximizing development potential"""
        zoning = neighborhood.zoning
        
        # Aggressive approach: Push to maximum allowable limits
        far = zoning.max_far
        height = zoning.max_height_ft
        
        # Maximum density calculation
        total_units = int(lot_area * far / 550)  # ~550 sq ft per unit (compact)
        
        # High affordability targets
        affordable_pct = min((zoning.affordable_housing_req or 0.20) * 1.5, 0.35)
        affordable_units = int(total_units * affordable_pct)
        
        # Aggressive parking reduction
        parking_spaces = int(total_units * max(zoning.min_parking * 0.5, 0.25))
        
        # Likely required variances for aggressive development
        variances = ["parking_reduction"]
        if total_units > lot_area * zoning.max_far / 600:  # High density variance
            variances.append("density_bonus")
        if affordable_pct > zoning.affordable_housing_req * 1.3:
            variances.append("affordability_bonus")
        
        return DevelopmentPlan(
            plan_id=f"{neighborhood.name}_aggressive_001",
            plan_type=PlanType.AGGRESSIVE,
            name=f"Maximum Density {neighborhood.display_name} Development",
            description="High-impact development maximizing units and affordability",
            far=far,
            height_ft=height,
            total_units=total_units,
            lot_area_sf=lot_area,
            affordable_units=affordable_units,
            affordable_percentage=affordable_pct,
            parking_spaces=parking_spaces,
            ground_floor_commercial_sf=1500 if zoning.ground_floor_commercial else 0,
            feasibility=PlanFeasibility.REQUIRES_VARIANCES,
            zoning_compliance=f"{zoning.zone_type} maximum density with multiple variances",
            required_variances=variances,
            design_rationale=[
                "Maximum allowable density",
                "Highest feasible affordability percentage", 
                "Transit-oriented minimal parking",
                "Active ground floor commercial" if zoning.ground_floor_commercial else "Residential focus"
            ],
            policy_alignment=[
                "Affordable housing maximization",
                "Transit-oriented development",
                "Density bonus program eligibility"
            ],
            compliance_score=0.70
        )
    
    def _generate_innovative_plan(self, neighborhood, target_metrics, intent, lot_area) -> DevelopmentPlan:
        """Generate innovative plan with intent-specific creative solutions"""
        zoning = neighborhood.zoning
        
        # Base parameters similar to moderate
        far = zoning.max_far * 0.85
        height = int(zoning.max_height_ft * 0.90)
        
        # Intent-specific innovations
        if str(intent) == "anti_displacement":
            # Community ownership model
            total_units = int(lot_area * far / 650)
            affordable_units = int(total_units * 0.40)  # 40% affordable
            
            return DevelopmentPlan(
                plan_id=f"{neighborhood.name}_innovative_displacement_001",
                plan_type=PlanType.INNOVATIVE,
                name=f"Community Land Trust {neighborhood.display_name}",
                description="Anti-displacement development with community ownership model",
                far=far, height_ft=height, total_units=total_units, lot_area_sf=lot_area,
                affordable_units=affordable_units, affordable_percentage=0.40,
                parking_spaces=int(total_units * 0.6),
                ground_floor_commercial_sf=800,
                feasibility=PlanFeasibility.NEEDS_REZONING,
                zoning_compliance="Requires community benefit zoning",
                required_variances=["community_ownership", "enhanced_affordability"],
                design_rationale=[
                    "Community land trust model",
                    "40% permanently affordable units",
                    "Local business preservation space",
                    "Resident equity building"
                ],
                policy_alignment=[
                    "Anti-displacement policy",
                    "Community ownership priority",
                    "Cultural preservation"
                ],
                compliance_score=0.75
            )
        
        elif str(intent) == "climate_resilience":
            # Elevated, resilient design
            total_units = int(lot_area * far / 700)
            
            return DevelopmentPlan(
                plan_id=f"{neighborhood.name}_innovative_climate_001", 
                plan_type=PlanType.INNOVATIVE,
                name=f"Climate-Resilient {neighborhood.display_name}",
                description="Elevated development with flood adaptation and green infrastructure",
                far=far, height_ft=height + 5, total_units=total_units, lot_area_sf=lot_area,
                affordable_units=int(total_units * (zoning.affordable_housing_req or 0.20)),
                affordable_percentage=zoning.affordable_housing_req or 0.20,
                parking_spaces=int(total_units * 0.4),  # Elevated parking
                ground_floor_commercial_sf=0,  # Elevated design
                feasibility=PlanFeasibility.REQUIRES_VARIANCES,
                zoning_compliance="Climate adaptation design standards",
                required_variances=["elevated_construction", "flood_adaptation"],
                design_rationale=[
                    "Elevated above flood zones",
                    "Green infrastructure integration",
                    "Climate-adaptive building systems",
                    "Resilient community space"
                ],
                policy_alignment=[
                    "Climate adaptation strategy",
                    "Flood resilience requirements",
                    "Green building standards"
                ],
                compliance_score=0.80
            )
        
        else:  # walkability_improvement
            # Mixed-use walkability focus
            total_units = int(lot_area * far / 750)
            
            return DevelopmentPlan(
                plan_id=f"{neighborhood.name}_innovative_walkability_001",
                plan_type=PlanType.INNOVATIVE,
                name=f"Walkable {neighborhood.display_name} Hub",
                description="Mixed-use development optimizing pedestrian experience",
                far=far, height_ft=height, total_units=total_units, lot_area_sf=lot_area,
                affordable_units=int(total_units * (zoning.affordable_housing_req or 0.20)),
                affordable_percentage=zoning.affordable_housing_req or 0.20,
                parking_spaces=int(total_units * 0.3),  # Minimal parking
                ground_floor_commercial_sf=2000,  # Extensive ground floor
                feasibility=PlanFeasibility.REQUIRES_VARIANCES,
                zoning_compliance="Mixed-use walkability optimization",
                required_variances=["parking_reduction", "pedestrian_priority_design"],
                design_rationale=[
                    "Extensive ground floor activation",
                    "Minimal parking for walkability",
                    "Pedestrian-priority design",
                    "Neighborhood amenity integration"
                ],
                policy_alignment=[
                    "Walkability improvement goals",
                    "Active transportation support",
                    "Neighborhood commercial vitality"
                ],
                compliance_score=0.78
            )
    
    def _extract_planning_context(self, research_brief: Any) -> Dict[str, List[str]]:
        """Extract zoning opportunities, challenges, and community considerations"""
        return {
            "zoning_opportunities": research_brief.key_opportunities,
            "regulatory_challenges": research_brief.major_constraints,
            "community_considerations": research_brief.policy_considerations
        }


# Example usage and testing
if __name__ == "__main__":
    # Test cases will be added after implementation
    planner = PlannerAgent()
    
    print("Agent 2 (Planner) interface contracts defined")
    print("Ready for implementation of scenario generation modules")