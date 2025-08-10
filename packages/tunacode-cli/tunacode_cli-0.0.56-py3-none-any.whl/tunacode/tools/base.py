"""Base tool class for all TunaCode tools.

This module provides a base class that implements common patterns
for all tools including error handling, UI logging, and ModelRetry support.
"""

from abc import ABC, abstractmethod

from pydantic_ai.exceptions import ModelRetry

from tunacode.core.logging.logger import get_logger
from tunacode.exceptions import FileOperationError, ToolExecutionError
from tunacode.types import FilePath, ToolName, ToolResult, UILogger


class BaseTool(ABC):
    """Base class for all TunaCode tools providing common functionality."""

    def __init__(self, ui_logger: UILogger | None = None):
        """Initialize the base tool.

        Args:
            ui_logger: UI logger instance for displaying messages
        """
        self.ui = ui_logger
        self.logger = get_logger(self.__class__.__name__)

    async def execute(self, *args, **kwargs) -> ToolResult:
        """Execute the tool with error handling and logging.

        This method wraps the tool-specific logic with:
        - UI logging of the operation
        - Exception handling (except ModelRetry and ToolExecutionError)
        - Consistent error message formatting

        Returns:
            str: Success message

        Raises:
            ModelRetry: Re-raised to guide the LLM
            ToolExecutionError: Raised for all other errors with structured information
        """
        try:
            msg = f"{self.tool_name}({self._format_args(*args, **kwargs)})"
            if self.ui:
                await self.ui.info(msg)
            self.logger.info(msg)
            result = await self._execute(*args, **kwargs)
            return result
        except ModelRetry as e:
            # Log as warning and re-raise for pydantic-ai
            if self.ui:
                await self.ui.warning(str(e))
            self.logger.warning(f"ModelRetry: {e}")
            raise
        except ToolExecutionError:
            # Already properly formatted, just re-raise
            raise
        except Exception as e:
            # Handle any other exceptions
            await self._handle_error(e, *args, **kwargs)

    @property
    @abstractmethod
    def tool_name(self) -> ToolName:
        """Return the display name for this tool."""
        pass

    @abstractmethod
    async def _execute(self, *args, **kwargs) -> ToolResult:
        """Implement tool-specific logic here.

        This method should contain the core functionality of the tool.

        Returns:
            str: Success message describing what was done

        Raises:
            ModelRetry: When the LLM needs guidance
            Exception: Any other errors will be caught and handled
        """
        pass

    async def _handle_error(self, error: Exception, *args, **kwargs) -> ToolResult:
        """Handle errors by logging and raising proper exceptions.

        Args:
            error: The exception that was raised
            *args, **kwargs: Original arguments for context

        Raises:
            ToolExecutionError: Always raised with structured error information
        """
        # Format error message for display
        err_msg = f"Error {self._get_error_context(*args, **kwargs)}: {error}"
        if self.ui:
            await self.ui.error(err_msg)
        self.logger.error(err_msg)

        # Raise proper exception instead of returning string
        raise ToolExecutionError(tool_name=self.tool_name, message=str(error), original_error=error)

    def _format_args(self, *args, **kwargs) -> str:
        """Format arguments for display in UI logging.

        Override this method to customize how arguments are displayed.

        Returns:
            str: Formatted argument string
        """
        # Collect all arguments
        all_args = []

        # Add positional arguments
        for arg in args:
            if isinstance(arg, str) and len(arg) > 50:
                # Truncate long strings
                all_args.append(f"'{arg[:47]}...'")
            else:
                all_args.append(repr(arg))

        # Add keyword arguments
        for key, value in kwargs.items():
            if isinstance(value, str) and len(value) > 50:
                all_args.append(f"{key}='{value[:47]}...'")
            else:
                all_args.append(f"{key}={repr(value)}")

        return ", ".join(all_args)

    def _get_error_context(self, *args, **kwargs) -> str:
        """Get context string for error messages.

        Override this method to provide tool-specific error context.

        Returns:
            str: Context for the error message
        """
        return f"in {self.tool_name}"


class FileBasedTool(BaseTool):
    """Base class for tools that work with files.

    Provides common file-related functionality like:
    - Path validation
    - File existence checking
    - Directory creation
    - Encoding handling
    - Enhanced error handling for file operations
    """

    def _format_args(self, filepath: FilePath, *args, **kwargs) -> str:
        """Format arguments with filepath as first argument."""
        # Always show the filepath first
        all_args = [repr(filepath)]

        # Add remaining positional arguments
        for arg in args:
            if isinstance(arg, str) and len(arg) > 50:
                all_args.append(f"'{arg[:47]}...'")
            else:
                all_args.append(repr(arg))

        # Add keyword arguments
        for key, value in kwargs.items():
            if isinstance(value, str) and len(value) > 50:
                all_args.append(f"{key}='{value[:47]}...'")
            else:
                all_args.append(f"{key}={repr(value)}")

        return ", ".join(all_args)

    def _get_error_context(self, filepath: FilePath = None, *args, **kwargs) -> str:
        """Get error context including file path."""
        if filepath:
            return f"handling file '{filepath}'"
        return super()._get_error_context(*args, **kwargs)

    async def _handle_error(self, error: Exception, *args, **kwargs) -> ToolResult:
        """Handle file-specific errors.

        Overrides base class to create FileOperationError for file-related issues.

        Raises:
            ToolExecutionError: Always raised with structured error information
        """
        filepath = args[0] if args else kwargs.get("filepath", "unknown")

        # Check if this is a file-related error
        if isinstance(error, (IOError, OSError, PermissionError, FileNotFoundError)):
            # Determine the operation based on the tool name
            operation = self.tool_name.replace("_", " ")

            # Create a FileOperationError
            file_error = FileOperationError(
                operation=operation, path=str(filepath), message=str(error), original_error=error
            )

            # Format error message for display
            err_msg = str(file_error)
            if self.ui:
                await self.ui.error(err_msg)

            # Raise ToolExecutionError with the file error
            raise ToolExecutionError(
                tool_name=self.tool_name, message=str(file_error), original_error=file_error
            )

        # For non-file errors, use the base class handling
        await super()._handle_error(error, *args, **kwargs)
