"""
FastAPI app - the main API server
Has one main endpoint: /infer (where all the magic happens)
"""

import time
from typing import Any, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.router import route_query
from app.pipelines.respond import handle_respond
from app.pipelines.plan import handle_plan
from app.pipelines.search import handle_search
from app.pipelines.act import handle_act


app = FastAPI(
    title="Agentic AI Demo",
    description="Router-based agent with RESPOND/PLAN/SEARCH/ACT modes",
    version="1.0.0"
)


class InferRequest(BaseModel):
    """What the user sends us"""
    query: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is the capital of France?"
            }
        }


class InferResponse(BaseModel):
    """What we send back"""
    mode: str
    answer: str
    latency_ms: float
    metadata: Dict[str, Any] = {}


@app.get("/")
def root():
    """Root endpoint - just shows what's available"""
    return {
        "message": "Agentic AI Demo API",
        "endpoints": {
            "/infer": "POST - Submit a query to the agent",
            "/health": "GET - Health check"
        }
    }


@app.get("/health")
def health():
    """Quick health check - is the server alive?"""
    return {"status": "healthy"}


@app.post("/infer", response_model=InferResponse)
def infer(request: InferRequest) -> InferResponse:
    """
    The main endpoint - this is where all the magic happens!
    Takes a query, routes it to the right mode, and returns the answer.
    """
    start_time = time.time()
    
    try:
        # Step 1: Figure out which mode to use
        mode = route_query(request.query)
        
        # Step 2: Run the right pipeline
        if mode == "RESPOND":
            result = handle_respond(request.query)
        elif mode == "PLAN":
            result = handle_plan(request.query)
        elif mode == "SEARCH":
            result = handle_search(request.query)
        elif mode == "ACT":
            result = handle_act(request.query)
        else:
            raise ValueError(f"Got an unknown mode somehow: {mode}")
        
        # Step 3: Calculate how long this took
        latency_ms = (time.time() - start_time) * 1000
        
        # Step 4: Send it back
        return InferResponse(
            mode=result["mode"],
            answer=result["answer"],
            latency_ms=round(latency_ms, 2),
            metadata=result.get("metadata", {})
        )
        
    except Exception as e:
        # Something went wrong - let the user know
        raise HTTPException(status_code=500, detail=str(e))

