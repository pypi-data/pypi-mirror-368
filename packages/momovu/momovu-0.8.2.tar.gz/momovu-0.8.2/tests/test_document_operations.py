"""
Tests for document operations utilities.
"""

from PySide6.QtCore import QRectF

from momovu.lib.exceptions import DocumentLoadError
from momovu.views.components.document_operations import (
    DocumentOperationResult,
    calculate_page_bounds,
    calculate_spinbox_range,
    convert_page_index_to_number,
    convert_page_number_to_index,
    create_error_message,
    extract_filename_from_path,
    format_page_label,
    format_window_title,
    is_valid_page_number,
    safe_document_operation,
    should_show_error_dialog,
    validate_pdf_path,
)


class TestValidatePdfPath:
    """Test PDF path validation."""

    def test_empty_path(self):
        """Test empty path returns False."""
        assert not validate_pdf_path("")
        assert not validate_pdf_path(None)

    def test_nonexistent_file(self):
        """Test nonexistent file returns False."""
        assert not validate_pdf_path("/nonexistent/file.pdf")

    def test_non_pdf_extension(self, tmp_path):
        """Test non-PDF file returns False."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        assert not validate_pdf_path(str(test_file))

    def test_valid_pdf_file(self, tmp_path):
        """Test valid PDF file returns True."""
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"fake pdf content")
        assert validate_pdf_path(str(test_file))


class TestExtractFilenameFromPath:
    """Test filename extraction."""

    def test_simple_filename(self):
        """Test simple filename extraction."""
        assert extract_filename_from_path("/path/to/file.pdf") == "file.pdf"

    def test_windows_path(self):
        """Test Windows path."""
        # On Linux, this won't be interpreted as a Windows path
        # So we'll test with a forward slash path instead
        assert extract_filename_from_path("C:/path/to/file.pdf") == "file.pdf"

    def test_filename_only(self):
        """Test filename without path."""
        assert extract_filename_from_path("file.pdf") == "file.pdf"


class TestFormatWindowTitle:
    """Test window title formatting."""

    def test_base_title_only(self):
        """Test base title without filename."""
        assert format_window_title("Momovu") == "Momovu"
        assert format_window_title("Momovu", None) == "Momovu"

    def test_title_with_filename(self):
        """Test title with filename."""
        assert format_window_title("Momovu", "test.pdf") == "Momovu - test.pdf"


class TestFormatPageLabel:
    """Test page label formatting."""

    def test_normal_pages(self):
        """Test normal page formatting."""
        assert format_page_label(0, 10) == "Page: 1/10"
        assert format_page_label(4, 10) == "Page: 5/10"
        assert format_page_label(9, 10) == "Page: 10/10"

    def test_single_page(self):
        """Test single page document."""
        assert format_page_label(0, 1) == "Page: 1/1"


class TestCalculatePageBounds:
    """Test page bounds calculation."""

    def test_default_margin(self):
        """Test with default margin."""
        rect = QRectF(10, 20, 100, 200)
        bounds = calculate_page_bounds(rect)
        assert bounds.left() == 0  # 10 - 10
        assert bounds.top() == 10  # 20 - 10
        assert bounds.width() == 120  # 100 + 20
        assert bounds.height() == 220  # 200 + 20

    def test_custom_margin(self):
        """Test with custom margin."""
        rect = QRectF(10, 20, 100, 200)
        bounds = calculate_page_bounds(rect, margin=5)
        assert bounds.left() == 5  # 10 - 5
        assert bounds.top() == 15  # 20 - 5
        assert bounds.width() == 110  # 100 + 10
        assert bounds.height() == 210  # 200 + 10


class TestShouldShowErrorDialog:
    """Test error dialog decision logic."""

    def test_normal_exceptions(self):
        """Test normal exceptions should show dialog."""
        assert should_show_error_dialog(ValueError("test"))
        assert should_show_error_dialog(DocumentLoadError("test.pdf", "test"))
        assert should_show_error_dialog(RuntimeError("test"))

    def test_system_exceptions(self):
        """Test system exceptions should not show dialog."""
        assert not should_show_error_dialog(KeyboardInterrupt())
        assert not should_show_error_dialog(SystemExit())


class TestCreateErrorMessage:
    """Test error message creation."""

    def test_document_error(self):
        """Test DocumentError formatting."""
        error = DocumentLoadError("test.pdf", "Invalid PDF")
        message = create_error_message(error)
        assert (
            message == "Document Error: Failed to load document 'test.pdf': Invalid PDF"
        )

    def test_generic_error_with_context(self):
        """Test generic error with context."""
        error = ValueError("Invalid value")
        message = create_error_message(error, "loading document")
        assert message == "Error in loading document: Invalid value"

    def test_generic_error_without_context(self):
        """Test generic error without context."""
        error = ValueError("Invalid value")
        message = create_error_message(error)
        assert message == "An error occurred: Invalid value"


class TestDocumentOperationResult:
    """Test DocumentOperationResult class."""

    def test_success_result(self):
        """Test successful result."""
        result = DocumentOperationResult(True, "Success", {"data": "test"})
        assert result.success
        assert result.message == "Success"
        assert result.data["data"] == "test"
        assert bool(result) is True

    def test_failure_result(self):
        """Test failure result."""
        result = DocumentOperationResult(False, "Failed")
        assert not result.success
        assert result.message == "Failed"
        assert result.data == {}
        assert bool(result) is False

    def test_default_values(self):
        """Test default values."""
        result = DocumentOperationResult(True)
        assert result.success
        assert result.message == ""
        assert result.data == {}


class TestSafeDocumentOperation:
    """Test safe document operation wrapper."""

    def test_successful_operation(self):
        """Test successful operation."""

        def test_func(x, y):
            return x + y

        result = safe_document_operation("test_add", test_func, 2, 3)
        assert result.success
        assert result.data["result"] == 5
        assert "test_add completed" in result.message

    def test_document_error(self):
        """Test DocumentError handling."""

        def test_func():
            raise DocumentLoadError("test.pdf", "Test error")

        result = safe_document_operation("test_error", test_func)
        assert not result.success
        assert (
            "Document error: Failed to load document 'test.pdf': Test error"
            in result.message
        )

    def test_generic_error(self):
        """Test generic error handling."""

        def test_func():
            raise ValueError("Test error")

        result = safe_document_operation("test_error", test_func)
        assert not result.success
        assert "Unexpected error: Test error" in result.message


class TestCalculateSpinboxRange:
    """Test spinbox range calculation."""

    def test_normal_pages(self):
        """Test normal page count."""
        min_val, max_val = calculate_spinbox_range(10)
        assert min_val == 1
        assert max_val == 10

    def test_zero_pages(self):
        """Test zero pages."""
        min_val, max_val = calculate_spinbox_range(0)
        assert min_val == 1
        assert max_val == 1

    def test_negative_pages(self):
        """Test negative pages."""
        min_val, max_val = calculate_spinbox_range(-5)
        assert min_val == 1
        assert max_val == 1


class TestIsValidPageNumber:
    """Test page number validation."""

    def test_valid_pages(self):
        """Test valid page numbers."""
        assert is_valid_page_number(1, 10)
        assert is_valid_page_number(5, 10)
        assert is_valid_page_number(10, 10)

    def test_invalid_pages(self):
        """Test invalid page numbers."""
        assert not is_valid_page_number(0, 10)
        assert not is_valid_page_number(11, 10)
        assert not is_valid_page_number(-1, 10)


class TestPageNumberConversion:
    """Test page number/index conversion."""

    def test_number_to_index(self):
        """Test page number to index conversion."""
        assert convert_page_number_to_index(1) == 0
        assert convert_page_number_to_index(5) == 4
        assert convert_page_number_to_index(0) == 0  # Edge case
        assert convert_page_number_to_index(-1) == 0  # Edge case

    def test_index_to_number(self):
        """Test page index to number conversion."""
        assert convert_page_index_to_number(0) == 1
        assert convert_page_index_to_number(4) == 5
        assert convert_page_index_to_number(-1) == 1  # Edge case
