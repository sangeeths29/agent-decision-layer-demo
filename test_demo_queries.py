#!/usr/bin/env python3
"""
Test script to verify all demo queries work before your presentation.
Run this before your demo to make sure everything is working!
"""

import requests
import json
import time
import sys

API_URL = "http://localhost:8000"

# Test queries for each mode
TEST_QUERIES = {
    "RESPOND": [
        "What is machine learning?",
        "Explain quantum computing in simple terms"
    ],
    "PLAN": [
        "How do I learn web development from scratch?",
        "Create a plan to build a mobile app"
    ],
    "SEARCH": [
        "Latest AI developments 2025",
        "Recent SpaceX launches",
        "Current Bitcoin price"
    ],
    "ACT": [
        "Calculate 15% tip on $87.50",
        "What's the square root of 12345?"
    ]
}


def test_health():
    """Check if server is running"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def test_query(query: str, expected_mode: str):
    """Test a single query"""
    try:
        response = requests.post(
            f"{API_URL}/infer",
            json={"query": query},
            timeout=30
        )
        
        if response.status_code != 200:
            return False, f"HTTP {response.status_code}", None
        
        data = response.json()
        actual_mode = data.get("mode", "UNKNOWN")
        latency = data.get("latency_ms", 0)
        
        if actual_mode == expected_mode:
            return True, actual_mode, latency
        else:
            return False, f"Expected {expected_mode}, got {actual_mode}", latency
            
    except requests.Timeout:
        return False, "TIMEOUT", None
    except Exception as e:
        return False, str(e), None


def main():
    print("=" * 70)
    print("🧪 DEMO QUERIES TEST - Verify Everything Works!")
    print("=" * 70)
    print()
    
    # Check server health
    print("1️⃣  Checking server health...")
    if not test_health():
        print("❌ ERROR: Server is not running!")
        print("   Start it with: python main.py")
        sys.exit(1)
    print("✅ Server is healthy\n")
    
    # Test each mode
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    for expected_mode, queries in TEST_QUERIES.items():
        print(f"2️⃣  Testing {expected_mode} mode...")
        print("-" * 50)
        
        for query in queries:
            total_tests += 1
            print(f"   Query: {query[:50]}...")
            
            success, result, latency = test_query(query, expected_mode)
            
            if success:
                passed_tests += 1
                latency_str = f"{latency:.0f}ms" if latency else "N/A"
                print(f"   ✅ PASS - Mode: {result}, Latency: {latency_str}")
            else:
                failed_tests.append((query, result))
                print(f"   ❌ FAIL - {result}")
            
            print()
            time.sleep(1)  # Rate limiting
    
    # Summary
    print("=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {len(failed_tests)}")
    print()
    
    if failed_tests:
        print("❌ Failed Tests:")
        for query, error in failed_tests:
            print(f"   - {query[:50]}... ({error})")
        print()
        print("⚠️  Some tests failed. Check the errors above.")
        sys.exit(1)
    else:
        print("🎉 ALL TESTS PASSED! Your demo is ready!")
        print()
        print("🚀 Next steps:")
        print("   1. Read DEMO_GUIDE.md for presentation tips")
        print("   2. Run: python interactive.py")
        print("   3. Use the guaranteed queries from DEMO_GUIDE.md")
        print()
        print("💪 You got this!")


if __name__ == "__main__":
    main()

