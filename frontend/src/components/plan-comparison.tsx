'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Home, 
  MapPin, 
  Users, 
  DollarSign, 
  Leaf,
  Star,
  ChevronRight,
  Info
} from 'lucide-react';
import type { AnalysisResult, PlanningAlternative, ImpactMetric } from '@/lib/api';

interface PlanComparisonProps {
  comparison: AnalysisResult;
  onSelectPlan: (plan: PlanningAlternative) => void;
}

export function PlanComparison({ comparison, onSelectPlan }: PlanComparisonProps) {
  const IMPACT_ICONS = {
    housing: Home,
    accessibility: MapPin,
    equity: Users,
    economic: DollarSign,
    environmental: Leaf,
  };

  const totalPlans = comparison.alternatives.length;
  const recommendedPlan = comparison.alternatives.find(plan => 
    plan.title === comparison.recommended
  );
  
  // Calculate solution sophistication metrics
  const calculateOverallImpactScore = () => {
    const metrics = comparison.impact;
    let totalScore = 0;
    let totalMetrics = 0;
    
    (['housing', 'accessibility', 'equity', 'economic', 'environmental'] as const).forEach(category => {
      const categoryMetrics = metrics[category].metrics;
      Object.values(categoryMetrics).forEach((metric) => {
        const change = Math.abs(metric.after - metric.before);
        const weightedScore = (change * metric.confidence);
        totalScore += weightedScore;
        totalMetrics += 1;
      });
    });
    
    return totalMetrics > 0 ? Math.round((totalScore / totalMetrics) * 10) : 0;
  };
  
  const calculateCrossCategoryBenefits = () => {
    let totalBenefits = 0;
    (['housing', 'accessibility', 'equity', 'economic', 'environmental'] as const).forEach(category => {
      totalBenefits += comparison.impact[category].benefits.length;
    });
    return totalBenefits;
  };
  
  const calculateSystemicIntegration = () => {
    // Count intervention types and their interconnectedness
    const interventionTypes = new Set(comparison.alternatives.map(alt => alt.type));
    const avgAmenities = comparison.alternatives.reduce((sum, alt) => sum + alt.amenities.length, 0) / comparison.alternatives.length;
    
    // Higher score for more diverse interventions and richer amenity profiles
    return Math.min(100, Math.round((interventionTypes.size * 15) + (avgAmenities * 8)));
  };
  
  const calculateImplementationComplexity = () => {
    // Based on intervention types - infrastructure and policy are more complex
    let complexityScore = 0;
    comparison.alternatives.forEach(alt => {
      if (alt.type.includes('street') || alt.type.includes('infrastructure')) complexityScore += 3;
      else if (alt.type.includes('policy') || alt.type.includes('zoning')) complexityScore += 4;
      else if (alt.type.includes('business') || alt.type.includes('economic')) complexityScore += 2;
      else complexityScore += 1;
    });
    
    const avgComplexity = complexityScore / comparison.alternatives.length;
    return avgComplexity <= 1.5 ? 'Low' : avgComplexity <= 2.5 ? 'Medium' : 'High';
  };

  const calculatePoliticalFeasibility = () => {
    // Based on SF planning precedents and intervention types
    let feasibilityScore = 70; // Base score for SF
    
    comparison.alternatives.forEach(alt => {
      // Policy and zoning changes are politically challenging
      if (alt.type.includes('policy') || alt.type.includes('zoning')) feasibilityScore -= 15;
      // Housing generally has political support
      else if (alt.type.includes('housing') || alt.type.includes('affordable')) feasibilityScore += 10;
      // Environmental and community programs have broad support
      else if (alt.type.includes('environmental') || alt.type.includes('community')) feasibilityScore += 5;
      // Infrastructure depends on funding
      else if (alt.type.includes('infrastructure')) feasibilityScore -= 5;
    });
    
    // Neighborhood-specific adjustments
    if (comparison.neighborhood.toLowerCase().includes('marina')) feasibilityScore -= 10; // NIMBY tendencies
    else if (comparison.neighborhood.toLowerCase().includes('mission')) feasibilityScore += 5; // Pro-development activism
    else if (comparison.neighborhood.toLowerCase().includes('hayes')) feasibilityScore += 8; // Transit-oriented support
    
    return Math.max(20, Math.min(90, feasibilityScore));
  };

  const getFundingPathwayClarity = () => {
    const interventionTypes = new Set(comparison.alternatives.map(alt => alt.type));
    let clarity = 0;
    
    // Count available funding mechanisms
    if (Array.from(interventionTypes).some(type => type.includes('housing') || type.includes('affordable'))) {
      clarity += 25; // Housing Bond, MOHCD, State HCD
    }
    if (Array.from(interventionTypes).some(type => type.includes('environmental') || type.includes('climate'))) {
      clarity += 20; // Climate bonds, green infrastructure funds
    }
    if (Array.from(interventionTypes).some(type => type.includes('infrastructure') || type.includes('street'))) {
      clarity += 30; // Federal infrastructure, MTC funds
    }
    if (Array.from(interventionTypes).some(type => type.includes('community') || type.includes('business'))) {
      clarity += 15; // Community development block grants
    }
    if (Array.from(interventionTypes).some(type => type.includes('policy'))) {
      clarity += 10; // General fund, planning grants
    }
    
    return Math.min(100, clarity);
  };

  const getRegulatoryComplexity = () => {
    const interventionTypes = comparison.alternatives.map(alt => alt.type);
    
    // Count regulatory hurdles
    const hasZoningChanges = interventionTypes.some(type => type.includes('zoning') || type.includes('policy'));
    const hasInfrastructure = interventionTypes.some(type => type.includes('infrastructure') || type.includes('street'));
    const hasEnvironmental = interventionTypes.some(type => type.includes('environmental'));
    const hasHousing = interventionTypes.some(type => type.includes('housing'));
    
    let complexity = 0;
    if (hasZoningChanges) complexity += 30; // Planning Commission, Board of Supervisors
    if (hasInfrastructure) complexity += 25; // Public Works, MTA, utilities
    if (hasEnvironmental) complexity += 20; // Environmental review, CEQA
    if (hasHousing) complexity += 15; // MOHCD review, inclusionary requirements
    
    if (complexity <= 20) return 'Low';
    else if (complexity <= 40) return 'Medium';
    else if (complexity <= 60) return 'High';
    else return 'Very High';
  };

  const getCommunitySupport = () => {
    let support = 60; // Base community support in SF
    
    comparison.alternatives.forEach(alt => {
      // Affordable housing generally supported
      if (alt.type.includes('affordable') || alt.type.includes('community')) support += 15;
      // Environmental improvements popular
      else if (alt.type.includes('environmental') || alt.type.includes('climate')) support += 12;
      // Transit improvements supported
      else if (alt.type.includes('transit') || alt.type.includes('pedestrian')) support += 8;
      // Market-rate housing more controversial
      else if (alt.type.includes('housing') && !alt.type.includes('affordable')) support += 2;
      // Business development mixed reception
      else if (alt.type.includes('business') || alt.type.includes('commercial')) support += 5;
      // Policy changes can be divisive
      else if (alt.type.includes('policy')) support -= 5;
    });
    
    // Neighborhood-specific factors
    if (comparison.neighborhood.toLowerCase().includes('mission')) {
      support += 10; // Strong community engagement
    } else if (comparison.neighborhood.toLowerCase().includes('marina')) {
      support -= 8; // More resistance to change
    }
    
    return Math.max(30, Math.min(85, support));
  };

  return (
    <div className="space-y-6">
      {/* Summary Card */}
      <Card>
        <CardHeader>
          <CardTitle>Scenario Analysis Summary</CardTitle>
          <CardDescription>
            Analysis of {totalPlans} planning alternatives for your query
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {recommendedPlan && (
            <Alert>
              <Star className="h-4 w-4" />
              <AlertDescription>
                <strong>Recommended: {recommendedPlan.title}</strong><br />
                {comparison.recommendation_rationale}
              </AlertDescription>
            </Alert>
          )}

          {/* Query Intelligence Dashboard */}
          <Alert className="border-blue-200 bg-blue-50">
            <Info className="h-4 w-4" />
            <AlertDescription>
              <div className="space-y-2">
                <div className="font-medium">AI Query Analysis</div>
                <div className="text-sm space-y-1">
                  <div>
                    <span className="font-medium">Detected Intent:</span> {comparison.intent.type} planning 
                    ({comparison.intent.priority} priority, {comparison.intent.density} density)
                  </div>
                  <div>
                    <span className="font-medium">Focus Area:</span> {comparison.intent.focus.replace('_', ' ')}
                  </div>
                  <div>
                    <span className="font-medium">Interpretation Confidence:</span> {Math.round(comparison.intent.confidence * 100)}%
                    <span className="ml-2 text-xs text-muted-foreground">
                      ({comparison.intent.confidence >= 0.8 ? 'High' : comparison.intent.confidence >= 0.6 ? 'Medium' : 'Low'} certainty)
                    </span>
                  </div>
                  <div className="text-xs text-muted-foreground mt-2">
                    The system analyzed "{comparison.query}" and generated {comparison.alternatives.length} contextually relevant alternatives 
                    focused on {comparison.intent.type} interventions.
                  </div>
                </div>
              </div>
            </AlertDescription>
          </Alert>

          {/* Solution Sophistication Metrics */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Solution Analysis</CardTitle>
              <CardDescription>Sophistication and integration metrics for generated alternatives</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center p-3 bg-blue-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">{calculateOverallImpactScore()}</div>
                  <div className="text-sm text-muted-foreground">Impact Score</div>
                  <div className="text-xs text-muted-foreground mt-1">
                    Weighted change across all categories
                  </div>
                </div>
                <div className="text-center p-3 bg-green-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">{calculateCrossCategoryBenefits()}</div>
                  <div className="text-sm text-muted-foreground">Total Benefits</div>
                  <div className="text-xs text-muted-foreground mt-1">
                    Cross-category positive impacts
                  </div>
                </div>
                <div className="text-center p-3 bg-purple-50 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">{calculateSystemicIntegration()}</div>
                  <div className="text-sm text-muted-foreground">Integration %</div>
                  <div className="text-xs text-muted-foreground mt-1">
                    System interconnectedness
                  </div>
                </div>
                <div className="text-center p-3 bg-yellow-50 rounded-lg">
                  <div className="text-2xl font-bold text-yellow-600">{calculateImplementationComplexity()}</div>
                  <div className="text-sm text-muted-foreground">Complexity</div>
                  <div className="text-xs text-muted-foreground mt-1">
                    Implementation difficulty
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Implementation Reality Indicators */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Implementation Reality Check</CardTitle>
              <CardDescription>Feasibility assessment based on SF planning precedents</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center p-3 bg-indigo-50 rounded-lg">
                  <div className="text-2xl font-bold text-indigo-600">{calculatePoliticalFeasibility()}%</div>
                  <div className="text-sm text-muted-foreground">Political Feasibility</div>
                  <div className="text-xs text-muted-foreground mt-1">
                    Based on SF precedents
                  </div>
                </div>
                <div className="text-center p-3 bg-emerald-50 rounded-lg">
                  <div className="text-2xl font-bold text-emerald-600">{getFundingPathwayClarity()}%</div>
                  <div className="text-sm text-muted-foreground">Funding Clarity</div>
                  <div className="text-xs text-muted-foreground mt-1">
                    Available funding sources
                  </div>
                </div>
                <div className="text-center p-3 bg-orange-50 rounded-lg">
                  <div className="text-2xl font-bold text-orange-600">{getRegulatoryComplexity()}</div>
                  <div className="text-sm text-muted-foreground">Regulatory Load</div>
                  <div className="text-xs text-muted-foreground mt-1">
                    Approval complexity
                  </div>
                </div>
                <div className="text-center p-3 bg-rose-50 rounded-lg">
                  <div className="text-2xl font-bold text-rose-600">{getCommunitySupport()}%</div>
                  <div className="text-sm text-muted-foreground">Community Support</div>
                  <div className="text-xs text-muted-foreground mt-1">
                    Neighborhood acceptance
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Dynamic Context Cards based on Query Intent */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {/* Card 1: Target Area (Always shown) */}
            <Card className="text-center p-4">
              <CardTitle className="text-2xl text-blue-600">
                {comparison.neighborhood}
              </CardTitle>
              <CardDescription>Target Area</CardDescription>
            </Card>
            
            {/* Card 2: Intent-specific primary metric */}
            <Card className="text-center p-4">
              <CardTitle className="text-2xl text-green-600">
                {(() => {
                  switch (comparison.intent.type) {
                    case 'environmental':
                      return comparison.alternatives.filter(alt => alt.type.includes('park') || alt.type.includes('climate') || alt.type.includes('green')).length;
                    case 'transit':
                      return comparison.alternatives.filter(alt => alt.type.includes('street') || alt.type.includes('transit') || alt.type.includes('pedestrian')).length;
                    case 'economic':
                      return comparison.alternatives.filter(alt => alt.type.includes('business') || alt.type.includes('commercial')).length;
                    case 'housing':
                      return comparison.alternatives.reduce((sum, plan) => sum + plan.units, 0);
                    default:
                      return comparison.alternatives.length;
                  }
                })()}
              </CardTitle>
              <CardDescription>
                {(() => {
                  switch (comparison.intent.type) {
                    case 'environmental':
                      return 'Green Solutions';
                    case 'transit':
                      return 'Mobility Options';
                    case 'economic':
                      return 'Business Solutions';
                    case 'housing':
                      return 'Total Units';
                    default:
                      return 'Planning Options';
                  }
                })()}
              </CardDescription>
            </Card>
            
            {/* Card 3: Confidence & Complexity */}
            <Card className="text-center p-4">
              <CardTitle className="text-2xl text-purple-600">
                {Math.round(comparison.intent.confidence * 100)}%
              </CardTitle>
              <CardDescription>Intent Confidence</CardDescription>
            </Card>
            
            {/* Card 4: Intent-specific secondary metric */}
            <Card className="text-center p-4">
              <CardTitle className="text-2xl text-yellow-600">
                {(() => {
                  switch (comparison.intent.type) {
                    case 'environmental':
                      const envAmenities = comparison.alternatives.reduce((sum, plan) => 
                        sum + plan.amenities.filter(amenity => 
                          amenity.toLowerCase().includes('green') || 
                          amenity.toLowerCase().includes('park') || 
                          amenity.toLowerCase().includes('garden') ||
                          amenity.toLowerCase().includes('tree') ||
                          amenity.toLowerCase().includes('climate')
                        ).length, 0);
                      return envAmenities;
                    case 'transit':
                      const transitAmenities = comparison.alternatives.reduce((sum, plan) => 
                        sum + plan.amenities.filter(amenity => 
                          amenity.toLowerCase().includes('bike') || 
                          amenity.toLowerCase().includes('transit') || 
                          amenity.toLowerCase().includes('pedestrian') ||
                          amenity.toLowerCase().includes('street')
                        ).length, 0);
                      return transitAmenities;
                    case 'economic':
                      const businessAmenities = comparison.alternatives.reduce((sum, plan) => 
                        sum + plan.amenities.filter(amenity => 
                          amenity.toLowerCase().includes('business') || 
                          amenity.toLowerCase().includes('commercial') || 
                          amenity.toLowerCase().includes('retail') ||
                          amenity.toLowerCase().includes('workspace')
                        ).length, 0);
                      return businessAmenities;
                    case 'housing':
                      return Math.round(comparison.alternatives.reduce((sum, plan) => sum + (plan.units * plan.affordable_percentage / 100), 0));
                    default:
                      return new Set(comparison.alternatives.map(plan => plan.type)).size;
                  }
                })()}
              </CardTitle>
              <CardDescription>
                {(() => {
                  switch (comparison.intent.type) {
                    case 'environmental':
                      return 'Green Features';
                    case 'transit':
                      return 'Mobility Features';
                    case 'economic':
                      return 'Business Features';
                    case 'housing':
                      return 'Affordable Units';
                    default:
                      return 'Intervention Types';
                  }
                })()}
              </CardDescription>
            </Card>
          </div>
        </CardContent>
      </Card>
      
      {/* Plans Grid */}
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <h3 className="text-xl font-semibold">Planning Alternatives</h3>
          <Info className="h-4 w-4 text-muted-foreground" />
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {comparison.alternatives.map((plan, index) => {
            const isRecommended = plan.title === comparison.recommended;
            
            return (
              <Card key={index} className={`transition-all hover:shadow-md ${isRecommended ? 'ring-2 ring-blue-500' : ''}`}>
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg flex items-center gap-2">
                      {plan.title}
                      {isRecommended && <Star className="h-4 w-4 text-yellow-500 fill-yellow-500" />}
                    </CardTitle>
                    {isRecommended && <Badge>Recommended</Badge>}
                  </div>
                  <CardDescription>{plan.description}</CardDescription>
                </CardHeader>
                
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-muted-foreground">Total Units: </span>
                      <span className="font-medium">{plan.total_units}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Affordable: </span>
                      <span className="font-medium">{plan.affordable_units} ({Math.round((plan.affordable_units / plan.total_units) * 100)}%)</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Height: </span>
                      <span className="font-medium">{plan.height_ft}ft</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">FAR: </span>
                      <span className="font-medium">{plan.far}</span>
                    </div>
                  </div>

                  {plan.amenities && plan.amenities.length > 0 && (
                    <div className="space-y-2">
                      <h4 className="text-sm font-medium">Amenities</h4>
                      <div className="flex flex-wrap gap-1">
                        {plan.amenities.map((amenity, index) => (
                          <Badge key={index} variant="secondary" className="text-xs">
                            {amenity}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="space-y-2">
                    <h4 className="text-sm font-medium">Impact Overview</h4>
                    <div className="grid grid-cols-5 gap-2">
                      {(['housing', 'accessibility', 'equity', 'economic', 'environmental'] as const).map((category) => {
                        const categoryData = comparison.impact[category];
                        const primaryMetric = Object.values(categoryData.metrics)[0] as ImpactMetric;
                        const change = primaryMetric.after - primaryMetric.before;
                        const Icon = IMPACT_ICONS[category];

                        return (
                          <div key={category} className="text-center">
                            <Icon className="h-4 w-4 mx-auto mb-1 text-muted-foreground" />
                            <Badge 
                              variant={change > 0 ? "default" : change < 0 ? "destructive" : "secondary"}
                              className="text-xs"
                            >
                              {change > 0 ? '+' : ''}{change.toFixed(1)}
                            </Badge>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  <Button 
                    className="w-full" 
                    variant={isRecommended ? "default" : "outline"}
                    onClick={() => onSelectPlan(plan)}
                  >
                    View Details
                    <ChevronRight className="h-4 w-4 ml-1" />
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </div>
  );
}