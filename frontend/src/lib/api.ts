/**
 * API client for urban planning system
 * Connects frontend to our 3-agent backend system
 */

export interface ImpactMetric {
  before: number;
  after: number;
  unit: string;
  confidence: number;
}

export interface CategoryImpact {
  metrics: Record<string, ImpactMetric>;
  benefits: string[];
  concerns: string[];
  mitigation_strategies: string[];
}

export interface ComprehensiveImpact {
  housing: CategoryImpact;
  accessibility: CategoryImpact;
  equity: CategoryImpact;
  economic: CategoryImpact;
  environmental: CategoryImpact;
  overall_assessment: string;
}

export interface PlanningAlternative {
  title: string;
  type: string;
  description: string;
  units: number;
  affordable_percentage: number;
  height_ft: number;
  amenities: string[];
}

export interface QueryIntent {
  type: string;
  priority: string;
  density: string;
  focus: string;
  confidence: number;
}

export interface AnalysisResult {
  query: string;
  neighborhood: string;
  intent: QueryIntent;
  alternatives: PlanningAlternative[];
  recommended: string;
  rationale: string;
  impact: ComprehensiveImpact;
}

// New Exploratory Canvas Types
export interface ExploratoryDimension {
  title: string;
  description: string;
  metrics: Record<string, any>;
  insights: string[];
  follow_up_questions: string[];
}

export interface NeighborhoodAnalysis {
  neighborhood: string;
  characteristics: Record<string, string>;
  impact_analysis: Record<string, ExploratoryDimension>;
  vulnerability_factors: string[];
  adaptation_strategies: string[];
}

export interface ScenarioBranch {
  scenario_name: string;
  description: string;
  probability: string;
  consequences: string[];
  related_factors: string[];
}

export interface QueryContext {
  query_type: string;
  exploration_mode: string;
  neighborhoods: string[];
  primary_domain: string;
  confidence: number;
  suggested_explorations: string[];
}

export interface ExploratoryCanvasResult {
  query: string;
  context: QueryContext;
  neighborhood_analyses: NeighborhoodAnalysis[];
  comparative_insights?: Record<string, any>;
  scenario_branches?: ScenarioBranch[];
  exploration_suggestions: string[];
  related_questions: string[];
}

// API client class
export class UrbanPlanningAPI {
  private baseUrl: string;

  constructor(baseUrl: string = 'http://localhost:8001') {
    this.baseUrl = baseUrl;
  }

  /**
   * Main analysis endpoint - sends query through complete 3-agent pipeline
   */
  async analyzeQuery(query: string): Promise<AnalysisResult> {
    const response = await fetch(`${this.baseUrl}/api/v1/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    });

    if (!response.ok) {
      throw new Error(`Analysis failed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * NEW: Exploratory canvas endpoint - generates open-ended exploration
   */
  async exploreQuery(query: string): Promise<ExploratoryCanvasResult> {
    const response = await fetch(`${this.baseUrl}/api/v1/explore`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    });

    if (!response.ok) {
      throw new Error(`Exploration failed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get available neighborhoods
   */
  async getNeighborhoods(): Promise<string[]> {
    const response = await fetch(`${this.baseUrl}/api/v1/neighborhoods/`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch neighborhoods: ${response.statusText}`);
    }

    const data = await response.json();
    return data.map((n: any) => n.name);
  }

  /**
   * Validate a development proposal
   */
  async validateProposal(neighborhood: string, proposal: any): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/v1/neighborhoods/${neighborhood}/validate-proposal`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(proposal),
    });

    if (!response.ok) {
      throw new Error(`Validation failed: ${response.statusText}`);
    }

    return response.json();
  }
}

// Default API instance
export const api = new UrbanPlanningAPI();