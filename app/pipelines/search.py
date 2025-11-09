"""
SEARCH mode - gets real-time info from the web
Uses Serper API (Google) for best results, falls back to DuckDuckGo if needed
"""

import os
from typing import List, Dict
import requests
from app.llm import llm_client


def web_search_serper(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Search using Serper API - basically Google search results.
    Much more reliable than DuckDuckGo! Get a free API key at serper.dev
    """
    serper_api_key = os.getenv("SERPER_API_KEY")
    
    if not serper_api_key:
        return []  # No key, no search
    
    try:
        url = "https://google.serper.dev/search"
        
        payload = {
            "q": query,
            "num": max_results
        }
        
        headers = {
            "X-API-KEY": serper_api_key,
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        # Grab the actual search results (the "organic" ones)
        for item in data.get("organic", [])[:max_results]:
            results.append({
                "title": item.get("title", ""),
                "snippet": item.get("snippet", ""),
                "url": item.get("link", "")
            })
        
        return results
        
    except Exception as e:
        print(f"Serper search error: {e}")
        return []


def web_search_duckduckgo(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    DuckDuckGo search - free but can be unreliable.
    Only used as a fallback if Serper doesn't work.
    """
    try:
        from duckduckgo_search import DDGS
        
        with DDGS() as ddgs:
            results = []
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "snippet": r.get("body", ""),
                    "url": r.get("href", "")
                })
            return results
    except Exception as e:
        print(f"DuckDuckGo search error: {e}")
        return []


def web_search(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Main search function - tries Serper first, falls back to DuckDuckGo.
    Also adds "2025" to queries that seem time-sensitive for better results.
    """
    # Smart trick: add "2025" to time-sensitive queries for more current results
    recency_keywords = ['latest', 'recent', 'current', 'today', 'now', 'when']
    enhanced_query = query
    
    # If they're asking about "latest" or "recent" stuff, specify 2025
    if any(keyword in query.lower() for keyword in recency_keywords):
        if '2025' not in query and '2024' not in query:
            enhanced_query = f"{query} 2025"
    
    # Try Serper first (best results)
    results = web_search_serper(enhanced_query, max_results)
    
    if results:
        print(f"✓ Serper search returned {len(results)} results")
        return results
    
    # Serper didn't work, try DuckDuckGo
    print("→ Falling back to DuckDuckGo...")
    results = web_search_duckduckgo(enhanced_query, max_results)
    
    if results:
        print(f"✓ DuckDuckGo search returned {len(results)} results")
        return results
    
    # Neither worked - let the user know
    print("✗ No results from any search provider")
    return [{
        "title": "Search Unavailable",
        "snippet": "Unable to fetch search results. This may be due to API limits or network issues.",
        "url": ""
    }]


SYNTHESIS_SYSTEM_PROMPT = """You are a research assistant. You will be given search results from the web.
Your job is to synthesize the information and provide a clear, accurate answer to the user's question.

Guidelines:
- Use only information from the provided search results
- Be PRECISE about context and scope (e.g., if results mention "Test cricket", specify it - don't generalize to "all cricket")
- If the results don't fully answer the question, explicitly say so
- Don't make assumptions beyond what the search results explicitly state
- Be concise but comprehensive
- Cite sources when relevant (mention the source name)
- If search results are unavailable, acknowledge it and suggest checking official sources
- When information is limited to a specific category, make that clear (e.g., "in Test format" vs "across all formats")
"""


def handle_search(query: str) -> dict:
    """
    Searches the web and synthesizes an answer.
    This is a two-step process: 1) search, 2) have LLM read and summarize results.
    """
    # Step 1: Get search results from the web
    search_results = web_search(query, max_results=5)
    
    # Step 2: Format them nicely for the LLM to read
    results_text = "Search Results:\n\n"
    for i, result in enumerate(search_results, 1):
        results_text += f"Result {i}:\n"
        results_text += f"Title: {result['title']}\n"
        results_text += f"Content: {result['snippet']}\n"
        results_text += f"URL: {result['url']}\n\n"
    
    # Step 3: Ask the LLM to synthesize an answer from the search results
    synthesis_prompt = f"{results_text}\n\nUser Question: {query}\n\nProvide a clear answer based on the search results above."
    
    answer = llm_client.generate(
        prompt=synthesis_prompt,
        system_prompt=SYNTHESIS_SYSTEM_PROMPT,
        temperature=0.5,  # Lower temp for more factual synthesis
        max_tokens=1000
    )
    
    # Pull out the top sources (useful for citations)
    sources = [
        {
            "title": r["title"],
            "url": r["url"]
        }
        for r in search_results
        if r.get("url") and r["title"] != "Search Unavailable"
    ]
    
    return {
        "mode": "SEARCH",
        "answer": answer,
        "sources": sources[:3],  # Just show top 3 to keep it clean
        "metadata": {
            "tool_used": "serper" if os.getenv("SERPER_API_KEY") else "duckduckgo",
            "num_results": len([r for r in search_results if r["title"] != "Search Unavailable"])
        }
    }

