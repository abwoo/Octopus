"""
Octopus Human Executor
======================
Provides low-level I/O primitives for simulating human-like interactions.
All operations are validated against safety boundaries before execution.

This module is the foundation layer - Skills call these primitives,
they never access pyautogui/pynput directly.

Author: Octopus Contributors
License: MIT
"""

import os
import time
import logging
import pyautogui
from typing import Dict, Any

# Safety configuration
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

log = logging.getLogger("octopus.executor")


class HumanExecutor:
    """
    Atomic I/O operations for keyboard, mouse, and file access.
    
    All coordinate-based operations validate against display bounds.
    All path-based operations are restricted to the workspace directory.
    
    Attributes:
        workspace_path: Root directory for sandboxed file operations
        screen_width: Current display width in pixels
        screen_height: Current display height in pixels
        min_interval: Minimum delay between operations (seconds)
    """

    # Class constants
    MIN_INTERVAL_SEC = 0.3
    
    def __init__(self, workspace_root: str):
        """
        Initialize executor with workspace sandbox.
        
        Args:
            workspace_root: Directory path for sandboxed file operations
        """
        self.workspace_path = os.path.abspath(workspace_root)
        self.screen_width, self.screen_height = pyautogui.size()
        self.min_interval = self.MIN_INTERVAL_SEC

        if not os.path.exists(self.workspace_path):
            os.makedirs(self.workspace_path, exist_ok=True)

    # ─────────────────────────────────────────────────────────────────────────
    # Safety Validation
    # ─────────────────────────────────────────────────────────────────────────

    def _check_coordinates(self, x: int, y: int) -> bool:
        """
        Validate coordinates are within display bounds.
        
        Args:
            x: Horizontal position (0-indexed from left)
            y: Vertical position (0-indexed from top)
            
        Raises:
            ValueError: If coordinates are out of bounds
        """
        if not (0 <= x < self.screen_width and 0 <= y < self.screen_height):
            raise ValueError(
                f"Coordinates ({x}, {y}) out of bounds. "
                f"Display: {self.screen_width}x{self.screen_height}"
            )
        return True

    def _check_path(self, path: str) -> str:
        """
        Validate and resolve path within workspace sandbox.
        
        Args:
            path: Relative or absolute path to validate
            
        Returns:
            Absolute path within workspace
            
        Raises:
            PermissionError: If path escapes workspace boundary
        """
        abs_path = os.path.abspath(os.path.join(self.workspace_path, path))
        if not abs_path.startswith(self.workspace_path):
            raise PermissionError(
                f"Access denied: '{path}' is outside workspace boundary"
            )
        return abs_path

    def _enforce_interval(self) -> None:
        """Pause to enforce minimum operation interval."""
        time.sleep(self.min_interval)

    def get_display_info(self) -> Dict[str, int]:
        """
        Get current display dimensions.
        
        Returns:
            Dictionary with 'width' and 'height' keys
        """
        return {"width": self.screen_width, "height": self.screen_height}

    # ─────────────────────────────────────────────────────────────────────────
    # Mouse Primitives
    # ─────────────────────────────────────────────────────────────────────────

    # ─────────────────────────────────────────────────────────────────────────
    # Mouse Primitives
    # ─────────────────────────────────────────────────────────────────────────

    def mouse_move(self, x: int, y: int, duration: float = 0.15) -> Dict[str, Any]:
        """
        Move mouse cursor to absolute screen position.
        
        Args:
            x: Target horizontal position
            y: Target vertical position
            duration: Movement duration in seconds
            
        Returns:
            Result dict with 'status' and 'message'
        """
        try:
            self._check_coordinates(x, y)
            pyautogui.moveTo(x, y, duration=duration)
            return {"status": "ok", "message": f"Moved to ({x}, {y})"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def mouse_drag(self, x: int, y: int, duration: float = 0.5, button: str = "left") -> Dict[str, Any]:
        """
        Drag mouse to target position holding button.
        
        Args:
            x: Target horizontal position
            y: Target vertical position
            duration: Drag duration in seconds
            button: Button to hold ('left', 'right', 'middle')
            
        Returns:
            Result dict with 'status' and 'message'
        """
        try:
            self._check_coordinates(x, y)
            pyautogui.dragTo(x, y, duration=duration, button=button)
            return {"status": "ok", "message": f"Dragged to ({x}, {y}) with {button}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def mouse_click(self, x: int, y: int, button: str = "left", clicks: int = 1, interval: float = 0.1) -> Dict[str, Any]:
        """
        Click at specified screen position.
        
        Args:
            x: Click horizontal position
            y: Click vertical position
            button: Mouse button - 'left', 'right', 'middle'
            clicks: Number of clicks
            interval: Interval between clicks
            
        Returns:
            Result dict with 'status' and 'message'
        """
        try:
            self._check_coordinates(x, y)
            valid_buttons = {"left", "right", "middle"}
            if button not in valid_buttons:
                return {"status": "error", "message": f"Invalid button: {button}"}
            pyautogui.click(x, y, button=button, clicks=clicks, interval=interval)
            self._enforce_interval()
            return {"status": "ok", "message": f"Clicked {button} ({clicks}x) at ({x}, {y})"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def mouse_scroll(self, clicks: int) -> Dict[str, Any]:
        """
        Scroll mouse wheel.
        
        Args:
            clicks: Scroll amount (positive=up, negative=down)
            
        Returns:
            Result dict with 'status' and 'message'
        """
        try:
            pyautogui.scroll(clicks)
            self._enforce_interval()
            return {"status": "ok", "message": f"Scrolled {clicks} clicks"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def mouse_position(self) -> Dict[str, Any]:
        """
        Get current mouse cursor position.
        
        Returns:
            Result dict with 'x', 'y' coordinates
        """
        try:
            x, y = pyautogui.position()
            return {"status": "ok", "x": x, "y": y, "message": f"Position: ({x}, {y})"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ─────────────────────────────────────────────────────────────────────────
    # Keyboard Primitives
    # ─────────────────────────────────────────────────────────────────────────

    def keyboard_type(self, text: str, interval: float = 0.02) -> Dict[str, Any]:
        """
        Type text string character by character.
        
        Args:
            text: String to type
            interval: Delay between keystrokes (seconds)
            
        Returns:
            Result dict with 'status' and 'message'
        """
        try:
            pyautogui.write(text, interval=interval)
            self._enforce_interval()
            return {"status": "ok", "message": f"Typed {len(text)} characters"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def keyboard_press(self, key: str) -> Dict[str, Any]:
        """
        Press and release a single key.
        
        Args:
            key: Key name (e.g., 'enter', 'tab', 'a')
            
        Returns:
            Result dict with 'status' and 'message'
        """
        try:
            pyautogui.press(key)
            self._enforce_interval()
            return {"status": "ok", "message": f"Pressed '{key}'"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def keyboard_hotkey(self, *keys) -> Dict[str, Any]:
        """
        Execute key combination.
        
        Args:
            *keys: Keys to press simultaneously (e.g., 'ctrl', 'c')
            
        Returns:
            Result dict with 'status' and 'message'
        """
        try:
            pyautogui.hotkey(*keys)
            self._enforce_interval()
            return {"status": "ok", "message": f"Hotkey: {'+'.join(keys)}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ─────────────────────────────────────────────────────────────────────────
    # File Primitives (Sandboxed)
    # ─────────────────────────────────────────────────────────────────────────

    def file_read(self, path: str) -> Dict[str, Any]:
        """
        Read file contents from workspace.
        
        Args:
            path: Relative path within workspace
            
        Returns:
            Result dict with 'status', 'message', and 'content'
        """
        try:
            safe_path = self._check_path(path)
            if not os.path.exists(safe_path):
                return {"status": "error", "message": "File does not exist"}
            with open(safe_path, "r", encoding="utf-8") as f:
                content = f.read()
            return {"status": "ok", "message": "Read complete", "content": content}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def file_write(self, path: str, content: str, append: bool = False) -> Dict[str, Any]:
        """
        Write content to file in workspace.
        
        Args:
            path: Relative path within workspace
            content: String content to write
            append: If True, append to existing file
            
        Returns:
            Result dict with 'status' and 'message'
        """
        try:
            safe_path = self._check_path(path)
            parent = os.path.dirname(safe_path)
            if parent and not os.path.exists(parent):
                os.makedirs(parent, exist_ok=True)
            mode = "a" if append else "w"
            with open(safe_path, mode, encoding="utf-8") as f:
                f.write(content)
            return {"status": "ok", "message": f"Written to {path}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def file_list(self, path: str = ".") -> Dict[str, Any]:
        """
        List files in workspace directory.
        
        Args:
            path: Relative path within workspace
            
        Returns:
            Result dict with 'files' list
        """
        try:
            safe_path = self._check_path(path)
            if not os.path.exists(safe_path):
                return {"status": "error", "message": "Directory does not exist"}
            
            items = []
            for item in os.listdir(safe_path):
                full_path = os.path.join(safe_path, item)
                items.append({
                    "name": item,
                    "type": "dir" if os.path.isdir(full_path) else "file",
                    "size": os.path.getsize(full_path) if os.path.isfile(full_path) else 0
                })
            return {"status": "ok", "files": items}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def file_delete(self, path: str) -> Dict[str, Any]:
        """
        Delete file in workspace.
        
        Args:
            path: Relative path within workspace
            
        Returns:
            Result dict with status
        """
        try:
            safe_path = self._check_path(path)
            if not os.path.exists(safe_path):
                return {"status": "error", "message": "File does not exist"}
            
            if os.path.isdir(safe_path):
                 os.rmdir(safe_path)
            else:
                os.remove(safe_path)
            return {"status": "ok", "message": f"Deleted {path}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def file_exists(self, path: str) -> Dict[str, Any]:
        """
        Check if file exists in workspace.
        
        Args:
            path: Relative path
            
        Returns:
            Result dict with 'exists' boolean
        """
        try:
            safe_path = self._check_path(path)
            return {"status": "ok", "exists": os.path.exists(safe_path)}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ─────────────────────────────────────────────────────────────────────────
    # System Primitives
    # ─────────────────────────────────────────────────────────────────────────

    def system_sleep(self, seconds: float) -> Dict[str, Any]:
        """
        Pause execution for specified duration.
        
        Args:
            seconds: Sleep duration
            
        Returns:
            Result dict with 'status' and 'message'
        """
        try:
            time.sleep(float(seconds))
            return {"status": "ok", "message": f"Slept {seconds}s"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def system_exit(self) -> Dict[str, Any]:
        """
        Signal agent to terminate.
        
        Returns:
            Result dict with exit signal
        """
        return {"status": "ok", "message": "EXIT_SIGNAL"}
