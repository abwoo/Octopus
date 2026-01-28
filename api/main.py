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

from api.llm_engine import LLMEngine

# Setup FastAPI
app = FastAPI(title="Octopus Dashboard API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared state
agent_instance = None
llm_engine = LLMEngine()
config = {
    "workspace": "workspace",
    "log_file": "logs/actions.log",
    "adapter": "file",
    "llm_config": "config/llm_config.json"
}

class ActionRequest(BaseModel):
    type: str
    params: Dict[str, Any] = {}

class LLMConfigRequest(BaseModel):
    provider: str
    api_key: str
    model: str

class ChatRequest(BaseModel):
    prompt: str

@app.on_event("startup")
async def startup_event():
    global agent_instance
    if not os.path.exists("workspace"):
        os.makedirs("workspace")
    if not os.path.exists("config"):
        os.makedirs("config")
    
    # Load persistence LLM config if exists
    if os.path.exists(config["llm_config"]):
        with open(config["llm_config"], "r") as f:
            saved_config = json.load(f)
            llm_engine.configure(
                saved_config.get("provider", "mock"),
                saved_config.get("api_key", ""),
                saved_config.get("model", "")
            )

    agent_instance = Agent(config)
    import threading
    threading.Thread(target=agent_instance.start, daemon=True).start()

@app.get("/status")
async def get_status():
    return {"status": "ready" if agent_instance and agent_instance._running else "initializing"}

@app.post("/config")
async def save_config(req: LLMConfigRequest):
    llm_engine.configure(req.provider, req.api_key, req.model)
    with open(config["llm_config"], "w") as f:
        json.dump(req.dict(), f)
    return {"status": "configured"}

@app.post("/chat")
async def chat(req: ChatRequest):
    if not agent_instance or not agent_instance._running:
        raise HTTPException(status_code=503, detail="Agent not running")
    
    # 1. Ask LLM for actions
    log.info(f"Processing chat prompt: {req.prompt}")
    result = await llm_engine.generate_actions(req.prompt)
    
    if "error" in result:
        return {"status": "error", "message": result["error"]}

    # 2. Queue actions
    for action in result.get("actions", []):
        agent_instance._action_queue.put(action)
    
    return {
        "status": "queued", 
        "intent": result.get("intent", "Executed"),
        "actions_count": len(result.get("actions", []))
    }

@app.post("/action")
async def execute_action(action: ActionRequest):
    if not agent_instance or not agent_instance._running:
        raise HTTPException(status_code=503, detail="Agent not running")
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
