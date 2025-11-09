"""
The router - this is where the magic happens!
Takes any query and decides which mode to use: RESPOND, PLAN, SEARCH, or ACT
"""

from typing import Literal
from app.llm import llm_client

# Type hint for the four agent modes
AgentMode = Literal["RESPOND", "PLAN", "SEARCH", "ACT"]

ROUTER_SYSTEM_PROMPT = """You are a routing agent. Your ONLY job is to classify the user's query into exactly ONE of these four categories:

RESPOND - Simple questions that can be answered directly with existing knowledge. No tools needed.
Examples: "What is the capital of France?", "Explain photosynthesis", "Tell me about Python"

PLAN - Complex tasks requiring multiple steps or where information is missing.
Examples: "Help me plan a wedding", "I want to start a business", "How do I learn machine learning?"

SEARCH - Questions requiring current, real-time, or recent information not in training data.
Examples: "What's the weather today?", "Latest news on AI", "Current stock price of Tesla"

ACT - Questions requiring calculations, data processing, or code execution.
Examples: "Calculate 234 * 567", "Generate fibonacci numbers", "What's the square root of 12345?"

You must respond with ONLY ONE WORD: RESPOND, PLAN, SEARCH, or ACT.
No explanation. No punctuation. Just the mode name."""


def route_query(query: str) -> AgentMode:
    """
    Figures out which mode to use for this query.
    Uses the LLM itself as a classifier - pretty neat!
    """
    response = llm_client.generate(
        prompt=query,
        system_prompt=ROUTER_SYSTEM_PROMPT,
        temperature=0.0,  # Keep it consistent - same query = same mode
        max_tokens=10
    )
    
    # Clean up the response
    mode = response.strip().upper()
    
    # Make sure we got a valid mode
    valid_modes = ["RESPOND", "PLAN", "SEARCH", "ACT"]
    
    if mode not in valid_modes:
        # Sometimes the LLM adds extra text, so try to find the mode in there
        for valid_mode in valid_modes:
            if valid_mode in mode:
                return valid_mode
        
        # If all else fails, just default to RESPOND - it's the safest option
        return "RESPOND"
    
    return mode

