# System Architecture

## How It Works

```
User Query
    ↓
┌───────────────────────────────────────┐
│         FastAPI /infer Endpoint       │
│              (app/api.py)             │
└─────────────────┬─────────────────────┘
                  ↓
┌───────────────────────────────────────┐
│           Router Agent                │
│          (app/router.py)              │
│                                       │
│  "Classify into: RESPOND/PLAN/       │
│   SEARCH/ACT"                        │
└─────────────────┬─────────────────────┘
                  ↓
         ┌────────┴────────┐
         │  Route Decision │
         └────────┬────────┘
                  ↓
    ┌─────────────┼─────────────┐
    ↓             ↓             ↓             ↓
┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐
│ RESPOND │  │  PLAN   │  │ SEARCH  │  │   ACT   │
│         │  │         │  │         │  │         │
│ Simple  │  │ Multi-  │  │ Web     │  │ Python  │
│ LLM     │  │ step    │  │ Search  │  │ Code    │
│ Answer  │  │ Planning│  │ + LLM   │  │ Exec    │
└────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘
     │            │            │            │
     └────────────┴────────────┴────────────┘
                  ↓
          ┌───────────────┐
          │   Response    │
          │ {mode, answer,│
          │  latency, ... }│
          └───────────────┘
```

## Components

### Router (`app/router.py`)

The brain. Takes a query, returns which mode to use.

- Uses GPT-4o-mini as a classifier
- Temperature = 0 (consistent decisions)
- Fallback to RESPOND if uncertain

```python
query = "What's the weather?"
mode = route_query(query)  # Returns: "SEARCH"
```

### LLM Client (`app/llm.py`)

Wrapper around OpenAI API.

```python
from app.llm import llm_client

response = llm_client.generate(
    prompt="What is AI?",
    temperature=0.7
)
```

### Pipelines

**RESPOND** (`respond.py`)
- Query → LLM → Answer
- No tools

**PLAN** (`plan.py`)
- Query → LLM w/ planning prompt → Parse into steps/missing info
- Returns structured breakdown

**SEARCH** (`search.py`)
- Query → Serper/DuckDuckGo → LLM synthesis → Answer + sources
- Automatically adds "2025" to time-sensitive queries

**ACT** (`act.py`)
- Query → LLM generates Python → Safe execution → Result
- Restricted environment: no file I/O, no imports (except math)

## Config (`app/config.py`)

Loads from `.env`:
```env
OPENAI_API_KEY=...
SERPER_API_KEY=...
API_HOST=0.0.0.0
API_PORT=8000
```

## API (`app/api.py`)

**Endpoints:**
- `POST /infer` - Main endpoint
- `GET /health` - Health check
- `GET /` - Info

**Request Format**:
```json
{
  "query": "string"
}
```

**Response Format**:
```json
{
  "mode": "RESPOND|PLAN|SEARCH|ACT",
  "answer": "string",
  "latency_ms": 1234.56,
  "metadata": {...}
}
```

## Evaluation

Run `python eval/run_eval.py` to test:
- Routing accuracy (right mode?)
- Answer correctness (contains expected terms?)
- Latency

Score: 30% routing + 50% answer + 20% latency

## Test Files (`tasks/*.yaml`)

20 test cases across 4 files:
```yaml
tasks:
  - id: task_id
    query: "User question"
    expected_mode: RESPOND
    expected_contains: ["term1", "term2"]
```

## Example Flow: "Calculate 15% of 850"

```
1. POST /infer {"query": "Calculate 15% of 850"}
2. Router → ACT
3. ACT → generates code: result = 850 * 0.15
4. Execute → 127.5
5. Return: {"mode": "ACT", "answer": "Result: 127.5"}
```

## Design Choices

**Why four modes?**  
Covers main agent behaviors: knowledge, planning, tools, code execution.

**Why explicit routing vs function calling?**  
- Clearer decisions
- Easier to debug
- Works with any LLM provider
- Faster (one routing call)

Downside: Can't combine multiple tools in one query.

**Safety in ACT mode:**  
Blocks file I/O, imports (except math), eval(), network calls.

## Extending

**Add a new mode:**
1. Create `app/pipelines/new_mode.py`
2. Add handler function
3. Update router prompt
4. Add to API dispatch
5. Create test cases

**Add tools to existing modes:**
```python
# Example: Add database to SEARCH
def handle_search(query):
    web = web_search(query)
    db = database_search(query)
    return synthesize(web + db)
```

## Performance

Typical latency:
- Router: ~500-1000ms
- RESPOND: +500-1500ms
- PLAN: +1000-2000ms
- SEARCH: +2000-4000ms (web search)
- ACT: +800-1800ms

Total: 1-5 seconds

**Optimize:**
- Cache routing decisions
- Use streaming responses
- Smaller models for routing

## Security

Current:
- Restricted Python execution
- Input validation
- Timeouts

For production, add:
- API auth
- Rate limiting
- Proper secrets management
- Audit logging

