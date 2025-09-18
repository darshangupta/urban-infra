'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { QueryInput } from '@/components/query-input';
import { ExploratoryCanvas } from '@/components/exploratory-canvas';
import { AnalyticsDashboard } from '@/components/analytics-dashboard';
import { ThemeToggle } from '@/components/theme-toggle';
import { ErrorBoundary, EmptyState, AnalyticsLoadingSkeleton } from '@/components/error-boundary';
import { UrbanPlanningAPI } from '@/lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import { AlertCircle, Building2, Search } from 'lucide-react';
import type { ExploratoryCanvasResult } from '@/lib/api';

const api = new UrbanPlanningAPI();

export default function Home() {
  const [currentQuery, setCurrentQuery] = useState<string>('');

  const {
    data: exploratoryResult,
    error,
    isLoading,
    refetch,
  } = useQuery<ExploratoryCanvasResult>({
    queryKey: ['urban-exploration', currentQuery],
    queryFn: () => api.exploreQuery(currentQuery),
    enabled: !!currentQuery,
    staleTime: 5 * 60 * 1000,
    retry: 2,
  });

  const handleSubmitQuery = (query: string) => {
    setCurrentQuery(query);
  };

  return (
    <main className="min-h-screen bg-background transition-colors duration-300">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="space-y-8">
          {/* Theme Toggle - Fixed Position */}
          <div className="fixed top-4 right-4 z-50">
            <ThemeToggle />
          </div>
          {/* Header */}
          <Card>
            <CardHeader className="text-center">
              <CardTitle className="text-4xl font-bold flex items-center justify-center gap-3 text-foreground">
                <Building2 className="h-10 w-10 text-blue-600 dark:text-blue-400 transition-colors duration-300" />
                Urban Planning Analysis
              </CardTitle>
              <CardDescription className="text-xl max-w-2xl mx-auto text-foreground/80">
                AI-powered exploratory analysis for San Francisco neighborhoods. 
                Ask questions about climate, transportation, housing, and urban planning.
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
                    <p className="text-lg font-medium text-foreground">Analyzing urban planning impacts...</p>
                    <p className="text-foreground/70">This may take a few moments</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Loading Analytics Skeleton */}
          {isLoading && currentQuery && (
            <AnalyticsLoadingSkeleton />
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
          {exploratoryResult && !isLoading && (
            <ErrorBoundary>
              <div className="space-y-6">
                {/* Analytics Dashboard - Comprehensive analysis */}
                <AnalyticsDashboard
                  data={exploratoryResult}
                  onExploreMore={handleSubmitQuery}
                />
                
                {/* Exploratory Canvas - Detailed view for climate/scenario queries */}
                {(exploratoryResult.context.query_type === 'scenario_planning' && 
                  exploratoryResult.context.primary_domain === 'climate') && (
                  <ExploratoryCanvas
                    query={currentQuery}
                    queryType={exploratoryResult.context.query_type as any}
                    neighborhoods={exploratoryResult.context.neighborhoods}
                    primaryDomain={exploratoryResult.context.primary_domain}
                  />
                )}
              </div>
            </ErrorBoundary>
          )}

          {/* Empty State - When no data but no loading */}
          {!exploratoryResult && !isLoading && currentQuery && (
            <EmptyState 
              title="No results found"
              description="We couldn't find any analysis for your query. Please try a different question."
              action={
                <Button variant="outline" onClick={() => setCurrentQuery('')}>
                  <Search className="h-4 w-4 mr-2" />
                  Try a new search
                </Button>
              }
            />
          )}

          {/* Welcome State - Show when no query has been made */}
          {!currentQuery && !isLoading && (
            <Card>
              <CardHeader>
                <CardTitle className="text-foreground">Get Started</CardTitle>
                <CardDescription className="text-foreground/80">
                  Ask a question about urban planning in San Francisco neighborhoods to see detailed exploratory analysis
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                  <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg transition-all duration-300 hover:scale-105 hover:shadow-lg cursor-pointer">
                    <h3 className="font-medium mb-2 text-blue-900 dark:text-blue-100">Climate & Environment</h3>
                    <p className="text-blue-700 dark:text-blue-200">Explore how temperature, flooding, and environmental changes affect neighborhoods</p>
                  </div>
                  <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg transition-all duration-300 hover:scale-105 hover:shadow-lg cursor-pointer">
                    <h3 className="font-medium mb-2 text-green-900 dark:text-green-100">Transit & Business</h3>
                    <p className="text-green-700 dark:text-green-200">Analyze transportation changes and business ecosystem impacts</p>
                  </div>
                  <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg transition-all duration-300 hover:scale-105 hover:shadow-lg cursor-pointer">
                    <h3 className="font-medium mb-2 text-purple-900 dark:text-purple-100">Comparative Analysis</h3>
                    <p className="text-purple-700 dark:text-purple-200">Compare scenarios across Marina, Mission, and Hayes Valley neighborhoods</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Footer */}
          <Card>
            <CardContent className="py-4">
              <p className="text-center text-foreground/60 text-sm">
                Urban Infrastructure Planning System - Powered by AI for San Francisco neighborhoods
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </main>
  );
}
