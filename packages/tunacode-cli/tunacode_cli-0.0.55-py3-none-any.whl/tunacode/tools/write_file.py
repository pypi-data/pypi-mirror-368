"""
Module: tunacode.tools.write_file

File writing tool for agent operations in the TunaCode application.
Provides safe file creation with conflict detection and encoding handling.
"""

import os

from pydantic_ai.exceptions import ModelRetry

from tunacode.exceptions import ToolExecutionError
from tunacode.tools.base import FileBasedTool
from tunacode.types import ToolResult


class WriteFileTool(FileBasedTool):
    """Tool for writing content to new files."""

    @property
    def tool_name(self) -> str:
        return "Write"

    async def _execute(self, filepath: str, content: str) -> ToolResult:
        """Write content to a new file. Fails if the file already exists.

        Args:
            filepath: The path to the file to write to.
            content: The content to write to the file.

        Returns:
            ToolResult: A message indicating success.

        Raises:
            ModelRetry: If the file already exists
            Exception: Any file writing errors
        """
        # Prevent overwriting existing files with this tool.
        if os.path.exists(filepath):
            # Use ModelRetry to guide the LLM
            raise ModelRetry(
                f"File '{filepath}' already exists. "
                "Use the `update_file` tool to modify it, or choose a different filepath."
            )

        # Create directories if they don't exist
        dirpath = os.path.dirname(filepath)
        if dirpath and not os.path.exists(dirpath):
            os.makedirs(dirpath, exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as file:
            file.write(content)

        return f"Successfully wrote to new file: {filepath}"

    def _format_args(self, filepath: str, content: str = None) -> str:
        """Format arguments, truncating content for display."""
        if content is not None and len(content) > 50:
            return f"{repr(filepath)}, content='{content[:47]}...'"
        return super()._format_args(filepath, content)


# Create the function that maintains the existing interface
async def write_file(filepath: str, content: str) -> str:
    """
    Write content to a new file. Fails if the file already exists.
    Requires confirmation before writing.

    Args:
        filepath: The path to the file to write to.
        content: The content to write to the file.

    Returns:
        A message indicating the success or failure of the operation.
    """
    tool = WriteFileTool(None)  # No UI for pydantic-ai compatibility
    try:
        return await tool.execute(filepath, content)
    except ToolExecutionError as e:
        # Return error message for pydantic-ai compatibility
        return str(e)
