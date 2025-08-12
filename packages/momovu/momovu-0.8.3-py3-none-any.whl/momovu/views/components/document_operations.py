"""
Document operation utilities for the Main Window.

This module contains pure functions and utilities for document operations,
extracted from the Main Window to reduce complexity and improve testability.
"""

from pathlib import Path
from typing import Any, Optional

from PySide6.QtCore import QRectF

from momovu.lib.exceptions import DocumentLoadError
from momovu.lib.logger import get_logger

logger = get_logger(__name__)


def validate_pdf_path(file_path: str) -> bool:
    """Check if path exists, is a file, and has .pdf extension.

    Args:
        file_path: Path to validate

    Returns:
        True if valid PDF file path, False otherwise
    """
    if not file_path:
        return False

    path = Path(file_path)
    return path.exists() and path.is_file() and path.suffix.lower() == ".pdf"


def extract_filename_from_path(file_path: str) -> str:
    """Get filename component from full path.

    Args:
        file_path: Full or relative path

    Returns:
        Filename with extension (e.g., 'document.pdf')
    """
    return Path(file_path).name


def format_window_title(base_title: str, filename: Optional[str] = None) -> str:
    """Build window title showing app name and current document.

    Args:
        base_title: Application name (e.g., 'Momovu')
        filename: Current document name to append

    Returns:
        'AppName' or 'AppName - filename.pdf'
    """
    if filename:
        return f"{base_title} - {filename}"
    return base_title


def format_page_label(current_page: int, total_pages: int) -> str:
    """Convert 0-based page index to human-readable label.

    Args:
        current_page: Zero-based page index
        total_pages: Total page count

    Returns:
        'Page: X/Y' format string
    """
    # Convert to 1-based for display
    display_current = current_page + 1
    return f"Page: {display_current}/{total_pages}"


def calculate_page_bounds(page_rect: QRectF, margin: int = 10) -> QRectF:
    """Expand rectangle by adding margin on all sides.

    Args:
        page_rect: Original bounds
        margin: Pixels to add on each side

    Returns:
        Expanded rectangle
    """
    return QRectF(
        page_rect.left() - margin,
        page_rect.top() - margin,
        page_rect.width() + 2 * margin,
        page_rect.height() + 2 * margin,
    )


def should_show_error_dialog(error: Exception) -> bool:
    """Filter out system exits from user-facing error dialogs.

    Args:
        error: Exception to evaluate

    Returns:
        False for KeyboardInterrupt/SystemExit, True otherwise
    """
    # Don't show dialogs for certain types of errors
    return not isinstance(error, (KeyboardInterrupt, SystemExit))


def create_error_message(error: Exception, context: str = "") -> str:
    """Format exception into readable error message for users.

    Args:
        error: Exception to format
        context: Optional location/operation description

    Returns:
        Human-readable error description
    """
    if isinstance(error, DocumentLoadError):
        return f"Document Error: {str(error)}"
    elif context:
        return f"Error in {context}: {str(error)}"
    else:
        return f"An error occurred: {str(error)}"


class DocumentOperationResult:
    """Result of a document operation with success/failure information."""

    def __init__(
        self, success: bool, message: str = "", data: Optional[dict[str, Any]] = None
    ):
        """Initialize the result.

        Args:
            success: Whether the operation succeeded
            message: Optional message about the operation
            data: Optional data returned by the operation
        """
        self.success = success
        self.message = message
        self.data = data or {}

    def __bool__(self) -> bool:
        """Enable 'if result:' syntax to check success."""
        return self.success


def safe_document_operation(
    operation_name: str, operation_func: Any, *args: Any, **kwargs: Any
) -> DocumentOperationResult:
    """Wrap operation with try/catch and structured result.

    Args:
        operation_name: Description for logging
        operation_func: Callable to execute
        *args: Positional arguments for operation
        **kwargs: Keyword arguments for operation

    Returns:
        Result object with success flag and error details
    """
    try:
        logger.debug(f"Starting {operation_name}")
        result = operation_func(*args, **kwargs)
        logger.debug(f"Completed {operation_name} successfully")
        return DocumentOperationResult(
            True, f"{operation_name} completed", {"result": result}
        )
    except DocumentLoadError as e:
        logger.error(f"Document error in {operation_name}: {e}")
        return DocumentOperationResult(False, f"Document error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in {operation_name}: {e}", exc_info=True)
        return DocumentOperationResult(False, f"Unexpected error: {str(e)}")


def calculate_spinbox_range(total_pages: int) -> tuple[int, int]:
    """Determine valid page number bounds for UI spinbox.

    Args:
        total_pages: Document page count

    Returns:
        (min=1, max=total_pages) or (1, 1) if no pages
    """
    if total_pages <= 0:
        return (1, 1)
    return (1, total_pages)


def is_valid_page_number(page_number: int, total_pages: int) -> bool:
    """Verify page number is within document bounds.

    Args:
        page_number: 1-based page number to validate
        total_pages: Document page count

    Returns:
        True if 1 <= page_number <= total_pages
    """
    return 1 <= page_number <= total_pages


def convert_page_number_to_index(page_number: int) -> int:
    """Convert human page number to array index.

    Args:
        page_number: Human-readable page (1, 2, 3...)

    Returns:
        Zero-based index (0, 1, 2...)
    """
    return max(0, page_number - 1)


def convert_page_index_to_number(page_index: int) -> int:
    """Convert array index to human page number.

    Args:
        page_index: Zero-based index (0, 1, 2...)

    Returns:
        Human-readable page (1, 2, 3...)
    """
    return max(1, page_index + 1)
