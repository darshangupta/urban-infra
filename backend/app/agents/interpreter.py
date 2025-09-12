"""
Agent 1: Interpreter - Convert natural language to structured planning parameters
"""

from crewai import Agent, Task, Crew, LLM
from crewai_tools import BaseTool
from typing import Dict, Any, List
import json
import httpx
from pydantic import BaseModel


class UrbanPlanningTool(BaseTool):
    """Tool for the interpreter to call our neighborhood APIs"""
    
    name: str = "urban_planning_api"
    description: str = "Get SF neighborhood data, zoning rules, and validate development proposals"
    
    def _run(self, action: str, neighborhood: str = None, **kwargs) -> str:
        """Execute urban planning API calls"""
        base_url = "http://localhost:8001/api/v1"
        
        try:
            if action == "list_neighborhoods":
                response = httpx.get(f"{base_url}/neighborhoods/")
                
            elif action == "get_zoning" and neighborhood:
                response = httpx.get(f"{base_url}/neighborhoods/{neighborhood}/zoning")
                
            elif action == "validate_proposal" and neighborhood:
                proposal_data = {
                    "far": kwargs.get("far", 1.0),
                    "height_ft": kwargs.get("height_ft", 40),
                    "lot_area_sf": kwargs.get("lot_area_sf", 2500),
                    "num_units": kwargs.get("num_units", 1)
                }
                response = httpx.post(
                    f"{base_url}/neighborhoods/{neighborhood}/validate-proposal",
                    json=proposal_data
                )
            else:
                return json.dumps({"error": "Invalid action or missing neighborhood"})
            
            if response.status_code == 200:
                return json.dumps(response.json(), indent=2)
            else:
                return json.dumps({"error": f"API call failed: {response.status_code}"})
                
        except Exception as e:
            return json.dumps({"error": str(e)})


class PlanningParameters(BaseModel):
    """Structured planning parameters output"""
    neighborhood: str
    intent: str  # "housing_development", "transit_improvement", "mixed_use", etc.
    constraints: List[str]
    target_metrics: Dict[str, Any]  # units, affordability %, etc.
    spatial_focus: str  # "near_transit", "waterfront", "cultural_district", etc.


class InterpreterAgent:
    """Agent 1: Natural language to structured planning parameters"""
    
    def __init__(self, openai_api_key: str = None):
        self.urban_tool = UrbanPlanningTool()
        self.openai_api_key = openai_api_key
        
        # Initialize agent only if API key provided
        if openai_api_key:
            self.llm = LLM(
                model="gpt-4o-mini",
                api_key=openai_api_key,
                temperature=0.1
            )
            # Create the agent
            self.agent = Agent(
                role='Urban Planning Interpreter',
                goal='Convert natural language urban planning queries into structured parameters for analysis',
                backstory="""You are an expert urban planner specializing in San Francisco zoning and development. 
                You understand SF neighborhoods, zoning codes (RH-1, NCT-3, NCT-4), transit systems, and planning constraints.
                You excel at translating citizen requests and planning ideas into actionable technical parameters.""",
                tools=[self.urban_tool],
                llm=self.llm,
                verbose=True
            )
        else:
            self.agent = None
    
    def interpret_query(self, user_query: str) -> PlanningParameters:
        """Convert natural language query to structured planning parameters"""
        
        task = Task(
            description=f"""
            Analyze this urban planning query and convert it to structured parameters:
            
            USER QUERY: "{user_query}"
            
            Your task:
            1. First call urban_planning_api with action="list_neighborhoods" to see available SF neighborhoods
            2. Identify which neighborhood the query refers to (Marina District, Hayes Valley, Mission District)
            3. Call urban_planning_api with action="get_zoning" for that neighborhood to understand constraints
            4. Determine the planning intent (housing_development, transit_improvement, etc.)
            5. Extract any target metrics mentioned (number of units, affordability requirements, etc.)
            6. Identify spatial focus areas (near transit, waterfront, etc.)
            7. List relevant constraints from the neighborhood data
            
            Return ONLY a JSON object with these exact fields:
            - neighborhood: (exact name from API)
            - intent: (housing_development, transit_improvement, mixed_use, walkability, climate_resilience)  
            - constraints: (list of constraint strings from neighborhood data)
            - target_metrics: (dict with units, affordability_pct, far, height_ft if mentioned)
            - spatial_focus: (near_transit, waterfront, cultural_district, general)
            """,
            agent=self.agent,
            expected_output="JSON object with structured planning parameters"
        )
        
        # Execute the task
        crew = Crew(agents=[self.agent], tasks=[task])
        result = crew.kickoff()
        
        try:
            # Parse the result JSON
            if isinstance(result, str):
                parsed_result = json.loads(result.strip('```json').strip('```').strip())
            else:
                parsed_result = result
            
            return PlanningParameters(**parsed_result)
            
        except Exception as e:
            # Fallback parsing for robust operation
            return self._fallback_parse(user_query, str(result))
    
    def _fallback_parse(self, user_query: str, agent_output: str) -> PlanningParameters:
        """Fallback parsing if JSON extraction fails"""
        
        # Simple keyword matching for fallback
        neighborhoods = {"marina": "Marina District", "hayes": "Hayes Valley", "mission": "Mission District"}
        
        neighborhood = "Hayes Valley"  # Default
        for key, value in neighborhoods.items():
            if key in user_query.lower():
                neighborhood = value
                break
        
        intent = "housing_development"
        if "transit" in user_query.lower():
            intent = "transit_improvement"
        elif "mixed" in user_query.lower():
            intent = "mixed_use"
        elif "walkable" in user_query.lower():
            intent = "walkability"
        
        return PlanningParameters(
            neighborhood=neighborhood,
            intent=intent,
            constraints=["zoning_compliance", "community_input"],
            target_metrics={"units": 50, "affordability_pct": 20},
            spatial_focus="near_transit"
        )


# Example usage
if __name__ == "__main__":
    # Test the interpreter
    interpreter = InterpreterAgent()
    
    test_queries = [
        "Add affordable housing near BART in Hayes Valley",
        "Make the Marina more walkable while respecting flood risks",
        "Increase density in Mission without displacing existing residents"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        result = interpreter.interpret_query(query)
        print(f"Structured Parameters: {result.dict()}")