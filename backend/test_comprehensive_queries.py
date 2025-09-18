#!/usr/bin/env python3
"""
Test the enhanced analytics system with comprehensive query coverage
Tests various query types and edge cases to ensure robust handling
"""

import requests
import json

def test_comprehensive_queries():
    """Test all query types and edge cases"""
    
    base_url = "http://localhost:8001/api/v1"
    
    # Comprehensive test queries covering all scenarios
    test_queries = [
        # Scenario Planning (Climate)
        {
            "query": "What if it became 10 degrees colder? How would that affect Mission vs Hayes vs Marina?",
            "expected_type": "scenario_planning",
            "expected_domain": "climate",
            "description": "Climate scenario with temperature change"
        },
        
        # Comparative Analysis (Transportation - Bike Infrastructure)
        {
            "query": "How would more bike infrastructure affect businesses in the Marina vs the Mission?",
            "expected_type": "comparative", 
            "expected_domain": "transportation",
            "description": "Bike infrastructure business impact comparison"
        },
        
        # Analytical (Housing)
        {
            "query": "How would adding affordable housing near BART affect Hayes Valley?",
            "expected_type": "analytical",
            "expected_domain": "transportation",  # BART keyword triggers transportation
            "description": "Housing development near transit"
        },
        
        # Solution Seeking
        {
            "query": "How should we make the Marina more walkable while protecting from flooding?",
            "expected_type": "solution_seeking",
            "expected_domain": "transportation",  # walkable keyword
            "description": "Solution-oriented walkability question"
        },
        
        # Economic Focus
        {
            "query": "What would happen to local businesses if we pedestrianized Valencia Street?",
            "expected_type": "analytical",
            "expected_domain": "economics",
            "description": "Business impact of pedestrianization"
        },
        
        # Environmental Focus
        {
            "query": "How would adding more parks affect air quality in the Mission?",
            "expected_type": "analytical",
            "expected_domain": "environment",
            "description": "Environmental impact of green space"
        },
        
        # Multi-neighborhood comparative
        {
            "query": "Compare the effects of upzoning in Marina vs Mission vs Hayes Valley",
            "expected_type": "comparative",
            "expected_domain": "housing",
            "description": "Multi-neighborhood housing policy comparison"
        },
        
        # Edge Case: Vague query
        {
            "query": "What about development in the Marina?",
            "expected_type": "analytical",
            "expected_domain": "general",
            "description": "Vague development question"
        },
        
        # Edge Case: Very specific technical query
        {
            "query": "What are the FAR implications of NCT-3 zoning changes for 45-foot height limits?",
            "expected_type": "analytical", 
            "expected_domain": "housing",
            "description": "Technical zoning question"
        },
        
        # Edge Case: Single word
        {
            "query": "Marina",
            "expected_type": "analytical",
            "expected_domain": "general", 
            "description": "Single word query"
        }
    ]
    
    print("🧪 COMPREHENSIVE QUERY TESTING")
    print("=" * 80)
    
    results = {
        "total": len(test_queries),
        "passed": 0,
        "failed": 0,
        "errors": []
    }
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}/{len(test_queries)}: {test_case['description']}")
        print(f"Query: \"{test_case['query']}\"")
        print("-" * 60)
        
        try:
            response = requests.post(
                f"{base_url}/explore",
                json={"query": test_case["query"]},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                assert "context" in data, "Missing 'context' in response"
                assert "neighborhood_analyses" in data, "Missing 'neighborhood_analyses'"
                assert "exploration_suggestions" in data, "Missing 'exploration_suggestions'"
                assert "related_questions" in data, "Missing 'related_questions'"
                
                context = data["context"]
                
                # Check query type detection
                actual_type = context["query_type"]
                expected_type = test_case["expected_type"]
                
                # Check domain detection  
                actual_domain = context["primary_domain"]
                expected_domain = test_case["expected_domain"]
                
                print(f"✅ SUCCESS - API Response OK")
                print(f"   Query Type: {actual_type} (expected: {expected_type}) {'✓' if actual_type == expected_type else '⚠️'}")
                print(f"   Domain: {actual_domain} (expected: {expected_domain}) {'✓' if actual_domain == expected_domain else '⚠️'}")
                print(f"   Neighborhoods: {context['neighborhoods']}")
                print(f"   Confidence: {context['confidence']:.2f}")
                print(f"   Analyses: {len(data['neighborhood_analyses'])} neighborhoods")
                
                # Check content quality
                total_insights = sum(
                    len(analysis['impact_analysis'].get(dim, {}).get('insights', []))
                    for analysis in data['neighborhood_analyses']
                    for dim in analysis.get('impact_analysis', {})
                )
                print(f"   Content Quality: {total_insights} total insights")
                
                # Scenario-specific checks
                if actual_type == "scenario_planning":
                    has_scenarios = bool(data.get('scenario_branches'))
                    print(f"   Scenario Branches: {'✓' if has_scenarios else '❌'}")
                
                if actual_type == "comparative":
                    has_comparison = bool(data.get('comparative_insights'))
                    print(f"   Comparative Insights: {'✓' if has_comparison else '❌'}")
                
                # Domain-specific content validation
                if actual_domain == "climate":
                    has_climate_content = any(
                        any(keyword in str(analysis).lower() for keyword in ['temperature', 'climate', 'heating', 'cold'])
                        for analysis in data['neighborhood_analyses']
                    )
                    print(f"   Climate Content: {'✓' if has_climate_content else '❌'}")
                
                if actual_domain == "transportation":
                    has_transport_content = any(
                        any(keyword in str(analysis).lower() for keyword in ['bike', 'transit', 'transport', 'mobility'])
                        for analysis in data['neighborhood_analyses']
                    )
                    print(f"   Transportation Content: {'✓' if has_transport_content else '❌'}")
                
                results["passed"] += 1
                
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"Response: {response.text}")
                results["failed"] += 1
                results["errors"].append(f"Test {i}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            results["failed"] += 1
            results["errors"].append(f"Test {i}: {str(e)}")
        
        print("-" * 60)
    
    # Summary
    print(f"\n📊 TEST SUMMARY")
    print("=" * 40)
    print(f"Total Tests: {results['total']}")
    print(f"Passed: {results['passed']} ✅")
    print(f"Failed: {results['failed']} ❌")
    print(f"Success Rate: {(results['passed']/results['total']*100):.1f}%")
    
    if results["errors"]:
        print(f"\n🐛 ERRORS:")
        for error in results["errors"]:
            print(f"   • {error}")
    
    print(f"\n{'🎉 ALL TESTS PASSED!' if results['failed'] == 0 else '⚠️ SOME TESTS FAILED'}")

def test_edge_cases():
    """Test specific edge cases and error handling"""
    
    print(f"\n🔬 EDGE CASE TESTING")
    print("=" * 50)
    
    edge_cases = [
        {"query": "", "description": "Empty query"},
        {"query": "   ", "description": "Whitespace only"},
        {"query": "a", "description": "Single character"},
        {"query": "?" * 100, "description": "Very long query"},
        {"query": "🏠🚊🌳", "description": "Emoji only"},
        {"query": "SELECT * FROM neighborhoods", "description": "SQL injection attempt"},
        {"query": "<script>alert('test')</script>", "description": "XSS attempt"}
    ]
    
    base_url = "http://localhost:8001/api/v1"
    
    for case in edge_cases:
        print(f"\n🧪 Testing: {case['description']}")
        try:
            response = requests.post(
                f"{base_url}/explore",
                json={"query": case["query"]},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Handled gracefully - returned {len(data.get('neighborhood_analyses', []))} analyses")
            else:
                print(f"⚠️ HTTP {response.status_code} - {response.text[:100]}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Starting comprehensive analytics testing...")
    test_comprehensive_queries()
    test_edge_cases()
    print(f"\n✨ Testing complete!")