import logging
import psutil
from typing import Dict, Any, List

log = logging.getLogger("octopus.skill.process")

def execute(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Manage system processes.
    Params:
        action: list, kill, start
        name: process name (for kill/start)
        pid: process ID (for kill)
    """
    action = params.get("action", "list").lower()
    
    if action == "list":
        procs = []
        for p in psutil.process_iter(['pid', 'name', 'username']):
            try:
                procs.append(p.info)
            except:
                continue
        # Return top 20 processes to avoid bloat
        return {"status": "ok", "processes": procs[:20], "message": "Processes listed (top 20)"}

    elif action == "kill":
        pid = params.get("pid")
        name = params.get("name")
        killed = 0
        for p in psutil.process_iter(['pid', 'name']):
            if (pid and p.info['pid'] == pid) or (name and name.lower() in p.info['name'].lower()):
                try:
                    p.terminate()
                    killed += 1
                except:
                    continue
        return {"status": "ok", "message": f"Killed {killed} processes"}

    return {"status": "error", "message": f"Unknown action: {action}"}
