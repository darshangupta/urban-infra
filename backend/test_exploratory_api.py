#!/usr/bin/env python3
"""
Test the new exploratory API endpoint with the climate example
"""

import json
import requests
import asyncio

def test_exploratory_api():
    """Test the new /explore endpoint with climate query"""
    
    base_url = "http://localhost:8001/api/v1"
    
    # Test the exact climate query from user's example
    test_queries = [
        "What if it became 10 degrees colder? How would that affect Mission vs Hayes vs Marina?",
        "How would more bike infrastructure affect businesses in the Marina vs the Mission?",
        "What if we added affordable housing near BART in Hayes Valley?"
    ]
    
    print("🔬 TESTING NEW EXPLORATORY API ENDPOINT")
    print("=" * 80)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        print("-" * 60)
        
        try:
            response = requests.post(
                f"{base_url}/explore",
                json={"query": query},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ SUCCESS!")
                print(f"Query Type: {data['context']['query_type']}")
                print(f"Exploration Mode: {data['context']['exploration_mode']}")
                print(f"Primary Domain: {data['context']['primary_domain']}")
                print(f"Neighborhoods: {data['context']['neighborhoods']}")
                print(f"Confidence: {data['context']['confidence']:.2f}")
                
                print(f"\n🏘️  NEIGHBORHOOD ANALYSES:")
                for analysis in data['neighborhood_analyses']:
                    print(f"   {analysis['neighborhood'].upper()}:")
                    print(f"   Character: {analysis['characteristics']['primary_character']}")
                    
                    for dimension_name, dimension in analysis['impact_analysis'].items():
                        print(f"   📊 {dimension['title']}:")
                        print(f"      {dimension['description']}")
                        print(f"      Key insights: {len(dimension['insights'])} insights")
                        print(f"      Follow-up questions: {len(dimension['follow_up_questions'])} questions")
                
                if data.get('scenario_branches'):
                    print(f"\n🌳 SCENARIO BRANCHES:")
                    for branch in data['scenario_branches']:
                        print(f"   {branch['scenario_name']}: {branch['probability']}")
                        print(f"   {branch['description']}")
                
                if data.get('comparative_insights'):
                    print(f"\n🔄 COMPARATIVE INSIGHTS:")
                    for key, value in data['comparative_insights'].items():
                        print(f"   {key}: {value}")
                
                print(f"\n💡 EXPLORATION SUGGESTIONS:")
                for suggestion in data['exploration_suggestions']:
                    print(f"   • {suggestion}")
                
                print(f"\n❓ RELATED QUESTIONS:")
                for question in data['related_questions'][:3]:  # Show first 3
                    print(f"   • {question}")
                
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        
        print("\n" + "=" * 60)

def test_climate_query_specifically():
    """Test specifically the climate query that should NOT suggest housing"""
    
    print("\n🌡️  SPECIFIC CLIMATE QUERY TEST")
    print("=" * 50)
    
    query = "What if it became 10 degrees colder? How would that affect Mission vs Hayes vs Marina?"
    
    try:
        response = requests.post(
            "http://localhost:8001/api/v1/explore",
            json={"query": query},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Query correctly identified as: {data['context']['query_type']}")
            print(f"✅ Primary domain: {data['context']['primary_domain']}")
            print(f"✅ Exploration mode: {data['context']['exploration_mode']}")
            
            # Check that we're NOT getting housing suggestions
            housing_mentioned = False
            for analysis in data['neighborhood_analyses']:
                for dimension_name, dimension in analysis['impact_analysis'].items():
                    if 'housing' in dimension['title'].lower() and 'affordable housing units' in dimension['description']:
                        housing_mentioned = True
            
            if not housing_mentioned:
                print("✅ CORRECT: No irrelevant housing development suggestions!")
            else:
                print("❌ PROBLEM: Still suggesting housing for climate query")
            
            # Check that we ARE getting climate-relevant analysis
            climate_relevant = False
            for analysis in data['neighborhood_analyses']:
                for dimension_name, dimension in analysis['impact_analysis'].items():
                    if any(word in dimension['description'].lower() for word in ['temperature', 'heating', 'cold', 'climate']):
                        climate_relevant = True
            
            if climate_relevant:
                print("✅ CORRECT: Climate-relevant analysis provided!")
            else:
                print("❌ PROBLEM: Missing climate-relevant analysis")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting exploratory API tests...")
    test_exploratory_api()
    test_climate_query_specifically()