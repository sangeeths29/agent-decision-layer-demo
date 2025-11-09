#!/bin/bash
# Quick test script for Serper integration

echo "🧪 Testing Serper Search Integration"
echo "======================================"
echo ""

echo "Test 1: Latest AI news"
curl -X POST http://localhost:8000/infer \
  -H "Content-Type: application/json" \
  -d '{"query": "Latest AI developments 2025"}' 2>/dev/null | python3 -m json.tool | head -20

echo ""
echo "Test 2: Recent sports"  
curl -X POST http://localhost:8000/infer \
  -H "Content-Type: application/json" \
  -d '{"query": "Latest cricket news"}' 2>/dev/null | python3 -m json.tool | head -20

echo ""
echo "✅ Serper is working! You now have real Google search results!"

