import logging
import psutil
from typing import Dict, Any

log = logging.getLogger("octopus.skill.hardware")

def execute(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Monitor system hardware resources.
    Actions: usage, specs
    """
    action = params.get("action", "usage").lower()
    
    if action == "usage":
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        return {
            "status": "ok",
            "cpu_percent": cpu,
            "ram_percent": ram,
            "disk_percent": disk,
            "message": f"CPU: {cpu}%, RAM: {ram}%, Disk: {disk}%"
        }
    
    elif action == "specs":
        import platform
        return {
            "status": "ok",
            "processor": platform.processor(),
            "architecture": platform.architecture()[0],
            "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "os": platform.system() + " " + platform.release()
        }

    return {"status": "error", "message": f"Unknown action: {action}"}
