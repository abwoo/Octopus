"""
Octopus Keyboard Skill
======================
Provides keyboard operations via HumanExecutor primitives.
No logic - only passes through to executor methods.

Author: Octopus Contributors
License: MIT
"""


class KeyboardSkill:
    """
    Keyboard operations skill.
    
    Wraps HumanExecutor keyboard primitives with a clean interface.
    All methods return standardized result dictionaries.
    """

    def __init__(self, executor):
        """
        Initialize skill with executor.
        
        Args:
            executor: HumanExecutor instance
        """
        self._executor = executor

    def type(self, text: str, interval: float = 0.02):
        """
        Type text string.
        
        Args:
            text: String to type
            interval: Delay between keystrokes (seconds)
        """
        return self._executor.keyboard_type(text, interval)
    
    def write(self, text: str, interval: float = 0.02):
        """Alias for type."""
        return self.type(text, interval)

    def press(self, key: str):
        """
        Press and release a single key.
        
        Args:
            key: Key name (e.g., 'enter', 'tab', 'esc')
        """
        return self._executor.keyboard_press(key)

    def hotkey(self, *keys):
        """
        Execute key combination.
        
        Args:
            *keys: Keys to press simultaneously (e.g., 'ctrl', 'c')
        """
        return self._executor.keyboard_hotkey(*keys)
