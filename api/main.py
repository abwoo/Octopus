import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import queue
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List

# Standard Octopus imports
from core.agent import Agent

# Setup FastAPI
app = FastAPI(title="Octopus Dashboard API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared state (Agent instance will be injected here)
agent_instance = None
config = {
    "workspace": "workspace",
    "log_file": "logs/actions.log",
    "adapter": "file" # Use file adapter for API injection
}

class ActionRequest(BaseModel):
    type: str
    params: Dict[str, Any] = {}

@app.on_event("startup")
async def startup_event():
    global agent_instance
    # Ensure workspace exists
    if not os.path.exists("workspace"):
        os.makedirs("workspace")
    
    # Initialize Agent
    # Note: We'll modify Agent to support external queue injection later if needed
    # For now, we'll use the file adapter mechanism or direct queue access
    agent_instance = Agent(config)
    import threading
    threading.Thread(target=agent_instance.start, daemon=True).start()

@app.get("/status")
async def get_status():
    return {"status": "ready" if agent_instance and agent_instance._running else "initializing"}

@app.post("/action")
async def execute_action(action: ActionRequest):
    if not agent_instance or not agent_instance._running:
        raise HTTPException(status_code=503, detail="Agent not running")
    
    # Put action directly into the agent's queue
    agent_instance._action_queue.put(action.dict())
    return {"status": "queued", "action": action.type}

@app.get("/logs")
async def get_logs(limit: int = 50):
    log_file = config["log_file"]
    if not os.path.exists(log_file):
        return {"logs": []}
    
    with open(log_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        return {"logs": lines[-limit:]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
