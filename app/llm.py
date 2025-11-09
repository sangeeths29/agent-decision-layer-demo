"""
LLM client - handles all OpenAI API calls
"""

from typing import Optional
from openai import OpenAI
from app.config import config


class LLMClient:
    """Simple OpenAI client wrapper"""
    
    def __init__(self):
        if not config.openai_api_key:
            raise ValueError("Hey! You need to set OPENAI_API_KEY in your .env file")
        
        self.client = OpenAI(api_key=config.openai_api_key)
        self.model = config.openai_model
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Get a completion from OpenAI"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=config.llm_timeout
        )
        
        return response.choices[0].message.content.strip()


# Create a global instance so we don't have to initialize it everywhere
llm_client = LLMClient()

