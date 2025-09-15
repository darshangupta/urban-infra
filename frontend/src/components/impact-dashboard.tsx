'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Home, 
  MapPin, 
  Users, 
  DollarSign, 
  Leaf, 
  TrendingUp, 
  TrendingDown,
  AlertCircle,
  CheckCircle2,
  Info
} from 'lucide-react';
import type { ComprehensiveImpact, ImpactMetric } from '@/lib/api';

interface ImpactDashboardProps {
  impact: ComprehensiveImpact;
  planTitle: string;
}

export function ImpactDashboard({ impact, planTitle }: ImpactDashboardProps) {
  const categories = ['housing', 'accessibility', 'equity', 'economic', 'environmental'] as const;
  
  const IMPACT_ICONS = {
    housing: Home,
    accessibility: MapPin,
    equity: Users,
    economic: DollarSign,
    environmental: Leaf,
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">Impact Analysis</CardTitle>
          <CardDescription>{planTitle}</CardDescription>
        </CardHeader>
      </Card>

      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="housing">Housing</TabsTrigger>
          <TabsTrigger value="accessibility">Access</TabsTrigger>
          <TabsTrigger value="equity">Equity</TabsTrigger>
          <TabsTrigger value="economic">Economic</TabsTrigger>
          <TabsTrigger value="environmental">Environmental</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            {categories.map((category) => {
              const categoryData = impact[category as keyof ComprehensiveImpact];
              const Icon = IMPACT_ICONS[category];
              const firstMetric = Object.values((categoryData as any).metrics)[0] as ImpactMetric;
              const change = firstMetric ? firstMetric.after - firstMetric.before : 0;

              return (
                <Card key={category}>
                  <CardHeader className="pb-2">
                    <CardTitle className="flex items-center gap-2 text-sm">
                      <Icon className="h-4 w-4" />
                      {category.charAt(0).toUpperCase() + category.slice(1)}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center gap-1">
                      {change > 0 ? (
                        <TrendingUp className="h-3 w-3 text-green-500" />
                      ) : change < 0 ? (
                        <TrendingDown className="h-3 w-3 text-red-500" />
                      ) : null}
                      <span className={`text-lg font-semibold ${
                        change > 0 ? 'text-green-600' : 
                        change < 0 ? 'text-red-600' : 'text-gray-500'
                      }`}>
                        {change > 0 ? '+' : ''}{change.toFixed(1)}
                      </span>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          {impact.overall_assessment && (
            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>{impact.overall_assessment}</AlertDescription>
            </Alert>
          )}
        </TabsContent>

        {categories.map((category) => {
          const categoryData = impact[category as keyof ComprehensiveImpact];
          const Icon = IMPACT_ICONS[category];

          return (
            <TabsContent key={category} value={category}>
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Icon className="h-5 w-5" />
                    {category.charAt(0).toUpperCase() + category.slice(1)} Impact
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {Object.entries((categoryData as any).metrics).map(([key, metric]) => {
                    const m = metric as ImpactMetric;
                    const change = m.after - m.before;
                    const percentChange = m.before !== 0 ? (change / m.before) * 100 : 0;

                    return (
                      <div key={key} className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="font-medium">{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                          <Badge variant={change > 0 ? "default" : change < 0 ? "destructive" : "secondary"}>
                            {change > 0 ? '+' : ''}{change.toFixed(1)} ({percentChange > 0 ? '+' : ''}{percentChange.toFixed(1)}%)
                          </Badge>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4 text-sm text-muted-foreground">
                          <div>Before: {m.before.toFixed(1)}{m.unit}</div>
                          <div>After: {m.after.toFixed(1)}{m.unit}</div>
                        </div>
                        
                        <div>
                          <div className="flex justify-between text-xs mb-1">
                            <span>Confidence</span>
                            <span>{Math.round(m.confidence * 100)}%</span>
                          </div>
                          <Progress value={m.confidence * 100} className="h-2" />
                        </div>
                      </div>
                    );
                  })}

                  <Separator />

                  {(categoryData as any).benefits && (categoryData as any).benefits.length > 0 && (
                    <Alert>
                      <CheckCircle2 className="h-4 w-4" />
                      <AlertDescription>
                        <strong>Specific Benefits:</strong>
                        <ul className="mt-2 space-y-1">
                          {(categoryData as any).benefits.map((benefit: string, index: number) => (
                            <li key={index} className="text-sm">• {benefit}</li>
                          ))}
                        </ul>
                      </AlertDescription>
                    </Alert>
                  )}

                  {(categoryData as any).concerns && (categoryData as any).concerns.length > 0 && (
                    <Alert variant="destructive">
                      <AlertCircle className="h-4 w-4" />
                      <AlertDescription>
                        <strong>Potential Concerns:</strong>
                        <ul className="mt-2 space-y-1">
                          {(categoryData as any).concerns.map((concern: string, index: number) => (
                            <li key={index} className="text-sm">• {concern}</li>
                          ))}
                        </ul>
                      </AlertDescription>
                    </Alert>
                  )}

                  {(categoryData as any).mitigation_strategies && (categoryData as any).mitigation_strategies.length > 0 && (
                    <Alert>
                      <Info className="h-4 w-4" />
                      <AlertDescription>
                        <strong>Mitigation Strategies:</strong>
                        <ul className="mt-2 space-y-1">
                          {(categoryData as any).mitigation_strategies.map((strategy: string, index: number) => (
                            <li key={index} className="text-sm">• {strategy}</li>
                          ))}
                        </ul>
                      </AlertDescription>
                    </Alert>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          );
        })}
      </Tabs>
    </div>
  );
}