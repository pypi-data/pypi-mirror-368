"""User-friendly error dialog utilities for Momovu.

This module provides centralized error handling with clear user feedback.
It enhances existing error handling without changing program flow.
"""

from typing import Optional

from PySide6.QtWidgets import QApplication, QMessageBox, QWidget

from momovu.lib.logger import get_logger

logger = get_logger(__name__)


def show_pdf_error(
    parent: Optional[QWidget],
    title: str,
    message: str,
    details: Optional[str] = None,
    error_type: str = "error",
) -> None:
    """Show a user-friendly error dialog for PDF-related errors.

    This function displays clear error messages to users while also
    logging the error for debugging. It does not change program flow
    or raise exceptions - it only provides user feedback.

    Args:
        parent: Parent widget for the dialog (can be None)
        title: Dialog title (e.g., "Cannot Open PDF")
        message: Main error message shown to user
        details: Optional detailed error information
        error_type: Type of error for logging ("error", "warning", "info")
    """
    # Log the error first
    log_msg = f"{title}: {message}"
    if details:
        log_msg += f" - Details: {details}"

    if error_type == "warning":
        logger.warning(log_msg)
    elif error_type == "info":
        logger.info(log_msg)
    else:
        logger.error(log_msg)

    # Only show the dialog if we have a QApplication (not in tests)
    # Check this BEFORE creating the QMessageBox to avoid crashes
    if QApplication.instance() is None:
        # No GUI available (probably in test environment)
        return

    try:
        # Create the appropriate message box
        if error_type == "warning":
            msg_box = QMessageBox(
                QMessageBox.Icon.Warning, title, message, parent=parent
            )
        elif error_type == "info":
            msg_box = QMessageBox(
                QMessageBox.Icon.Information, title, message, parent=parent
            )
        else:
            msg_box = QMessageBox(
                QMessageBox.Icon.Critical, title, message, parent=parent
            )

        # Add details if provided
        if details:
            msg_box.setDetailedText(details)

        # Show the dialog
        msg_box.exec()
    except (RuntimeError, AttributeError):
        # Can't show dialog (probably in test environment or no display)
        pass


def show_pdf_load_error(
    parent: Optional[QWidget], file_path: str, reason: Optional[str] = None
) -> None:
    """Show error dialog when PDF fails to load.

    Args:
        parent: Parent widget for the dialog
        file_path: Path to the PDF file
        reason: Optional specific reason for failure
    """
    message = f"Failed to load PDF file:\n{file_path}"

    details = "Possible reasons:\n"
    if reason:
        details += f"• {reason}\n"
    else:
        details += "• The file may be corrupted\n"
        details += "• The file may be password protected\n"
        details += "• The file may not be a valid PDF\n"
        details += "• Insufficient permissions to read the file\n"

    show_pdf_error(
        parent, "Cannot Open PDF", message, details=details, error_type="error"
    )


def show_pdf_corrupted_error(parent: Optional[QWidget], file_path: str) -> None:
    """Show error dialog for corrupted PDF files.

    Args:
        parent: Parent widget for the dialog
        file_path: Path to the corrupted PDF file
    """
    show_pdf_error(
        parent,
        "Corrupted PDF File",
        f"The PDF file appears to be corrupted:\n{file_path}",
        details="The file structure is damaged and cannot be read.\n\n"
        "Try:\n"
        "• Opening the file in another PDF viewer to verify\n"
        "• Re-downloading or re-creating the file\n"
        "• Using a PDF repair tool",
        error_type="error",
    )


def show_pdf_password_error(parent: Optional[QWidget], file_path: str) -> None:
    """Show error dialog for password-protected PDF files.

    Args:
        parent: Parent widget for the dialog
        file_path: Path to the password-protected PDF file
    """
    show_pdf_error(
        parent,
        "Password Protected PDF",
        f"Cannot open password-protected PDF:\n{file_path}",
        details="This PDF requires a password to open.\n\n"
        "Momovu does not currently support password-protected PDFs.\n"
        "Please remove the password protection and try again.",
        error_type="warning",
    )


def show_unexpected_error(
    parent: Optional[QWidget], operation: str, error: Exception
) -> None:
    """Show error dialog for unexpected errors.

    Args:
        parent: Parent widget for the dialog
        operation: Description of what was being attempted
        error: The exception that occurred
    """
    show_pdf_error(
        parent,
        "Unexpected Error",
        f"An unexpected error occurred while {operation}",
        details=f"Error details:\n{type(error).__name__}: {str(error)}",
        error_type="error",
    )
