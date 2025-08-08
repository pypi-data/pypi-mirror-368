"""
Tool handling business logic, separated from UI concerns.
"""

from typing import Optional

from tunacode.constants import READ_ONLY_TOOLS
from tunacode.core.state import StateManager
from tunacode.templates.loader import Template
from tunacode.types import (
    ToolArgs,
    ToolConfirmationRequest,
    ToolConfirmationResponse,
    ToolName,
)


class ToolHandler:
    """Handles tool confirmation logic separate from UI."""

    def __init__(self, state_manager: StateManager):
        self.state = state_manager
        self.active_template: Optional[Template] = None

    def set_active_template(self, template: Optional[Template]) -> None:
        """
        Set the currently active template.

        Args:
            template: The template to activate, or None to clear the active template.
        """
        self.active_template = template

    def should_confirm(self, tool_name: ToolName) -> bool:
        """
        Determine if a tool requires confirmation.

        Args:
            tool_name: Name of the tool to check.

        Returns:
            bool: True if confirmation is required, False otherwise.
        """
        # Skip confirmation for read-only tools
        if is_read_only_tool(tool_name):
            return False

        # Check if tool is allowed by active template
        if self.active_template and self.active_template.allowed_tools:
            if tool_name in self.active_template.allowed_tools:
                return False

        return not (self.state.session.yolo or tool_name in self.state.session.tool_ignore)

    def process_confirmation(self, response: ToolConfirmationResponse, tool_name: ToolName) -> bool:
        """
        Process the confirmation response.

        Args:
            response: The confirmation response from the user.
            tool_name: Name of the tool being confirmed.

        Returns:
            bool: True if tool should proceed, False if aborted.
        """
        if response.skip_future:
            self.state.session.tool_ignore.append(tool_name)

        return response.approved and not response.abort

    def create_confirmation_request(
        self, tool_name: ToolName, args: ToolArgs
    ) -> ToolConfirmationRequest:
        """
        Create a confirmation request from tool information.

        Args:
            tool_name: Name of the tool.
            args: Tool arguments.

        Returns:
            ToolConfirmationRequest: The confirmation request.
        """
        filepath = args.get("filepath")
        return ToolConfirmationRequest(tool_name=tool_name, args=args, filepath=filepath)


def is_read_only_tool(tool_name: str) -> bool:
    """
    Check if a tool is read-only (safe to execute without confirmation).

    Args:
        tool_name: Name of the tool to check.

    Returns:
        bool: True if the tool is read-only, False otherwise.
    """
    return tool_name in READ_ONLY_TOOLS
