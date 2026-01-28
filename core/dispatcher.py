"""
Octopus Action Dispatcher
=========================
Routes incoming JSON actions to appropriate Skill handlers.
Validates action structure and parameters before dispatch.

Author: Octopus Contributors
License: MIT
"""

import logging
from typing import Dict, Any

from skills.mouse import MouseSkill
from skills.keyboard import KeyboardSkill
from skills.file import FileSkill
from skills.system import SystemSkill

log = logging.getLogger("octopus.dispatcher")


class Dispatcher:
    """
    Routes structured action requests to Skill handlers.
    
    Actions are expected in format:
        {"type": "skill.method", "params": {...}}
    
    The dispatcher validates the format, locates the skill,
    and invokes the appropriate method with provided parameters.
    """

    def __init__(self, executor):
        """
        Initialize dispatcher with executor instance.
        
        Args:
            executor: HumanExecutor instance for skill operations
        """
        self._skills = {
            "mouse": MouseSkill(executor),
            "keyboard": KeyboardSkill(executor),
            "file": FileSkill(executor),
            "system": SystemSkill(executor),
        }

    def get_available_skills(self) -> list:
        """Return list of registered skill names."""
        return list(self._skills.keys())

    def dispatch(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispatch action to appropriate skill handler.
        
        Args:
            action: Dictionary with 'type' and 'params' keys
            
        Returns:
            Result dictionary with 'status' and 'message'
        """
        # Validate action structure
        if not isinstance(action, dict):
            return {"status": "error", "message": "Action must be a dictionary"}

        action_type = action.get("type", "")
        params = action.get("params", {})

        if not action_type:
            return {"status": "error", "message": "Missing 'type' field"}

        if "." not in action_type:
            return {
                "status": "error",
                "message": f"Invalid format: '{action_type}'. Expected 'skill.method'",
            }

        skill_name, method_name = action_type.split(".", 1)

        # Locate skill
        if skill_name not in self._skills:
            return {
                "status": "error",
                "message": f"Unknown skill: '{skill_name}'. "
                           f"Available: {self.get_available_skills()}",
            }

        skill = self._skills[skill_name]

        # Locate method
        if not hasattr(skill, method_name):
            methods = [m for m in dir(skill) if not m.startswith("_")]
            return {
                "status": "error",
                "message": f"Unknown method: '{method_name}'. "
                           f"Available in {skill_name}: {methods}",
            }

        handler = getattr(skill, method_name)

        # Execute
        try:
            result = handler(**params)
            log.info(f"Dispatched: {action_type} -> {result.get('status')}")
            return result
        except TypeError as e:
            return {"status": "error", "message": f"Parameter error: {e}"}
        except Exception as e:
            return {"status": "error", "message": f"Execution error: {e}"}
