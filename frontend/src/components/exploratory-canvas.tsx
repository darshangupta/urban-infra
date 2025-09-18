'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Thermometer, 
  MapPin, 
  Users, 
  DollarSign, 
  Home,
  ArrowRight,
  TreePine,
  Zap,
  Info,
  TrendingUp,
  TrendingDown,
  AlertTriangle
} from 'lucide-react';

interface ExploratoryCanvasProps {
  query: string;
  queryType: 'analytical' | 'comparative' | 'scenario_planning' | 'solution_seeking';
  neighborhoods: string[];
  primaryDomain: string;
}

export function ExploratoryCanvas({ 
  query, 
  queryType, 
  neighborhoods, 
  primaryDomain 
}: ExploratoryCanvasProps) {
  
  // Demo data for climate query "What if it became 10 degrees colder? How would that affect Mission vs Hayes vs Marina?"
  const isClimateQuery = query.toLowerCase().includes('colder') || query.toLowerCase().includes('temperature');
  
  if (isClimateQuery && queryType === 'scenario_planning') {
    return <ClimateImpactCanvas query={query} neighborhoods={neighborhoods} />;
  }
  
  // Default analytical canvas
  return <AnalyticalCanvas query={query} neighborhoods={neighborhoods} primaryDomain={primaryDomain} />;
}

