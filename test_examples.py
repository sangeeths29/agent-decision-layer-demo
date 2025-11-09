"""
Example test script to demonstrate the agent modes.
Run this after starting the server with: python main.py
"""

import requests
import json
from time import sleep


API_URL = "http://localhost:8000"


def test_query(query: str, description: str):
    """Test a single query"""
    print(f"\n{'='*60}")
    print(f"TEST: {description}")
    print(f"Query: {query}")
    print("-" * 60)
    
    try:
        response = requests.post(
            f"{API_URL}/infer",
            json={"query": query},
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        
        print(f"Mode: {result['mode']}")
        print(f"Latency: {result['latency_ms']:.2f}ms")
        print(f"\nAnswer:\n{result['answer'][:300]}...")
        
        if 'sources' in result:
            print(f"\nSources:")
            for source in result.get('sources', [])[:2]:
                print(f"  - {source['title']}")
        
        if 'code' in result:
            print(f"\nGenerated Code:\n{result['code']}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def main():
    """Run example tests"""
    print("🤖 Agentic AI Demo - Example Tests")
    print("="*60)
    print("Make sure the server is running: python main.py")
    print("="*60)
    
    # Check health
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        response.raise_for_status()
        print("✅ Server is running!\n")
    except:
        print("❌ Server not running. Start with: python main.py")
        return
    
    # Test each mode
    tests = [
        ("What is the capital of France?", "RESPOND: Simple Question"),
        ("Help me plan a startup launch", "PLAN: Multi-step Planning"),
        ("What's the latest news about SpaceX?", "SEARCH: Current Information"),
        ("Calculate the factorial of 10", "ACT: Mathematical Calculation"),
    ]
    
    for query, description in tests:
        test_query(query, description)
        sleep(1)  # Rate limiting
    
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60)


if __name__ == "__main__":
    main()
