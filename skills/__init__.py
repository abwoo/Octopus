"""
Octopus Skills Package
======================
Contains skill modules that wrap HumanExecutor primitives.

Author: Octopus Contributors
License: MIT
"""

from skills.mouse import MouseSkill
from skills.keyboard import KeyboardSkill
from skills.file import FileSkill
from skills.system import SystemSkill

__all__ = ["MouseSkill", "KeyboardSkill", "FileSkill", "SystemSkill"]
