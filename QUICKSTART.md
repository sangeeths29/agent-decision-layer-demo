# Quick Start

Get it running in 5 minutes.

## 1. Install

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Add API Key

```bash
cp .env.example .env
```

Edit `.env`:
```env
OPENAI_API_KEY=your-key-here
SERPER_API_KEY=your-serper-key  # Optional, for better search
```

## 3. Run

```bash
python main.py
```

Should see:
```
Model: gpt-4o-mini
Starting API server on http://0.0.0.0:8000
```

## 4. Test It

Try each mode:

**RESPOND**
```bash
curl -X POST http://localhost:8000/infer \
  -H "Content-Type: application/json" \
  -d '{"query": "What is machine learning?"}'
```

**PLAN**
```bash
curl -X POST http://localhost:8000/infer \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I learn Python?"}'
```

**SEARCH**
```bash
curl -X POST http://localhost:8000/infer \
  -H "Content-Type: application/json" \
  -d '{"query": "Latest AI news"}'
```

**ACT**
```bash
curl -X POST http://localhost:8000/infer \
  -H "Content-Type: application/json" \
  -d '{"query": "Calculate 234 times 567"}'
```

## Interactive Mode

```bash
python interactive.py
```

Type queries directly, watch the router pick modes.

## Run Tests

```bash
python eval/run_eval.py
```

Tests 20 queries, checks routing accuracy and latency.

## API Docs

http://localhost:8000/docs for Swagger UI.

