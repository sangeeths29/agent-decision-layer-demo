#!/usr/bin/env python3
"""
Interactive CLI for testing the Agentic AI system with custom prompts.
Type any query and get instant responses!
"""

import requests
import json
from typing import Optional

API_URL = "http://localhost:8000"


def print_banner():
    """Print welcome banner"""
    print("\n" + "="*70)
    print("🤖 INTERACTIVE AGENTIC AI DEMO")
    print("="*70)
    print("Type any query and watch the agent choose the right mode!")
    print("Commands: 'quit' or 'exit' to stop, 'clear' to clear screen")
    print("="*70 + "\n")


def check_server():
    """Check if server is running"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        response.raise_for_status()
        return True
    except:
        return False


def query_agent(prompt: str) -> Optional[dict]:
    """Send query to the agent"""
    try:
        response = requests.post(
            f"{API_URL}/infer",
            json={"query": prompt},
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def format_response(result: dict):
    """Pretty print the response"""
    print(f"\n{'='*70}")
    print(f"🎯 MODE: {result['mode']}")
    print(f"⏱️  LATENCY: {result['latency_ms']:.2f}ms")
    print(f"{'='*70}")
    print(f"\n📝 ANSWER:\n{result['answer']}\n")
    
    # Show additional info for specific modes
    if result['mode'] == 'ACT' and 'code' in result.get('metadata', {}).get('variables', {}):
        print(f"💻 GENERATED CODE:")
        print(result.get('code', 'N/A'))
        print(f"\n✅ RESULT: {result.get('result', 'N/A')}\n")
    
    if result['mode'] == 'SEARCH' and result.get('sources'):
        print(f"🔍 SOURCES:")
        for i, source in enumerate(result['sources'][:3], 1):
            print(f"  {i}. {source['title']}")
            print(f"     {source['url']}")
        print()
    
    if result['mode'] == 'PLAN' and result.get('plan'):
        plan = result['plan']
        if plan.get('steps'):
            print(f"📋 STEPS:")
            for i, step in enumerate(plan['steps'][:5], 1):
                print(f"  {i}. {step}")
            print()
    
    print(f"{'='*70}\n")


def main():
    """Main interactive loop"""
    print_banner()
    
    # Check server
    if not check_server():
        print("❌ ERROR: Server not running!")
        print("Start it with: python main.py")
        return
    
    print("✅ Server is running! Ready for your queries...\n")
    
    # Interactive loop
    while True:
        try:
            # Get user input
            query = input("💬 Your query: ").strip()
            
            # Handle commands
            if query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye! Thanks for using the Agentic AI Demo!\n")
                break
            
            if query.lower() == 'clear':
                print("\033c", end="")  # Clear screen
                print_banner()
                continue
            
            if not query:
                continue
            
            # Query the agent
            print("\n🤔 Agent is thinking...")
            result = query_agent(query)
            
            if result:
                format_response(result)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Thanks for using the Agentic AI Demo!\n")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}\n")


if __name__ == "__main__":
    main()

