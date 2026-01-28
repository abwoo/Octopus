"""
Octopus System Skill
====================
Provides system control operations via HumanExecutor primitives.
No logic - only passes through to executor methods.

Author: Octopus Contributors
License: MIT
"""

import sys
import platform


class SystemSkill:
    """
    System control skill.
    
    Wraps HumanExecutor system primitives with a clean interface.
    Provides sleep, exit, and display information operations.
    """

    def __init__(self, executor):
        """
        Initialize skill with executor.
        
        Args:
            executor: HumanExecutor instance
        """
        self._executor = executor

    def sleep(self, seconds: float):
        """
        Pause execution.
        
        Args:
            seconds: Sleep duration
        """
        return self._executor.system_sleep(seconds)

    def exit(self):
        """Signal agent to terminate."""
        return self._executor.system_exit()

    def screen_size(self):
        """Get current display dimensions."""
        info = self._executor.get_display_info()
        return {
            "status": "ok",
            "message": f"Display: {info['width']}x{info['height']}",
            "width": info["width"],
            "height": info["height"],
        }
    
    def info(self):
        """Get system platform information."""
        return {
            "status": "ok",
            "platform": platform.platform(),
            "python": sys.version.split(" ")[0],
            "os": platform.system()
        }
