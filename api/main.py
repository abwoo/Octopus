import subprocess
import json
import sys
import os
import queue
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

# Standard Octopus imports
from core.agent import Agent
from api.llm_engine import LLMEngine

# Setup FastAPI
app = FastAPI(title="Octopus Dashboard API")

# Enable CORS
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
    "llm_config": "config/llm_config.json"
}

class ActionRequest(BaseModel):
    type: str
    params: Dict[str, Any] = {}

class LLMConfigRequest(BaseModel):
    provider: str
    api_key: str
    model: str
    base_url: Optional[str] = None

class ChatRequest(BaseModel):
    prompt: str

@app.on_event("startup")
async def startup_event():
    global agent_instance
    if not os.path.exists("workspace"): os.makedirs("workspace")
    if not os.path.exists("config"): os.makedirs("config")
    
    if os.path.exists(config["llm_config"]):
        with open(config["llm_config"], "r") as f:
            c = json.load(f)
            llm_engine.configure(c["provider"], c["api_key"], c["model"], c.get("base_url"))

    # Only start agent if needed for background adapters, 
    # but for unified logic we'll mostly use the CLI subprocess.
    agent_instance = Agent(config)
    import threading
    threading.Thread(target=agent_instance.start, daemon=True).start()

def run_cli_action(action_data: Dict[str, Any]):
    """Execute action through the exact same logic path as agent.ps1 / cli main.py"""
    cli_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cli", "main.py")
    json_str = json.dumps(action_data)
    
    # Run as a separate process to guarantee same environment and logic chain
    try:
        result = subprocess.run(
            [sys.executable, cli_path, "run", json_str],
            capture_output=True,
            text=True,
            check=True
        )
        return {"status": "ok", "output": result.stdout}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": e.stderr or str(e)}

@app.post("/config")
async def save_config(req: LLMConfigRequest):
    llm_engine.configure(req.provider, req.api_key, req.model, req.base_url)
    with open(config["llm_config"], "w") as f:
        json.dump(req.dict(), f)
    return {"status": "configured"}

@app.post("/chat")
async def chat(req: ChatRequest):
    result = await llm_engine.generate_actions(req.prompt)
    if "error" in result:
        return {"status": "error", "message": result["error"]}

    # Execute the generated actions sequence through the CLI path
    outputs = []
    for action in result.get("actions", []):
        res = run_cli_action(action)
        outputs.append(res)
    
    return {
        "status": "completed", 
        "intent": result.get("intent", "Executed"),
        "results": outputs
    }

@app.post("/action")
async def execute_action(action: ActionRequest):
    res = run_cli_action(action.dict())
    if res["status"] == "error":
        raise HTTPException(status_code=500, detail=res["message"])
    return res

@app.get("/logs")
async def get_logs(limit: int = 50):
    log_file = config["log_file"]
    if not os.path.exists(log_file): return {"logs": []}
    with open(log_file, "r", encoding="utf-8") as f:
        return {"logs": f.readlines()[-limit:]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
