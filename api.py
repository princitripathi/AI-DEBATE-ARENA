#!/usr/bin/env python
"""
Main entry point for the AI Debate Arena API.

This script starts the FastAPI web server for the AI Debate Arena application.
It provides the web interface for streaming debates with real-time rendering.
"""

from main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
