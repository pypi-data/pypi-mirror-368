"""
Module: tunacode.tools.update_file

File update tool for agent operations in the TunaCode application.
Provides targeted file content modification with diff-based updates.
"""

import os

from pydantic_ai.exceptions import ModelRetry

from tunacode.exceptions import ToolExecutionError
from tunacode.tools.base import FileBasedTool
from tunacode.types import ToolResult


class UpdateFileTool(FileBasedTool):
    """Tool for updating existing files by replacing text blocks."""

    @property
    def tool_name(self) -> str:
        return "Update"

    async def _execute(self, filepath: str, target: str, patch: str) -> ToolResult:
        """Update an existing file by replacing a target text block with a patch.

        Args:
            filepath: The path to the file to update.
            target: The entire, exact block of text to be replaced.
            patch: The new block of text to insert.

        Returns:
            ToolResult: A message indicating success.

        Raises:
            ModelRetry: If file not found or target not found
            Exception: Any file operation errors
        """
        if not os.path.exists(filepath):
            raise ModelRetry(
                f"File '{filepath}' not found. Cannot update. "
                "Verify the filepath or use `write_file` if it's a new file."
            )

        with open(filepath, "r", encoding="utf-8") as f:
            original = f.read()

        if target not in original:
            # Provide context to help the LLM find the target
            context_lines = 10
            lines = original.splitlines()
            snippet = "\n".join(lines[:context_lines])
            # Use ModelRetry to guide the LLM
            raise ModelRetry(
                f"Target block not found in '{filepath}'. "
                "Ensure the `target` argument exactly matches the content you want to replace. "
                f"File starts with:\n---\n{snippet}\n---"
            )

        new_content = original.replace(target, patch, 1)  # Replace only the first occurrence

        if original == new_content:
            # This could happen if target and patch are identical
            raise ModelRetry(
                f"Update target found, but replacement resulted in no changes to '{filepath}'. "
                "Was the `target` identical to the `patch`? Please check the file content."
            )

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)

        return f"File '{filepath}' updated successfully."

    def _format_args(self, filepath: str, target: str = None, patch: str = None) -> str:
        """Format arguments, truncating target and patch for display."""
        args = [repr(filepath)]

        if target is not None:
            if len(target) > 50:
                args.append(f"target='{target[:47]}...'")
            else:
                args.append(f"target={repr(target)}")

        if patch is not None:
            if len(patch) > 50:
                args.append(f"patch='{patch[:47]}...'")
            else:
                args.append(f"patch={repr(patch)}")

        return ", ".join(args)


# Create the function that maintains the existing interface
async def update_file(filepath: str, target: str, patch: str) -> str:
    """
    Update an existing file by replacing a target text block with a patch.
    Requires confirmation with diff before applying.

    Args:
        filepath: The path to the file to update.
        target: The entire, exact block of text to be replaced.
        patch: The new block of text to insert.

    Returns:
        str: A message indicating the success or failure of the operation.
    """
    tool = UpdateFileTool(None)  # No UI for pydantic-ai compatibility
    try:
        return await tool.execute(filepath, target, patch)
    except ToolExecutionError as e:
        # Return error message for pydantic-ai compatibility
        return str(e)
