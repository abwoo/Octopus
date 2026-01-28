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

# Use absolute paths rooted at project directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config = {
    "workspace": os.path.join(PROJECT_ROOT, "workspace"),
    "log_file": os.path.join(PROJECT_ROOT, "logs", "actions.log"),
    "llm_config": os.path.join(PROJECT_ROOT, "config", "llm_config.json"),
    "guide_file": os.path.join(PROJECT_ROOT, "docs", "GUIDE.md")
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
    os.makedirs(config["workspace"], exist_ok=True)
    os.makedirs(os.path.dirname(config["llm_config"]), exist_ok=True)
    os.makedirs(os.path.dirname(config["log_file"]), exist_ok=True)
    
    if os.path.exists(config["llm_config"]):
        with open(config["llm_config"], "r") as f:
            c = json.load(f)
            llm_engine.configure(c["provider"], c["api_key"], c["model"], c.get("base_url"))

    agent_instance = Agent(config)
    import threading
    threading.Thread(target=agent_instance.start, daemon=True).start()

def run_cli_action(action_data: Dict[str, Any]):
    """Execute action through the exact same logic path as CLI"""
    cli_path = os.path.join(PROJECT_ROOT, "cli", "main.py")
    json_str = json.dumps(action_data)
    
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

@app.get("/status")
async def get_status():
    return {"status": "ready", "version": "0.2.1"}

@app.get("/guide")
async def get_guide():
    if not os.path.exists(config["guide_file"]):
        return {"content": f"# Guide not found at {config['guide_file']}"}
    with open(config["guide_file"], "r", encoding="utf-8") as f:
        return {"content": f.read()}

@app.post("/config")
async def save_config(req: LLMConfigRequest):
    llm_engine.configure(req.provider, req.api_key, req.model, req.base_url)
    with open(config["llm_config"], "w") as f:
        json.dump(req.dict(), f)
    return {"status": "configured"}

@app.post("/chat")
async def chat(req: ChatRequest):
    # LLM translates prompt to actions
    result = await llm_engine.generate_actions(req.prompt)
    if "error" in result:
        return {"status": "error", "message": result["error"]}

    # Unified execution path
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
    return run_cli_action(action.dict())

@app.post("/terminal")
async def execute_terminal(command: Dict[str, str]):
    """Allow direct PowerShell/CLI command execution for power users"""
    raw_cmd = command.get("cmd", "")
    try:
        # Run raw command in the project context
        result = subprocess.run(
            ["powershell", "-Command", raw_cmd],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )
        return {
            "status": "ok" if result.returncode == 0 else "error",
            "output": result.stdout,
            "error": result.stderr
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/logs")
async def get_logs(limit: int = 50):
    if not os.path.exists(config["log_file"]): return {"logs": []}
    with open(config["log_file"], "r", encoding="utf-8") as f:
        return {"logs": f.readlines()[-limit:]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
