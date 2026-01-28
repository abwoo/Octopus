import logging
import pyperclip
from typing import Dict, Any

log = logging.getLogger("octopus.skill.clipboard")

def execute(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Manage system clipboard.
    Actions: read, write, clear
    """
    action = params.get("action", "read").lower()
    
    if action == "write":
        text = params.get("text", "")
        pyperclip.copy(text)
        return {"status": "ok", "message": "Text copied to clipboard"}
    
    elif action == "read":
        text = pyperclip.paste()
        return {"status": "ok", "content": text, "message": "Clipboard read successfully"}
    
    elif action == "clear":
        pyperclip.copy("")
        return {"status": "ok", "message": "Clipboard cleared"}

    return {"status": "error", "message": f"Unknown action: {action}"}