function ClimateImpactCanvas({ query, neighborhoods }: { query: string, neighborhoods: string[] }) {
  const temperatureChange = extractTemperatureChange(query);
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <Card className="border-blue-200 bg-blue-50">
        <CardHeader>
          <div className="flex items-center gap-3">
            <Thermometer className="h-6 w-6 text-blue-600" />
            <div>
              <CardTitle className="text-blue-900">Climate Scenario Analysis</CardTitle>
              <CardDescription className="text-blue-700 dark:text-blue-300">
                Exploring impacts of {Math.abs(temperatureChange)}°F colder weather across SF neighborhoods
              </CardDescription>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Scenario Timeline */}
      <Card>
        <CardHeader>
          <CardTitle>Scenario Progression</CardTitle>
          <CardDescription className="text-foreground/80">How impacts would unfold over time</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <ScenarioTimelineCard
              period="Immediate (0-6 months)"
              probability="Highly Likely"
              impacts={[
                "Emergency heating assistance activated",
                "Outdoor dining revenue drops 40-60%",
                "Public facility usage shifts indoors"
              ]}
              color="red"
              className="bg-red-900/20 border-red-800 text-red-100"
            />
            <ScenarioTimelineCard
              period="Medium-term (6 months - 2 years)"
              probability="Likely with Planning"
              impacts={[
                "Building weatherization programs expanded", 
                "Business models adapt to indoor focus",
                "Community warming centers established"
              ]}
              color="yellow"
              className="bg-amber-900/20 border-amber-800 text-amber-100"
            />
            <ScenarioTimelineCard
              period="Long-term (2+ years)"
              probability="Possible with Sustained Change"
              impacts={[
                "Neighborhood character permanently shifts",
                "Population migration due to cost burden",
                "Infrastructure fundamentally adapted"
              ]}
              color="blue"
              className="bg-blue-900/20 border-blue-800 text-blue-100"
            />
          </div>
        </CardContent>
      </Card>

      {/* Neighborhood Impact Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {neighborhoods.map((neighborhood) => (
          <NeighborhoodClimateCard 
            key={neighborhood} 
            neighborhood={neighborhood} 
            temperatureChange={temperatureChange}
          />
        ))}
      </div>

      {/* Cross-Cutting Insights */}
      <Card>
        <CardHeader>
          <CardTitle>Cross-Neighborhood Insights</CardTitle>
          <CardDescription className="text-foreground/80">Patterns and differences across SF neighborhoods</CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="vulnerability" className="w-full">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="vulnerability">Vulnerability</TabsTrigger>
              <TabsTrigger value="adaptation">Adaptation</TabsTrigger>
              <TabsTrigger value="equity">Equity Impact</TabsTrigger>
              <TabsTrigger value="coordination">Coordination</TabsTrigger>
            </TabsList>
            
            <TabsContent value="vulnerability" className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <VulnerabilityCard
                  neighborhood="Marina"
                  riskLevel="High"
                  primaryRisks={["Waterfront flooding", "Car-dependent isolation", "Fixed-income heating burden"]}
                  icon={<AlertTriangle className="h-5 w-5 text-red-500" />}
                />
                <VulnerabilityCard
                  neighborhood="Mission"
                  riskLevel="Medium-High"
                  primaryRisks={["Energy burden on low-income residents", "Overcrowding for heat sharing", "Outdoor culture loss"]}
                  icon={<Users className="h-5 w-5 text-yellow-500" />}
                />
                <VulnerabilityCard
                  neighborhood="Hayes Valley"
                  riskLevel="Medium"
                  primaryRisks={["Transit-dependent mobility issues", "Outdoor plaza usage decline", "Small unit heating costs"]}
                  icon={<Home className="h-5 w-5 text-blue-500" />}
                />
              </div>
            </TabsContent>
            
            <TabsContent value="adaptation" className="space-y-4">
              <Alert>
                <TreePine className="h-4 w-4" />
                <AlertDescription>
                  <strong>Key Adaptation Strategies:</strong> Each neighborhood requires different approaches based on 
                  demographics, infrastructure, and existing community resources.
                </AlertDescription>
              </Alert>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm">Infrastructure-Focused</CardTitle>
                  </CardHeader>
                  <CardContent className="text-sm space-y-2">
                    <div>• Marina: Flood barriers + building retrofits</div>
                    <div>• Hayes: Covered transit connections</div>
                    <div>• Mission: Community resilience hubs</div>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm">Community-Focused</CardTitle>
                  </CardHeader>
                  <CardContent className="text-sm space-y-2">
                    <div>• Shared heating programs</div>
                    <div>• Indoor cultural space development</div>
                    <div>• Emergency mutual aid networks</div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
            
            <TabsContent value="equity" className="space-y-4">
              <div className="space-y-4">
                <Alert className="border-orange-200 bg-orange-50">
                  <AlertTriangle className="h-4 w-4 text-orange-600" />
                  <AlertDescription className="text-orange-800">
                    <strong>Equity Concern:</strong> Cold weather impacts disproportionately affect 
                    lower-income residents through increased heating costs and reduced outdoor economic opportunities.
                  </AlertDescription>
                </Alert>
                
                <div className="grid grid-cols-2 gap-4">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm flex items-center gap-2">
                        <TrendingUp className="h-4 w-4 text-red-500" />
                        Increased Burden
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="text-sm">
                      Mission residents face highest relative heating cost burden (15-25% of income vs 5-8% in Marina)
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm flex items-center gap-2">
                        <TrendingDown className="h-4 w-4 text-green-500" />
                        Mitigation Potential
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="text-sm">
                      Strong community networks in Mission/Hayes provide mutual aid opportunities
                    </CardContent>
                  </Card>
                </div>
              </div>
            </TabsContent>
            
            <TabsContent value="coordination" className="space-y-4">
              <div className="space-y-4">
                <Alert className="border-green-200 bg-green-50">
                  <Info className="h-4 w-4 text-green-600" />
                  <AlertDescription className="text-green-800">
                    <strong>Coordination Opportunity:</strong> City-wide response could leverage each neighborhood's strengths
                    while addressing specific vulnerabilities.
                  </AlertDescription>
                </Alert>
                
                <div className="space-y-3">
                  <div className="flex items-center gap-3 p-3 bg-gray-50 rounded">
                    <MapPin className="h-4 w-4 text-blue-500" />
                    <span className="text-sm">Marina resources (space, facilities) could serve as regional warming centers</span>
                  </div>
                  <div className="flex items-center gap-3 p-3 bg-gray-50 rounded">
                    <Users className="h-4 w-4 text-purple-500" />
                    <span className="text-sm">Mission community networks could model mutual aid for other neighborhoods</span>
                  </div>
                  <div className="flex items-center gap-3 p-3 bg-gray-50 rounded">
                    <Zap className="h-4 w-4 text-yellow-500" />
                    <span className="text-sm">Hayes transit infrastructure could prioritize heating for transit-dependent residents</span>
                  </div>
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Exploration Suggestions */}
      <Card>
        <CardHeader>
          <CardTitle>Continue Exploring</CardTitle>
          <CardDescription className="text-foreground/80">Related questions and deeper analysis</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <Button variant="outline" className="justify-start transition-all duration-300 hover:scale-105 hover:shadow-md hover:bg-blue-50 dark:hover:bg-blue-900/20">
              <ArrowRight className="h-4 w-4 mr-2" />
              What if it were 20 degrees colder instead?
            </Button>
            <Button variant="outline" className="justify-start transition-all duration-300 hover:scale-105 hover:shadow-md hover:bg-blue-50 dark:hover:bg-blue-900/20">
              <ArrowRight className="h-4 w-4 mr-2" />
              How do other cities handle similar conditions?
            </Button>
            <Button variant="outline" className="justify-start transition-all duration-300 hover:scale-105 hover:shadow-md hover:bg-blue-50 dark:hover:bg-blue-900/20">
              <ArrowRight className="h-4 w-4 mr-2" />
              What emergency resources currently exist?
            </Button>
            <Button variant="outline" className="justify-start transition-all duration-300 hover:scale-105 hover:shadow-md hover:bg-blue-50 dark:hover:bg-blue-900/20">
              <ArrowRight className="h-4 w-4 mr-2" />
              How would summer heat relief be affected?
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function ScenarioTimelineCard({ 
  period, 
  probability, 
  impacts, 
  color,
  className 
}: { 
  period: string, 
  probability: string, 
  impacts: string[], 
  color: 'red' | 'yellow' | 'blue',
  className?: string
}) {
  const colorClasses = {
    red: 'border-red-800 bg-red-900/20 text-red-100',
    yellow: 'border-amber-800 bg-amber-900/20 text-amber-100', 
    blue: 'border-blue-800 bg-blue-900/20 text-blue-100'
  };
  
  return (
    <Card className={`${className || colorClasses[color]} transition-all duration-300 hover:scale-105 hover:shadow-lg`}>
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-medium">{period}</CardTitle>
        <Badge variant="outline" className="w-fit border-current text-current">{probability}</Badge>
      </CardHeader>
      <CardContent>
        <ul className="text-sm space-y-1">
          {impacts.map((impact, i) => (
            <li key={i} className="flex items-start gap-2">
              <span className="w-1 h-1 bg-current rounded-full mt-2 flex-shrink-0 opacity-80"></span>
              <span className="text-current">{impact}</span>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}

function NeighborhoodClimateCard({ 
  neighborhood, 
  temperatureChange 
}: { 
  neighborhood: string, 
  temperatureChange: number 
}) {
  const neighborhoodData = {
    marina: {
      character: "Affluent, car-dependent waterfront",
      mainConcerns: ["Flood risk amplification", "Heating costs for fixed-income", "Outdoor business revenue loss"],
      heatingIncrease: Math.abs(temperatureChange * 12),
      businessImpact: "-40% outdoor dining revenue",
      demographics: "Higher fixed-income seniors vulnerable to heating costs"
    },
    mission: {
      character: "Dense, diverse, walkable community",
      mainConcerns: ["Energy burden on low-income", "Street culture disruption", "Community space adaptation"],
      heatingIncrease: Math.abs(temperatureChange * 18),
      businessImpact: "-25% street-facing business activity",
      demographics: "Working families face 15-25% of income on heating"
    },
    hayes_valley: {
      character: "Transit-rich, recently gentrified",
      mainConcerns: ["Reduced walkability appeal", "Transit dependency in cold", "Plaza usage decline"],
      heatingIncrease: Math.abs(temperatureChange * 15),
      businessImpact: "-30% outdoor plaza activity",
      demographics: "Young professionals, small units = higher heating per sqft"
    }
  };
  
  const data = neighborhoodData[neighborhood.toLowerCase() as keyof typeof neighborhoodData];
  if (!data) return null;
  
  return (
    <Card className="transition-all duration-300 hover:shadow-xl hover:shadow-blue-500/10 hover:-translate-y-2 cursor-pointer group">
      <CardHeader>
        <CardTitle className="capitalize group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors duration-300">{neighborhood} District</CardTitle>
        <CardDescription className="text-foreground/80">{data.character}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-foreground/70">Heating Cost Increase</span>
            <Badge variant="destructive">+{data.heatingIncrease}%</Badge>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-sm text-foreground/70">Business Impact</span>
            <Badge variant="outline">{data.businessImpact}</Badge>
          </div>
          
          <div className="pt-2 border-t">
            <h4 className="text-sm font-medium mb-2">Key Concerns</h4>
            <ul className="text-sm space-y-1">
              {data.mainConcerns.map((concern, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="w-1 h-1 bg-gray-400 rounded-full mt-2 flex-shrink-0"></span>
                  {concern}
                </li>
              ))}
            </ul>
          </div>
          
          <div className="pt-2 border-t">
            <h4 className="text-sm font-medium mb-1">Demographics Impact</h4>
            <p className="text-sm text-foreground/80">{data.demographics}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function VulnerabilityCard({ 
  neighborhood, 
  riskLevel, 
  primaryRisks, 
  icon 
}: { 
  neighborhood: string, 
  riskLevel: string, 
  primaryRisks: string[], 
  icon: React.ReactNode 
}) {
  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          {icon}
          <CardTitle className="text-sm">{neighborhood}</CardTitle>
        </div>
        <Badge variant="outline" className="w-fit">{riskLevel} Risk</Badge>
      </CardHeader>
      <CardContent>
        <ul className="text-sm space-y-1">
          {primaryRisks.map((risk, i) => (
            <li key={i} className="flex items-start gap-2">
              <span className="w-1 h-1 bg-gray-400 rounded-full mt-2 flex-shrink-0"></span>
              {risk}
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}

function AnalyticalCanvas({ 
  query, 
  neighborhoods, 
  primaryDomain 
}: { 
  query: string, 
  neighborhoods: string[], 
  primaryDomain: string 
}) {
  return (
    <div className="space-y-6">
      <Card className="transition-all duration-300 hover:shadow-lg hover:shadow-blue-500/10">
        <CardHeader>
          <CardTitle>Analytical Dashboard</CardTitle>
          <CardDescription className="text-foreground/80">Impact analysis for: {query}</CardDescription>
        </CardHeader>
        <CardContent>
          <p>This would show analytical content for {primaryDomain} domain across {neighborhoods.join(', ')} neighborhoods.</p>
        </CardContent>
      </Card>
    </div>
  );
}

function extractTemperatureChange(query: string): number {
  const match = query.match(/(\d+)\s*degrees?\s*(colder|cooler|warmer|hotter)/i);
  if (match) {
    const degrees = parseInt(match[1]);
    const direction = match[2].toLowerCase();
    return direction === 'colder' || direction === 'cooler' ? -degrees : degrees;
  }
  return -10; // default
}