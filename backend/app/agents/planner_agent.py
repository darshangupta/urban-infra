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
        # This is the interface contract - implementation comes next
        raise NotImplementedError("Implementation pending")
    
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
        raise NotImplementedError("Implementation pending")
    
    def _optimize_plans(self, plans: List[DevelopmentPlan], research_brief: Any) -> List[DevelopmentPlan]:
        """Rank and optimize plans based on feasibility and policy alignment"""
        raise NotImplementedError("Implementation pending")
    
    def _generate_comparative_analysis(self, plans: List[DevelopmentPlan], 
                                     research_brief: Any) -> Dict[str, Any]:
        """Generate comparative analysis and tradeoffs between plans"""
        raise NotImplementedError("Implementation pending")
    
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