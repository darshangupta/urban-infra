#!/usr/bin/env python3
"""
Test script for the enhanced Interpreter Agent
Tests multi-neighborhood detection and comparative analysis capabilities
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from agents.interpreter import InterpreterAgent

def test_interpreter():
    """Test the enhanced interpreter with comparative queries"""
    
    # Initialize interpreter without CrewAI (use rule-based fallback)
    interpreter = InterpreterAgent()
    
    test_queries = [
        "Add affordable housing near BART in Hayes Valley",
        "How would more bike infrastructure affect businesses in the Marina vs the Mission?",
        "Compare walkability improvements between Marina and Mission",
        "What's the impact of bike lanes on local businesses in both neighborhoods?",
        "Make the Marina more walkable while respecting flood risks",
        "Increase density in Mission without displacing existing residents",
        "How do bike lanes affect businesses in Marina compared to Mission?"
    ]
    
    print("🧠 Testing Enhanced Interpreter Agent")
    print("=" * 70)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        print("-" * 50)
        
        result = interpreter.interpret_query(query)
        
        print(f"🏘️  Neighborhoods: {result.neighborhoods}")
        print(f"🎯 Intent: {result.intent}")
        print(f"⭐ Priority: {result.priority}")
        print(f"🔍 Focus: {result.focus}")
        print(f"🔄 Comparative: {result.comparative}")
        print(f"🔧 Elements: {result.specific_elements}")
        print(f"📊 Confidence: {result.confidence:.2f}")
        print(f"⚠️  Constraints: {result.constraints[:3]}...")  # Show first 3 constraints
        
        # Special analysis for comparative queries
        if result.comparative and len(result.neighborhoods) > 1:
            print(f"✨ COMPARATIVE ANALYSIS DETECTED!")
            print(f"   Comparing: {' vs '.join(result.neighborhoods)}")
            if "business_impact" in result.specific_elements:
                print(f"   Business focus: Marina (affluent retail) vs Mission (community businesses)")

if __name__ == "__main__":
    test_interpreter()