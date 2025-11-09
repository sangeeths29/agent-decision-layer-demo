"""
Entry point - run this to start the server!
"""

import uvicorn
from app.config import config


if __name__ == "__main__":
    print("=" * 60)
    print("🤖 Agentic AI Demo - Router-based Agent System")
    print("=" * 60)
    print(f"Model: {config.openai_model}")
    print(f"\nStarting API server on http://{config.api_host}:{config.api_port}")
    print(f"Docs available at http://{config.api_host}:{config.api_port}/docs")
    print("=" * 60)
    
    # Start the server with hot reload (so changes auto-update)
    uvicorn.run(
        "app.api:app",
        host=config.api_host,
        port=config.api_port,
        reload=True
    )

