'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown,
  MapPin, 
  Users, 
  DollarSign, 
  Leaf,
  Home,
  AlertTriangle,
  Info,
  Target,
  Zap,
  Clock,
  CheckCircle,
  XCircle,
  Lightbulb,
  ArrowRight
} from 'lucide-react';
import type { ExploratoryCanvasResult } from '@/lib/api';

interface AnalyticsDashboardProps {
  data: ExploratoryCanvasResult;
  onExploreMore?: (query: string) => void;
}

export function AnalyticsDashboard({ data, onExploreMore }: AnalyticsDashboardProps) {
  const { context, neighborhood_analyses, comparative_insights, scenario_branches, exploration_suggestions, related_questions } = data;

  return (
    <div className="space-y-6">
      {/* Query Analysis Header */}
      <Card className="border-l-4 border-l-blue-500 transition-all duration-300 hover:shadow-lg">
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="space-y-2">
              <CardTitle className="text-xl text-foreground">Query Analysis Results</CardTitle>
              <CardDescription className="text-foreground/80 max-w-2xl">
                {data.query}
              </CardDescription>
              <div className="flex items-center gap-2 flex-wrap">
                <Badge variant="outline" className="capitalize">
                  {context.query_type.replace('_', ' ')}
                </Badge>
                <Badge variant="secondary" className="capitalize">
                  {context.primary_domain}
                </Badge>
                <Badge 
                  variant={context.confidence > 0.8 ? "default" : context.confidence > 0.6 ? "secondary" : "destructive"}
                  className="flex items-center gap-1"
                >
                  <Target className="h-3 w-3" />
                  {Math.round(context.confidence * 100)}% confidence
                </Badge>
              </div>
            </div>
            <div className="text-right">
              <div className="text-sm text-foreground/60">Analyzing</div>
              <div className="font-medium text-foreground">{context.neighborhoods.length} neighborhood{context.neighborhoods.length > 1 ? 's' : ''}</div>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Main Content Tabs */}
      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="neighborhoods">Neighborhoods</TabsTrigger>
          <TabsTrigger value="insights">Insights</TabsTrigger>
          <TabsTrigger value="scenarios">Scenarios</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          {renderOverviewDashboard(context, neighborhood_analyses, comparative_insights)}
        </TabsContent>

        {/* Neighborhoods Tab */}
        <TabsContent value="neighborhoods" className="space-y-6">
          {renderNeighborhoodAnalysis(neighborhood_analyses, context.primary_domain)}
        </TabsContent>

        {/* Insights Tab */}
        <TabsContent value="insights" className="space-y-6">
          {renderInsightsAnalysis(neighborhood_analyses, comparative_insights, context)}
        </TabsContent>

        {/* Scenarios Tab */}
        <TabsContent value="scenarios" className="space-y-6">
          {renderScenariosAnalysis(scenario_branches, context, exploration_suggestions)}
        </TabsContent>
      </Tabs>

      {/* Related Questions & Next Steps */}
      <Card className="transition-all duration-300 hover:shadow-lg">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-foreground">
            <Lightbulb className="h-5 w-5 text-yellow-500" />
            Continue Exploring
          </CardTitle>
          <CardDescription className="text-foreground/80">
            Related questions and suggested deep dives
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {related_questions.slice(0, 4).map((question, index) => (
              <Button
                key={index}
                variant="outline"
                className="justify-start text-left h-auto p-3 transition-all duration-300 hover:scale-105 hover:shadow-md"
                onClick={() => onExploreMore?.(question)}
              >
                <div className="flex items-start gap-2 w-full">
                  <ArrowRight className="h-4 w-4 mt-0.5 flex-shrink-0 text-blue-500" />
                  <span className="text-sm">{question}</span>
                </div>
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function renderOverviewDashboard(context: any, neighborhood_analyses: any[], comparative_insights: any) {
  return (
    <div className="space-y-6">
      {/* Key Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard
          title="Neighborhoods"
          value={context.neighborhoods.length}
          subtitle="Areas analyzed"
          icon={<MapPin className="h-4 w-4" />}
          trend="neutral"
        />
        <MetricCard
          title="Analysis Depth"
          value={neighborhood_analyses.reduce((sum, n) => sum + Object.keys(n.impact_analysis).length, 0)}
          subtitle="Impact dimensions"
          icon={<BarChart3 className="h-4 w-4" />}
          trend="positive"
        />
        <MetricCard
          title="Insights"
          value={neighborhood_analyses.reduce((sum, n) => 
            sum + Object.values(n.impact_analysis).reduce((s: number, d: any) => s + d.insights.length, 0), 0)}
          subtitle="Key findings"
          icon={<Lightbulb className="h-4 w-4" />}
          trend="positive"
        />
        <MetricCard
          title="Confidence"
          value={`${Math.round(context.confidence * 100)}%`}
          subtitle="Analysis quality"
          icon={<Target className="h-4 w-4" />}
          trend={context.confidence > 0.8 ? "positive" : context.confidence > 0.6 ? "neutral" : "negative"}
        />
      </div>

      {/* Domain-Specific Overview */}
      {renderDomainOverview(context.primary_domain, neighborhood_analyses)}

      {/* Quick Summary */}
      <Card className="transition-all duration-300 hover:shadow-lg">
        <CardHeader>
          <CardTitle className="text-foreground">Executive Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {generateExecutiveSummary(context, neighborhood_analyses, comparative_insights)}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function renderNeighborhoodAnalysis(neighborhood_analyses: any[], primary_domain: string) {
  return (
    <div className="space-y-6">
      {neighborhood_analyses.map((analysis, index) => (
        <Card key={index} className="transition-all duration-300 hover:shadow-lg">
          <CardHeader>
            <CardTitle className="capitalize text-foreground">{analysis.neighborhood} District</CardTitle>
            <CardDescription className="text-foreground/80">
              {analysis.characteristics.primary_character}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Impact Analysis Dimensions */}
            <div className="space-y-3">
              {Object.entries(analysis.impact_analysis).map(([key, dimension]: [string, any]) => (
                <div key={key} className="border rounded-lg p-4 space-y-2 hover:bg-muted/50 transition-colors">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-foreground">{dimension.title}</h4>
                    <Badge variant="outline" className="text-xs">
                      {dimension.insights.length} insights
                    </Badge>
                  </div>
                  <p className="text-sm text-foreground/80">{dimension.description}</p>
                  
                  {/* Key Metrics */}
                  {Object.keys(dimension.metrics).length > 0 && (
                    <div className="grid grid-cols-2 gap-2 mt-2">
                      {Object.entries(dimension.metrics).slice(0, 2).map(([metricKey, value]: [string, any]) => (
                        <div key={metricKey} className="text-xs">
                          <span className="text-foreground/60 capitalize">{metricKey.replace('_', ' ')}: </span>
                          <span className="font-medium text-foreground">{typeof value === 'string' ? value : JSON.stringify(value)}</span>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Top Insights */}
                  <div className="space-y-1">
                    {dimension.insights.slice(0, 2).map((insight: string, i: number) => (
                      <div key={i} className="flex items-start gap-2 text-xs">
                        <CheckCircle className="h-3 w-3 text-green-500 mt-0.5 flex-shrink-0" />
                        <span className="text-foreground/80">{insight}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            {/* Vulnerability & Adaptation */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2 border-t">
              <div>
                <h4 className="font-medium text-foreground mb-2 flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4 text-orange-500" />
                  Vulnerability Factors
                </h4>
                <div className="space-y-1">
                  {analysis.vulnerability_factors.map((factor: string, i: number) => (
                    <div key={i} className="text-xs text-foreground/70 flex items-start gap-1">
                      <span className="w-1 h-1 bg-orange-500 rounded-full mt-1.5 flex-shrink-0"></span>
                      {factor}
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <h4 className="font-medium text-foreground mb-2 flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  Adaptation Strategies
                </h4>
                <div className="space-y-1">
                  {analysis.adaptation_strategies.map((strategy: string, i: number) => (
                    <div key={i} className="text-xs text-foreground/70 flex items-start gap-1">
                      <span className="w-1 h-1 bg-green-500 rounded-full mt-1.5 flex-shrink-0"></span>
                      {strategy}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

function renderInsightsAnalysis(neighborhood_analyses: any[], comparative_insights: any, context: any) {
  const allInsights = neighborhood_analyses.flatMap(n => 
    Object.values(n.impact_analysis).flatMap((d: any) => d.insights)
  );

  return (
    <div className="space-y-6">
      {/* Comparative Insights */}
      {comparative_insights && (
        <Card className="transition-all duration-300 hover:shadow-lg">
          <CardHeader>
            <CardTitle className="text-foreground">Cross-Neighborhood Comparison</CardTitle>
            <CardDescription className="text-foreground/80">
              How different areas compare and opportunities for coordination
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {Object.entries(comparative_insights).map(([key, value]: [string, any]) => (
              <div key={key} className="flex items-start gap-3 p-3 bg-muted/20 rounded-lg">
                <Info className="h-4 w-4 text-blue-500 mt-0.5 flex-shrink-0" />
                <div>
                  <div className="font-medium text-sm text-foreground capitalize">
                    {key.replace('_', ' ')}
                  </div>
                  <div className="text-xs text-foreground/70 mt-1">
                    {typeof value === 'string' ? value : JSON.stringify(value)}
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Key Insights Categorized */}
      <Card className="transition-all duration-300 hover:shadow-lg">
        <CardHeader>
          <CardTitle className="text-foreground">Key Insights Summary</CardTitle>
          <CardDescription className="text-foreground/80">
            Most important findings from the analysis
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {allInsights.slice(0, 8).map((insight: string, index: number) => (
              <div key={index} className="flex items-start gap-2 p-3 border rounded-lg hover:bg-muted/20 transition-colors">
                <Lightbulb className="h-4 w-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                <span className="text-sm text-foreground/80">{insight}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function renderScenariosAnalysis(scenario_branches: any[] | undefined, context: any, exploration_suggestions: string[]) {
  // For scenario planning queries, show scenario analysis even if no branches are provided
  const isScenarioQuery = context.query_type === 'scenario_planning';
  
  if (!scenario_branches || scenario_branches.length === 0) {
    if (!isScenarioQuery) {
      return (
        <div className="space-y-6">
          <Alert>
            <Info className="h-4 w-4" />
            <AlertDescription>
              This query type doesn't include scenario analysis. Try a "what if" question to explore different scenarios.
            </AlertDescription>
          </Alert>

        {/* Exploration Suggestions */}
        <Card className="transition-all duration-300 hover:shadow-lg">
          <CardHeader>
            <CardTitle className="text-foreground">Suggested Explorations</CardTitle>
            <CardDescription className="text-foreground/80">
              Ways to expand this analysis
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {exploration_suggestions.map((suggestion, index) => (
                <div key={index} className="flex items-start gap-2 p-2 hover:bg-muted/20 rounded transition-colors">
                  <ArrowRight className="h-4 w-4 text-blue-500 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-foreground/80">{suggestion}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    );
    } else {
      // For scenario queries without explicit branches, generate scenario analysis
      return (
        <div className="space-y-6">
          <Card className="transition-all duration-300 hover:shadow-lg">
            <CardHeader>
              <CardTitle className="text-foreground flex items-center gap-2">
                <Zap className="h-5 w-5 text-blue-500" />
                Scenario Analysis
              </CardTitle>
              <CardDescription>
                Exploring potential outcomes and variations of this scenario
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                    <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-2">Base Scenario</h4>
                    <p className="text-sm text-blue-700 dark:text-blue-200">
                      Current conditions and immediate impacts of implementing the proposed changes.
                    </p>
                  </div>
                  <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                    <h4 className="font-medium text-green-900 dark:text-green-100 mb-2">Optimistic Scenario</h4>
                    <p className="text-sm text-green-700 dark:text-green-200">
                      Best-case outcomes with community support and optimal implementation.
                    </p>
                  </div>
                  <div className="p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
                    <h4 className="font-medium text-orange-900 dark:text-orange-100 mb-2">Cautious Scenario</h4>
                    <p className="text-sm text-orange-700 dark:text-orange-200">
                      Conservative approach addressing potential resistance and constraints.
                    </p>
                  </div>
                  <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                    <h4 className="font-medium text-purple-900 dark:text-purple-100 mb-2">Alternative Scenario</h4>
                    <p className="text-sm text-purple-700 dark:text-purple-200">
                      Modified approach considering different implementation strategies.
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Exploration Suggestions */}
          <Card className="transition-all duration-300 hover:shadow-lg">
            <CardHeader>
              <CardTitle className="text-foreground">Continue Exploring</CardTitle>
              <CardDescription className="text-foreground/80">
                Related questions and suggested deep dives
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {exploration_suggestions.map((suggestion, index) => (
                  <div key={index} className="flex items-start gap-2 p-2 hover:bg-muted/20 rounded transition-colors">
                    <ArrowRight className="h-4 w-4 text-blue-500 mt-0.5 flex-shrink-0" />
                    <span className="text-sm text-foreground/80">{suggestion}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      );
    }
  }

  return (
    <div className="space-y-6">
      {/* Scenario Timeline */}
      <Card className="transition-all duration-300 hover:shadow-lg">
        <CardHeader>
          <CardTitle className="text-foreground">Scenario Development Timeline</CardTitle>
          <CardDescription className="text-foreground/80">
            How impacts would unfold over time
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {scenario_branches.map((scenario, index) => (
              <div key={index} className="relative">
                {index < scenario_branches.length - 1 && (
                  <div className="absolute left-4 top-12 w-0.5 h-16 bg-border"></div>
                )}
                <div className="flex items-start gap-4">
                  <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                    <Clock className="h-4 w-4 text-primary" />
                  </div>
                  <div className="flex-1 space-y-2">
                    <div className="flex items-center gap-2">
                      <h4 className="font-medium text-foreground">{scenario.scenario_name}</h4>
                      <Badge variant="outline" className="text-xs">{scenario.probability}</Badge>
                    </div>
                    <p className="text-sm text-foreground/80">{scenario.description}</p>
                    
                    {/* Consequences */}
                    <div className="space-y-1">
                      {scenario.consequences.map((consequence: string, i: number) => (
                        <div key={i} className="flex items-start gap-2 text-xs">
                          <span className="w-1 h-1 bg-blue-500 rounded-full mt-1.5 flex-shrink-0"></span>
                          <span className="text-foreground/70">{consequence}</span>
                        </div>
                      ))}
                    </div>

                    {/* Related Factors */}
                    <div className="flex flex-wrap gap-1 mt-2">
                      {scenario.related_factors.map((factor: string, i: number) => (
                        <Badge key={i} variant="secondary" className="text-xs">
                          {factor}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function renderDomainOverview(domain: string, neighborhood_analyses: any[]) {
  const domainIcons = {
    climate: <Leaf className="h-5 w-5 text-green-500" />,
    transportation: <Zap className="h-5 w-5 text-blue-500" />,
    housing: <Home className="h-5 w-5 text-purple-500" />,
    economics: <DollarSign className="h-5 w-5 text-yellow-500" />,
    general: <Target className="h-5 w-5 text-gray-500" />
  };

  const icon = domainIcons[domain as keyof typeof domainIcons] || domainIcons.general;

  return (
    <Card className="transition-all duration-300 hover:shadow-lg">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-foreground">
          {icon}
          {domain.charAt(0).toUpperCase() + domain.slice(1)} Analysis Overview
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {neighborhood_analyses.map((analysis, index) => (
            <div key={index} className="p-3 border rounded-lg hover:bg-muted/20 transition-colors">
              <h4 className="font-medium text-foreground capitalize mb-2">{analysis.neighborhood}</h4>
              <div className="text-xs text-foreground/70">
                {Object.keys(analysis.impact_analysis).length} impact dimension{Object.keys(analysis.impact_analysis).length > 1 ? 's' : ''}
              </div>
              <Progress 
                value={Object.values(analysis.impact_analysis).reduce((sum: number, d: any) => sum + d.insights.length, 0) * 10} 
                className="mt-2" 
              />
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

function MetricCard({ title, value, subtitle, icon, trend }: {
  title: string;
  value: string | number;
  subtitle: string;
  icon: React.ReactNode;
  trend: 'positive' | 'negative' | 'neutral';
}) {
  const trendIcon = trend === 'positive' ? <TrendingUp className="h-3 w-3 text-green-500" /> :
                   trend === 'negative' ? <TrendingDown className="h-3 w-3 text-red-500" /> : null;

  return (
    <Card className="transition-all duration-300 hover:shadow-md hover:scale-105">
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <p className="text-sm text-foreground/60">{title}</p>
            <p className="text-2xl font-bold text-foreground">{value}</p>
            <div className="flex items-center gap-1">
              {trendIcon}
              <p className="text-xs text-foreground/60">{subtitle}</p>
            </div>
          </div>
          <div className="text-foreground/40">{icon}</div>
        </div>
      </CardContent>
    </Card>
  );
}

function generateExecutiveSummary(context: any, neighborhood_analyses: any[], comparative_insights: any) {
  const summaryPoints = [];

  // Query type specific summary
  switch (context.query_type) {
    case 'scenario_planning':
      summaryPoints.push({
        icon: <Zap className="h-4 w-4 text-blue-500" />,
        text: `Scenario analysis reveals ${neighborhood_analyses.length} neighborhoods would be affected differently by the proposed changes.`
      });
      break;
    case 'comparative':
      summaryPoints.push({
        icon: <BarChart3 className="h-4 w-4 text-purple-500" />,
        text: `Comparative analysis shows significant differences between ${context.neighborhoods.join(' and ')} neighborhoods.`
      });
      break;
    default:
      summaryPoints.push({
        icon: <Target className="h-4 w-4 text-green-500" />,
        text: `Analysis identified ${neighborhood_analyses.reduce((sum, n) => sum + Object.keys(n.impact_analysis).length, 0)} key impact areas across ${context.neighborhoods.length} neighborhoods.`
      });
  }

  // Domain specific insights
  summaryPoints.push({
    icon: <Lightbulb className="h-4 w-4 text-yellow-500" />,
    text: `${context.primary_domain.charAt(0).toUpperCase() + context.primary_domain.slice(1)} domain analysis reveals varying levels of vulnerability and adaptation potential.`
  });

  // Confidence assessment
  if (context.confidence > 0.8) {
    summaryPoints.push({
      icon: <CheckCircle className="h-4 w-4 text-green-500" />,
      text: "High confidence analysis with comprehensive data coverage and clear patterns."
    });
  } else if (context.confidence > 0.6) {
    summaryPoints.push({
      icon: <Info className="h-4 w-4 text-blue-500" />,
      text: "Moderate confidence analysis with good data coverage but some uncertainty in projections."
    });
  } else {
    summaryPoints.push({
      icon: <AlertTriangle className="h-4 w-4 text-orange-500" />,
      text: "Lower confidence analysis due to limited data or complex interactions requiring further investigation."
    });
  }

  return summaryPoints.map((point, index) => (
    <div key={index} className="flex items-start gap-3">
      {point.icon}
      <span className="text-sm text-foreground/80">{point.text}</span>
    </div>
  ));
}