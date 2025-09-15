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

export interface AnalysisResult {
  query: string;
  neighborhood: string;
  alternatives: PlanningAlternative[];
  recommended: string;
  rationale: string;
  impact: ComprehensiveImpact;
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