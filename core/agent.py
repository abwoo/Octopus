"""
Octopus Agent
=============
Main execution loop that fetches actions and dispatches to skills.
Includes emergency stop mechanism (Ctrl+Alt+Q) and action logging.

Author: Octopus Contributors
License: MIT
"""

import os
import sys
import time
import queue
import logging
import threading
from datetime import datetime
from typing import Dict, Any, Optional

from pynput import keyboard

from core.executor.human_executor import HumanExecutor
from core.dispatcher import Dispatcher
from core.model_adapter import create_adapter

log = logging.getLogger("octopus.agent")


class Agent:
    """
    Main agent that processes actions from a ModelAdapter.
    
    Features:
    - Blocking queue for low CPU idle usage
    - Emergency stop via Ctrl+Alt+Q hotkey
    - Action logging to file
    - Configurable adapter (mock/file)
    
    The agent fetches action batches from the adapter in a background
    thread and processes them sequentially in the main loop.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize agent with configuration.
        
        Args:
            config: Dictionary with keys:
                - workspace: Path to workspace directory
                - log_file: Path to action log file
                - adapter: Adapter name ('mock' or 'file')
        """
        self._config = config
        self._workspace = config.get("workspace", "workspace")
        self._log_file = config.get("log_file", "logs/actions.log")

        # Initialize components
        self._executor = HumanExecutor(self._workspace)
        self._dispatcher = Dispatcher(self._executor)
        self._adapter = create_adapter(
            config.get("adapter", "mock"), self._workspace
        )

        # Execution state
        self._action_queue: queue.Queue = queue.Queue()
        self._halt_event = threading.Event()
        self._running = False

        # Setup logging
        self._init_logging()

    def _init_logging(self) -> None:
        """Initialize file-based action logging."""
        log_dir = os.path.dirname(self._log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        file_handler = logging.FileHandler(self._log_file, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(formatter)
        logging.getLogger().addHandler(file_handler)

    def _log_action(self, action: Dict, result: Dict) -> None:
        """Record action execution to log."""
        action_type = action.get("type", "unknown")
        params = action.get("params", {})
        status = result.get("status", "unknown")
        message = result.get("message", "")
        log.info(f"ACTION: {action_type} | params={params} | {status}: {message}")

    def _on_emergency_halt(self) -> None:
        """Handle emergency stop hotkey."""
        log.warning("EMERGENCY HALT triggered via Ctrl+Alt+Q")
        self._halt_event.set()
        self._running = False

    def _start_halt_listener(self) -> None:
        """Start global hotkey listener for Ctrl+Alt+Q."""
        hotkey = keyboard.GlobalHotKeys({
            "<ctrl>+<alt>+q": self._on_emergency_halt
        })
        hotkey.start()
        log.info("Emergency halt listener active (Ctrl+Alt+Q)")

    def _adapter_loop(self) -> None:
        """Background thread: fetch actions from adapter."""
        while self._running and not self._halt_event.is_set():
            try:
                batch = self._adapter.get_actions()
                if batch and "actions" in batch:
                    intent = batch.get("intent", "No intent")
                    log.info(f"Received batch: {intent}")
                    for action in batch["actions"]:
                        self._action_queue.put(action)
            except Exception as e:
                if self._running:
                    log.error(f"Adapter error: {e}")
                time.sleep(0.5)

    def start(self) -> None:
        """Start the agent execution loop."""
        log.info("=" * 50)
        log.info("Octopus Agent starting")
        log.info(f"Workspace: {self._workspace}")
        log.info(f"Adapter: {self._config.get('adapter', 'mock')}")
        log.info("=" * 50)

        self._running = True
        self._halt_event.clear()

        # Start halt listener
        self._start_halt_listener()

        # Start adapter thread
        adapter_thread = threading.Thread(
            target=self._adapter_loop,
            daemon=True,
            name="adapter"
        )
        adapter_thread.start()

        try:
            self._main_loop()
        finally:
            self._running = False
            log.info("Octopus Agent stopped")

    def _main_loop(self) -> None:
        """
        Main execution loop using blocking queue.
        
        CPU usage is near zero when idle due to blocking get().
        """
        while self._running and not self._halt_event.is_set():
            try:
                # Block until action available (timeout allows halt check)
                try:
                    action = self._action_queue.get(timeout=0.5)
                except queue.Empty:
                    continue

                action_type = action.get("type", "")
                log.info(f"Executing: {action_type}")

                # Dispatch to skill
                result = self._dispatcher.dispatch(action)
                self._log_action(action, result)

                # Check for exit signal
                if result.get("message") == "EXIT_SIGNAL":
                    log.info("Exit signal received")
                    self._running = False
                    break

                self._action_queue.task_done()

            except KeyboardInterrupt:
                log.info("Keyboard interrupt received")
                self._running = False
                break
            except Exception as e:
                log.error(f"Loop error: {e}")
