#!/usr/bin/env python3
"""
Quick test of Agent 1 (Interpreter)
"""

import sys
import os
sys.path.append('backend')

from backend.app.agents.interpreter import InterpreterAgent

def test_interpreter():
    print("🤖 Testing Agent 1 (Interpreter)")
    print("=" * 50)
    
    # Initialize agent (will use mock/fallback mode without OpenAI key)
    interpreter = InterpreterAgent()
    
    test_queries = [
        "Add affordable housing near BART in Hayes Valley",
        "Make the Marina more walkable while respecting flood risks", 
        "Increase density in Mission without displacing existing residents"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test Query {i}: {query}")
        print("-" * 40)
        
        try:
            result = interpreter.interpret_query(query)
            print(f"✅ Structured Output:")
            print(f"  Neighborhood: {result.neighborhood}")
            print(f"  Intent: {result.intent}")
            print(f"  Constraints: {result.constraints}")
            print(f"  Target Metrics: {result.target_metrics}")
            print(f"  Spatial Focus: {result.spatial_focus}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n🎉 Agent 1 testing complete!")

if __name__ == "__main__":
    test_interpreter()