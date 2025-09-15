'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { QueryInput } from '@/components/query-input';
import { ImpactDashboard } from '@/components/impact-dashboard';
import { PlanComparison } from '@/components/plan-comparison';
import { UrbanPlanningAPI } from '@/lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import { ArrowLeft, AlertCircle, Building2 } from 'lucide-react';
import type { AnalysisResult, PlanningAlternative } from '@/lib/api';

const api = new UrbanPlanningAPI();

export default function Home() {
  const [currentQuery, setCurrentQuery] = useState<string>('');
  const [selectedPlan, setSelectedPlan] = useState<PlanningAlternative | null>(null);

  const {
    data: analysisResult,
    error,
    isLoading,
    refetch,
  } = useQuery<AnalysisResult>({
    queryKey: ['urban-analysis', currentQuery],
    queryFn: () => api.analyzeQuery(currentQuery),
    enabled: !!currentQuery,
    staleTime: 5 * 60 * 1000,
    retry: 2,
  });

  const handleSubmitQuery = (query: string) => {
    setCurrentQuery(query);
    setSelectedPlan(null);
  };

  const handleSelectPlan = (plan: PlanningAlternative) => {
    setSelectedPlan(plan);
  };

  const handleBackToPlans = () => {
    setSelectedPlan(null);
  };

  return (
    <main className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="space-y-8">
          {/* Header */}
          <Card>
            <CardHeader className="text-center">
              <CardTitle className="text-4xl font-bold flex items-center justify-center gap-3">
                <Building2 className="h-10 w-10 text-blue-600" />
                Urban Planning Analysis
              </CardTitle>
              <CardDescription className="text-xl max-w-2xl mx-auto">
                AI-powered impact analysis for San Francisco neighborhoods. 
                Ask questions about housing, development, and urban planning.
              </CardDescription>
            </CardHeader>
          </Card>

          {/* Query Input */}
          <QueryInput onSubmit={handleSubmitQuery} isLoading={isLoading} />

          {/* Loading State */}
          {isLoading && (
            <Card>
              <CardContent className="py-12">
                <div className="text-center space-y-4">
                  <div className="flex justify-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                  </div>
                  <div className="space-y-2">
                    <p className="text-lg font-medium">Analyzing urban planning impacts...</p>
                    <p className="text-muted-foreground">This may take a few moments</p>
                  </div>
                  <div className="space-y-2 max-w-md mx-auto">
                    <Skeleton className="h-4 w-full" />
                    <Skeleton className="h-4 w-3/4 mx-auto" />
                    <Skeleton className="h-4 w-1/2 mx-auto" />
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Error State */}
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription className="flex items-center justify-between">
                <div>
                  <strong>Analysis Failed:</strong> {error instanceof Error ? error.message : 'An unexpected error occurred'}
                </div>
                <Button onClick={() => refetch()} variant="outline" size="sm">
                  Try Again
                </Button>
              </AlertDescription>
            </Alert>
          )}

          {/* Results */}
          {analysisResult && !isLoading && (
            <div className="space-y-6">
              {/* Back Button - Show when plan is selected */}
              {selectedPlan && (
                <Button 
                  onClick={handleBackToPlans} 
                  variant="outline"
                  className="mb-4"
                >
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Plans
                </Button>
              )}

              {/* Plan Comparison - Show if no plan selected */}
              {!selectedPlan && (
                <PlanComparison 
                  comparison={analysisResult}
                  onSelectPlan={handleSelectPlan}
                />
              )}

              {/* Impact Dashboard - Show if plan selected */}
              {selectedPlan && (
                <ImpactDashboard 
                  impact={analysisResult.impact}
                  planTitle={selectedPlan.title}
                />
              )}
            </div>
          )}

          {/* Welcome State - Show when no query has been made */}
          {!currentQuery && !isLoading && (
            <Card>
              <CardHeader>
                <CardTitle>Get Started</CardTitle>
                <CardDescription>
                  Ask a question about urban planning in San Francisco neighborhoods to see detailed impact analysis
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <h3 className="font-medium mb-2">Housing Impact</h3>
                    <p className="text-muted-foreground">Analyze how development affects housing availability, affordability, and displacement</p>
                  </div>
                  <div className="p-4 bg-green-50 rounded-lg">
                    <h3 className="font-medium mb-2">Transit & Access</h3>
                    <p className="text-muted-foreground">Evaluate walkability, transit access, and neighborhood connectivity</p>
                  </div>
                  <div className="p-4 bg-purple-50 rounded-lg">
                    <h3 className="font-medium mb-2">Community Equity</h3>
                    <p className="text-muted-foreground">Assess equity impacts and community benefits of planning decisions</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Footer */}
          <Card>
            <CardContent className="py-4">
              <p className="text-center text-muted-foreground text-sm">
                Urban Infrastructure Planning System - Powered by AI for San Francisco neighborhoods
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </main>
  );
}
