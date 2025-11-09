# Agentic AI Demo - Router-based Decision Layer

A backend project showing how adding a router transforms a plain LLM into an agent.

## What This Does

The core idea: an LLM that can decide which tool to use based on the query.

The router classifies every query into one of four modes:
- **RESPOND** - Direct answer (no tools needed)
- **PLAN** - Break down complex tasks into steps
- **SEARCH** - Get current info from the web
- **ACT** - Run Python code for calculations

Without the router, it's just a chatbot. With it, it's an agent that can make decisions.

## Project Structure

```
agents-demo/
├─ app/
│  ├─ config.py          # Settings
│  ├─ llm.py             # OpenAI client
│  ├─ router.py          # The brain - decides which mode
│  ├─ pipelines/
│  │  ├─ respond.py      # Simple answers
│  │  ├─ plan.py         # Planning
│  │  ├─ search.py       # Web search (Serper + DuckDuckGo)
│  │  └─ act.py          # Python execution
│  └─ api.py             # FastAPI endpoint
├─ tasks/                # Test cases (YAML)
├─ eval/                 # Evaluation tools
├─ main.py               # Start here
└─ requirements.txt
```

## Setup

**1. Install dependencies**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**2. Add your API keys**

Create `.env` from `.env.example`:
```bash
cp .env.example .env
```

Edit `.env` and add:
```env
OPENAI_API_KEY=your-key-here
SERPER_API_KEY=your-key-here  # Optional but recommended for search
```

Get keys from:
- OpenAI: https://platform.openai.com/api-keys
- Serper: https://serper.dev (free tier available)

**3. Run it**
```bash
python main.py
```

Server starts at `http://localhost:8000`

## Usage

Send queries to the `/infer` endpoint:

```bash
curl -X POST http://localhost:8000/infer \
  -H "Content-Type: application/json" \
  -d '{"query": "What is machine learning?"}'
```

Response:
```json
{
  "mode": "RESPOND",
  "answer": "Machine learning is...",
  "latency_ms": 1234.56
}
```

Or use the interactive CLI:
```bash
python interactive.py
```

API docs: `http://localhost:8000/docs`

## The Four Modes

**1. RESPOND** - Direct answers
- For: General knowledge questions
- Example: "What is photosynthesis?"
- Just uses the LLM, no tools

**2. PLAN** - Multi-step breakdown
- For: Complex tasks needing planning
- Example: "How do I learn Python in 30 days?"
- Returns steps, identifies missing info

**3. SEARCH** - Web search + synthesis
- For: Current/recent information
- Example: "Latest AI developments"
- Uses Serper API (Google) + DuckDuckGo fallback
- Automatically adds "2025" to time-sensitive queries

**4. ACT** - Python execution
- For: Calculations and data tasks  
- Example: "Calculate square root of 12345"
- Generates code → runs it safely → returns result

## Safety (ACT Mode)

Python execution is restricted:

**Allowed:** Math, basic operations, loops  
**Blocked:** File I/O, imports (except math), eval(), system calls

## Testing

Run the evaluation suite:
```bash
python eval/run_eval.py
```

Tests routing accuracy, correctness, and latency across 20 test cases.

## Troubleshooting

**Port 8000 in use?**
```bash
lsof -i :8000  # Find what's using it
export API_PORT=8080  # Use different port
```

**OpenAI errors?**
Check your API key is set: `echo $OPENAI_API_KEY`

## Tech Stack

- FastAPI
- OpenAI (gpt-4o-mini)
- Serper API for search
- DuckDuckGo (fallback)

## License

MIT - use it however you want.

