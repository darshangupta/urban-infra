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

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card className="text-center p-4">
              <CardTitle className="text-2xl text-blue-600">
                {comparison.neighborhood}
              </CardTitle>
              <CardDescription>Target Area</CardDescription>
            </Card>
            <Card className="text-center p-4">
              <CardTitle className="text-2xl text-green-600">
                {comparison.alternatives.length}
              </CardTitle>
              <CardDescription>Planning Options</CardDescription>
            </Card>
            <Card className="text-center p-4">
              <CardTitle className="text-2xl text-purple-600">
                {new Set(comparison.alternatives.map(plan => plan.type)).size}
              </CardTitle>
              <CardDescription>Intervention Types</CardDescription>
            </Card>
            <Card className="text-center p-4">
              <CardTitle className="text-2xl text-yellow-600">
                {comparison.alternatives.reduce((sum, plan) => sum + plan.amenities.length, 0)}
              </CardTitle>
              <CardDescription>Total Amenities</CardDescription>
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