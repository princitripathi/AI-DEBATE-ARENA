from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from agent import DebateAgent, DebateJudge
from dotenv import load_dotenv
from common import get_expertise_by_persona
import os
import json

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


@app.get("/api/personas")
async def get_personas():
    """Get available persona pairs for debate"""
    return {
        "economists": {"pro": "Dr. Alex Chen", "con": "Prof. Sarah Martinez"},
        "lawyers": {"pro": "Prof. Michael Torres", "con": "Dr. Elena Rodriguez"},
        "scientists": {"pro": "Dr. James Wilson", "con": "Prof. Lisa Chen"},
        "philosophers": {"pro": "Prof. Robert Stevens", "con": "Dr. Amanda Collins"}
    }


@app.get("/api/debate")
async def debate_stream(request: Request, topic: str, rounds: int = 2, persona: str = "economists"):
    """
    Stream a live debate using Server-Sent Events (SSE).
    
    This endpoint mimics the exact same DebateAgent and DebateJudge
    logic from agent.py, but streams each argument as soon as it's
    generated instead of running the full debate first.
    """
    
    def debate_generator():
        # Get persona pairs
        personas = {
            "economists": {"pro": "Dr. Alex Chen", "con": "Prof. Sarah Martinez"},
            "lawyers": {"pro": "Prof. Michael Torres", "con": "Dr. Elena Rodriguez"},
            "scientists": {"pro": "Dr. James Wilson", "con": "Prof. Lisa Chen"},
            "philosophers": {"pro": "Prof. Robert Stevens", "con": "Dr. Amanda Collins"}
        }
        
        # Create the same exact agents as in agent.py using selected persona
        selected_persona = personas.get(persona, personas["economists"])
        
        pro = DebateAgent(
            name=selected_persona["pro"],
            position="FOR",
            expertise=get_expertise_by_persona(persona, "pro")
        )
        con = DebateAgent(
            name=selected_persona["con"],
            position="AGAINST",
            expertise=get_expertise_by_persona(persona, "con")
        )
        judge = DebateJudge()
        
        # Send start message
        yield f"data: {json.dumps({'type': 'start', 'topic': topic, 'rounds': rounds, 'pro_name': pro.name, 'con_name': con.name})}\n\n"
        
        # Update agent names with persona's expertise for proper streaming
        pro.name = personas.get(persona, personas["economists"])["pro"]
        con.name = personas.get(persona, personas["economists"])["con"]
        
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
    
    return StreamingResponse(
        debate_generator(),
        media_type="text/event-stream"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
