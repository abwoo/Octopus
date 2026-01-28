"""
Octopus File Skill
==================
Provides sandboxed file operations via HumanExecutor primitives.
No logic - only passes through to executor methods.

Author: Octopus Contributors
License: MIT
"""


class FileSkill:
    """
    Sandboxed file operations skill.
    
    Wraps HumanExecutor file primitives with a clean interface.
    All paths are validated against workspace boundary.
    """

    def __init__(self, executor):
        """
        Initialize skill with executor.
        
        Args:
            executor: HumanExecutor instance
        """
        self._executor = executor

    def read(self, path: str):
        """
        Read file contents from workspace.
        
        Args:
            path: Relative path within workspace
        """
        return self._executor.file_read(path)

    def write(self, path: str, content: str, append: bool = False):
        """
        Write content to file in workspace.
        
        Args:
            path: Relative path within workspace
            content: String to write
            append: If True, append instead of overwrite
        """
        return self._executor.file_write(path, content, append)

    def append(self, path: str, content: str):
        """
        Append content to file in workspace.
        
        Args:
            path: Relative path within workspace
            content: String to append
        """
        return self._executor.file_write(path, content, append=True)

    def list(self, path: str = "."):
        """
        List files in workspace directory.
        
        Args:
            path: Relative path (default root)
        """
        return self._executor.file_list(path)

    def delete(self, path: str):
        """
        Delete file or directory in workspace.
        
        Args:
            path: Relative path
        """
        return self._executor.file_delete(path)

    def exists(self, path: str):
        """
        Check if file exists in workspace.
        
        Args:
            path: Relative path
        """
        return self._executor.file_exists(path)
