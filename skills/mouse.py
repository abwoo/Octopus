"""
Octopus Mouse Skill
===================
Provides comprehensive mouse operations via HumanExecutor primitives.
No logic - only passes through to executor methods.

Author: Octopus Contributors
License: MIT
"""


class MouseSkill:
    """
    Mouse operations skill.
    
    Wraps HumanExecutor mouse primitives with a clean interface.
    All methods return standardized result dictionaries.
    """

    def __init__(self, executor):
        """
        Initialize skill with executor.
        
        Args:
            executor: HumanExecutor instance
        """
        self._executor = executor

    def move(self, x: int, y: int, duration: float = 0.15):
        """
        Move mouse cursor to absolute position.
        
        Args:
            x: Horizontal position
            y: Vertical position
            duration: Movement duration (default 0.15s)
        """
        return self._executor.mouse_move(x, y, duration)

    def drag(self, x: int, y: int, duration: float = 0.5, button: str = "left"):
        """
        Drag mouse to target position holding button.
        
        Args:
            x: Target horizontal position
            y: Target vertical position
            duration: Drag duration (default 0.5s)
            button: Button to hold ('left', 'right', 'middle')
        """
        return self._executor.mouse_drag(x, y, duration, button)

    def click(self, x: int, y: int, button: str = "left"):
        """
        Click at specified position.
        
        Args:
            x: Horizontal position
            y: Vertical position
            button: 'left', 'right', or 'middle'
        """
        return self._executor.mouse_click(x, y, button)

    def double_click(self, x: int, y: int, button: str = "left"):
        """
        Double-click at specified position.
        
        Args:
            x: Horizontal position
            y: Vertical position
            button: 'left', 'right', or 'middle'
        """
        return self._executor.mouse_click(x, y, button, clicks=2)

    def scroll(self, clicks: int):
        """
        Scroll mouse wheel.
        
        Args:
            clicks: Scroll amount (positive=up, negative=down)
        """
        return self._executor.mouse_scroll(clicks)

    def position(self):
        """
        Get current mouse cursor position.
        
        Returns:
             Dict with x, y coordinates
        """
        return self._executor.mouse_position()
