from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from agent import DebateAgent, DebateJudge
from dotenv import load_dotenv
import os
import json
import asyncio
from typing import AsyncGenerator

load_dotenv()

app = FastAPI(title="AI Debate Arena API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


@app.get("/api/debate")
async def debate_stream(request: Request, topic: str, rounds: int = 2):
    """
    Stream a live debate using Server-Sent Events (SSE).
    
    This endpoint mimics the exact same DebateAgent and DebateJudge
    logic from agent.py, but streams each argument as soon as it's
    generated instead of running the full debate first.
    """
    
    def debate_generator():
        # Create the same exact agents as in agent.py
        pro = DebateAgent(
            name="Dr. Alex Chen",
            position="FOR",
            expertise="technology economist and AI researcher"
        )
        con = DebateAgent(
            name="Prof. Sarah Martinez",
            position="AGAINST",
            expertise="labor economist and social policy expert"
        )
        judge = DebateJudge()
        
        # Send start message
        yield f"data: {json.dumps({'type': 'start', 'topic': topic, 'rounds': rounds, 'pro_name': pro.name, 'con_name': con.name})}\n\n"
        
        last_con_arg = ""
        
        for round_num in range(1, rounds + 1):
            # Send round start message
            yield f"data: {json.dumps({'type': 'round_start', 'round': round_num})}\n\n"
            
            # Generate pro argument
            pro_arg = pro.make_argument(topic, round_num, last_con_arg)
            yield f"data: {json.dumps({'type': 'argument', 'round': round_num, 'side': 'pro', 'name': pro.name, 'text': pro_arg})}\n\n"
            
            # Generate con argument
            con_arg = con.make_argument(topic, round_num, pro_arg)
            yield f"data: {json.dumps({'type': 'argument', 'round': round_num, 'side': 'con', 'name': con.name, 'text': con_arg})}\n\n"
            
            # Store last con argument for next round
            last_con_arg = con_arg
        
        # Generate and send verdict
        verdict = judge.evaluate(topic, pro, con)
        yield f"data: {json.dumps({'type': 'verdict', 'text': verdict['verdict']})}\n\n"
        
        # Send done message
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
    
    response = Response(debate_generator(), media_type="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Connection"] = "keep-alive"
    response.headers["X-Accel-Buffering"] = "no"
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
