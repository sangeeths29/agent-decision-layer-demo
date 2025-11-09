"""
RESPOND mode - the simplest one
Just answers the question directly using LLM knowledge, no fancy tools needed
"""

from app.llm import llm_client


RESPOND_SYSTEM_PROMPT = """You are a helpful AI assistant. Answer the user's question clearly and concisely.
Provide accurate information based on your knowledge. If you're not sure about something, say so."""


def handle_respond(query: str) -> dict:
    """
    Handles simple questions that the LLM already knows the answer to.
    No web search, no code execution - just pure knowledge.
    """
    answer = llm_client.generate(
        prompt=query,
        system_prompt=RESPOND_SYSTEM_PROMPT,
        temperature=0.7,  # A bit of creativity is fine here
        max_tokens=1000
    )
    
    return {
        "mode": "RESPOND",
        "answer": answer,
        "metadata": {
            "tool_used": None  # No tools used, just straight LLM
        }
    }

