"""
Octopus Model Adapter
=====================
Defines the interface for receiving actions from external sources.
Includes MockAdapter for testing and FileAdapter for file-based input.

Author: Octopus Contributors
License: MIT
"""

import os
import time
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

log = logging.getLogger("octopus.adapter")


class ModelAdapter(ABC):
    """
    Abstract base class for action providers.
    
    Subclasses implement get_actions() to fetch action batches
    from various sources (mock data, files, APIs, etc.).
    """

    @abstractmethod
    def get_actions(self) -> Optional[Dict[str, Any]]:
        """
        Fetch next action batch.
        
        Returns:
            Dictionary with 'actions' list, or None if no actions available
        """
        pass


class MockAdapter(ModelAdapter):
    """
    Returns predefined test actions for verification.
    
    Executes a brief test sequence then idles.
    Used for testing the complete execution pipeline.
    """

    def __init__(self):
        self._step = 0

    def get_actions(self) -> Optional[Dict[str, Any]]:
        time.sleep(0.5)  # Simulate fetch latency
        self._step += 1

        if self._step == 1:
            return {
                "intent": "Test sequence - system check",
                "actions": [
                    {"type": "system.sleep", "params": {"seconds": 0.3}},
                    {
                        "type": "file.write",
                        "params": {
                            "path": "test_output.txt",
                            "content": "Octopus v0.1 verification successful\n",
                        },
                    },
                ],
            }

        if self._step == 2:
            return {
                "intent": "Display info check",
                "actions": [
                    {"type": "system.screen_size", "params": {}},
                ],
            }

        return None  # Idle after test sequence


class FileAdapter(ModelAdapter):
    """
    Watches workspace for instruction files.
    
    Looks for 'instruction.json' in the workspace directory.
    When found, reads and deletes the file (consume pattern).
    """

    def __init__(self, workspace_path: str, trigger_file: str = "instruction.json"):
        self._trigger_path = os.path.join(workspace_path, trigger_file)

    def get_actions(self) -> Optional[Dict[str, Any]]:
        if not os.path.exists(self._trigger_path):
            time.sleep(0.5)
            return None

        try:
            with open(self._trigger_path, "r", encoding="utf-8") as f:
                batch = json.load(f)
            os.remove(self._trigger_path)
            log.info(f"Loaded instruction from {self._trigger_path}")
            return batch
        except json.JSONDecodeError as e:
            log.error(f"Invalid JSON in instruction file: {e}")
            os.remove(self._trigger_path)
            return None
        except Exception as e:
            log.error(f"Error reading instruction: {e}")
            return None


def create_adapter(adapter_name: str, workspace_path: str) -> ModelAdapter:
    """
    Factory function to create adapter by name.
    
    Args:
        adapter_name: 'mock' or 'file'
        workspace_path: Path to workspace directory
        
    Returns:
        Configured ModelAdapter instance
    """
    adapters = {
        "mock": lambda: MockAdapter(),
        "file": lambda: FileAdapter(workspace_path),
    }

    if adapter_name in adapters:
        log.info(f"Created adapter: {adapter_name}")
        return adapters[adapter_name]()

    log.warning(f"Unknown adapter '{adapter_name}', defaulting to mock")
    return MockAdapter()
