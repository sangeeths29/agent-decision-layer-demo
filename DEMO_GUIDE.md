# Demo Guide

Good queries to show off each mode.

## Quick Start

```bash
source venv/bin/activate
python interactive.py
```

## Demo Flow

### 1. RESPOND - Basic Knowledge

Simple queries the LLM already knows:

```
What is machine learning?
Explain quantum computing
Difference between Python and JavaScript?
```

### 2. PLAN - Multi-step Tasks

Complex tasks that need breakdown:

```
How do I learn web development?
Create a plan to build a mobile app
Steps to start a podcast
Improve Python skills in 3 months
```

### 3. SEARCH - Current Info

Queries needing real-time data:

**Tech:**
```
Latest AI developments 2025
Recent SpaceX launches
What's new with ChatGPT
Tesla stock price
```

**Space:**
```
Latest Mars rover news
Recent astronomy discoveries
Current ISS missions
```

**Current events:**
```
Latest climate conference news
Recent tech acquisitions
What happened at COP29
```

### 4. ACT - Python Execution

Computational tasks:

```
Calculate 15% tip on $87.50
Square root of 12345?
Compound interest on $10000 at 5% for 10 years
First 20 Fibonacci numbers
Area of circle with radius 7.5
```

## Presentation Flow

**Opening:**  
"This shows how adding a router turns an LLM into an agent. The router picks one of four modes for each query."

**Demo (3-4 min):**
1. RESPOND: "What is machine learning?" → Direct answer, no tools
2. PLAN: "How do I learn web development?" → Multi-step breakdown
3. SEARCH: "Latest SpaceX launches" → Real 2025 data (the impressive part)
4. ACT: "Calculate compound interest $5000 at 6% for 15 years" → Runs Python code

**Closing:**  
"The router classifies automatically. No hardcoded rules, just one decision layer."

## Quick Demo (90 sec)

```
What is Python?                    # RESPOND
How do I build a website?          # PLAN
Latest AI news                     # SEARCH
Calculate 18% tip on $156.80       # ACT
```

Say: "Watch the mode change."

## Tips

**Do:**
- Show all 4 modes
- Use SEARCH for current data (most impressive)
- Point out the 3-6 second latency for search (shows it's real)
- Emphasize backend-only architecture

**Don't:**
- Use very specific stats (can be unreliable)
- Skip modes
- Apologize for latency (it proves it's doing real searches)

## Reliable Search Queries

```
Latest AI developments
Recent SpaceX launches
Current Bitcoin price
Latest climate news
Recent quantum computing breakthroughs
Tesla news
Latest NASA missions
Recent AI model releases
```

## Q&A Prep

**"How does the router work?"**  
Uses GPT-4o-mini as a classifier with a strict prompt. Returns one mode. Temperature=0 for consistency.

**"What makes this an agent?"**  
The decision layer. A plain LLM can only answer from training data. This agent decides WHEN to search the web, WHEN to write code, WHEN to plan.

**"Is this production-ready?"**  
Architecture is solid - FastAPI, Serper API for search, proper error handling. Would need auth, rate limiting, and monitoring for prod.

**"Why backend-only?"**  
Wanted to focus on the core concept: the decision layer. Frontend would just distract from the routing logic.

## Show the Code

If asked:
```bash
cat app/router.py              # Router logic
cat app/pipelines/search.py    # Search pipeline
cat app/api.py                 # API endpoint
```

## Key Points

- 4 modes: RESPOND, PLAN, SEARCH, ACT
- Serper API for Google search
- OpenAI gpt-4o-mini
- FastAPI backend
- Safe Python execution (restricted environment)
- 3-6 second latency for search (proves it's real)
- Modular, each pipeline is independent

## Troubleshooting

**Server not responding:**
```bash
lsof -ti:8000 | xargs kill -9 2>/dev/null
python main.py
```

**Search returns nothing:**
- Use the reliable queries above
- Check `.env` has SERPER_API_KEY

**Import errors:**
```bash
source venv/bin/activate
```

