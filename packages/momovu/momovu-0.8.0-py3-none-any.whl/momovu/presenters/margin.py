"""Margin presenter for handling margin calculations and logic.

This presenter manages margin operations without UI dependencies.
It coordinates between MarginSettingsModel and the view layer.
"""

from typing import Any, Optional

from momovu.lib.constants import (
    BARCODE_HEIGHT_POINTS,
    BARCODE_MARGIN_POINTS,
    BARCODE_WIDTH_POINTS,
    DEFAULT_SAFETY_MARGIN_MM,  # noqa: F401  # Imported for test_constants_imports.py
    FLAP_HEIGHT_RATIO,
    FLAP_WIDTH_RATIO,
    MM_TO_POINTS,
    SPINE_WIDTH_DIVISOR,
    SPINE_WIDTH_OFFSET,
)
from momovu.lib.logger import get_logger
from momovu.models.margin_settings import MarginSettingsModel
from momovu.presenters.base import BasePresenter

logger = get_logger(__name__)


class MarginPresenter(BasePresenter):
    """Presenter for margin calculations and management.

    This presenter handles:
    - Margin calculations
    - Trim line positioning
    - Spine/flap calculations
    - Barcode area logic
    """

    def __init__(self, model: Optional[MarginSettingsModel] = None) -> None:
        """Initialize the margin presenter.

        Args:
            model: Optional margin settings model to use
        """
        super().__init__()
        self._model = model or MarginSettingsModel()

        self._model.add_observer(self._on_model_changed)

    def initialize(self) -> None:
        """Sync initial margin settings to the view."""
        self.update_view(
            document_type=self._model.document_type,
            safety_margin_mm=self._model.safety_margin_mm,
            safety_margin_points=self._model.safety_margin_points,
            spine_width=self._model.spine_width,
            flap_width=self._model.flap_width,
            flap_height=self._model.flap_height,
        )

    def set_document_type(self, document_type: str) -> None:
        """Set the document type.

        Args:
            document_type: Type of document ('interior', 'cover', 'dustjacket')
        """
        self._model.document_type = document_type

        if document_type in ["cover", "dustjacket"]:
            self._calculate_spine_width()

            if document_type == "dustjacket":
                # Standard dustjacket flap dimensions from constants
                self._model.flap_width = FLAP_WIDTH_RATIO * MM_TO_POINTS
                self._model.flap_height = FLAP_HEIGHT_RATIO * MM_TO_POINTS

        logger.info(f"Document type set to: {document_type}")

    def get_document_type(self) -> str:
        """Get the current document type.

        Returns:
            The current document type ('interior', 'cover', or 'dustjacket')
        """
        return self._model.document_type

    def set_num_pages(self, num_pages: int) -> None:
        """Update page count and recalculate spine width for cover/dustjacket.

        Args:
            num_pages: Total pages in the document
        """
        self._model.num_pages = num_pages
        if self._model.document_type in ["cover", "dustjacket"]:
            self._calculate_spine_width()

    def set_show_margins(self, show: bool) -> None:
        """Enable or disable safety margin overlay display.

        Args:
            show: True to display margin overlays
        """
        self._model.show_margins = show

    def set_show_trim_lines(self, show: bool) -> None:
        """Enable or disable trim line display at page edges.

        Args:
            show: True to display trim lines
        """
        self._model.show_trim_lines = show

    def set_show_barcode(self, show: bool) -> None:
        """Enable or disable barcode area indicator on covers.

        Args:
            show: True to display barcode area
        """
        self._model.show_barcode = show

    def set_show_fold_lines(self, show: bool) -> None:
        """Enable or disable spine/flap fold line display.

        Args:
            show: True to display fold lines
        """
        self._model.show_fold_lines = show

    def _calculate_spine_width(self) -> None:
        """Apply industry-standard formula to determine spine thickness from page count."""
        num_pages = self._model.num_pages if self._model.num_pages > 0 else 100

        # Industry-standard formula accounts for paper thickness and binding requirements
        spine_width_mm = (num_pages / SPINE_WIDTH_DIVISOR) + SPINE_WIDTH_OFFSET

        self._model.spine_width = spine_width_mm * MM_TO_POINTS

        logger.info(
            f"Calculated spine width: {spine_width_mm:.2f}mm ({self._model.spine_width:.2f} points) for {num_pages} pages"
        )

    def set_safety_margin(self, margin_mm: float) -> None:
        """Set the safety margin in millimeters.

        Args:
            margin_mm: Safety margin in millimeters
        """
        margin_points = margin_mm * MM_TO_POINTS
        self._model.update_margins(margin_mm, margin_points)
        logger.info(f"Safety margin set to: {margin_mm}mm ({margin_points:.1f} points)")

    def set_spine_width(self, width: Optional[float]) -> None:
        """Set the spine width.

        Args:
            width: Spine width in points, or None to clear
        """
        self._model.spine_width = width
        logger.info(f"Spine width set to: {width}")

    def set_flap_dimensions(
        self, width: Optional[float] = None, height: Optional[float] = None
    ) -> None:
        """Set flap dimensions.

        Args:
            width: Flap width in points
            height: Flap height in points
        """
        self._model.update_spine_dimensions(flap_width=width, flap_height=height)
        logger.info(f"Flap dimensions set to: {width}x{height}")

    def calculate_margin_rect(
        self, page_width: float, page_height: float, is_right_page: bool = False
    ) -> tuple[float, float, float, float]:
        """Calculate the margin rectangle for a page.

        Args:
            page_width: Page width in points
            page_height: Page height in points
            is_right_page: True if this is a right-side page

        Returns:
            Tuple of (x, y, width, height) for the margin rectangle
        """
        margin = self._model.safety_margin_points

        x = margin
        y = margin
        width = page_width - (2 * margin)
        height = page_height - (2 * margin)

        # Adjust for spine if applicable
        if self._model.spine_width and self._model.is_cover_or_dustjacket():
            if is_right_page:
                # Right page: add spine width to left margin
                x += self._model.spine_width / 2
            else:
                # Left page: reduce width by spine amount
                width -= self._model.spine_width / 2

        return (x, y, width, height)

    def calculate_trim_lines(
        self, page_width: float, page_height: float
    ) -> dict[str, tuple[float, float, float, float]]:
        """Calculate trim line positions.

        Args:
            page_width: Page width in points
            page_height: Page height in points

        Returns:
            Dictionary of line positions with keys 'top', 'bottom', 'left', 'right'
            Each value is a tuple of (x1, y1, x2, y2)
        """
        margin = self._model.safety_margin_points

        lines = {
            "top": (0, margin, page_width, margin),
            "bottom": (0, page_height - margin, page_width, page_height - margin),
            "left": (margin, 0, margin, page_height),
            "right": (page_width - margin, 0, page_width - margin, page_height),
        }

        return lines

    def calculate_spine_position(
        self, page_width: float, page_height: float, is_spread: bool = False
    ) -> Optional[tuple[float, float, float, float]]:
        """Calculate spine line position for covers/dustjackets.

        Args:
            page_width: Page width in points
            page_height: Page height in points
            is_spread: True if viewing as a spread

        Returns:
            Tuple of (x1, y1, x2, y2) for the spine line, or None
        """
        if not self._model.spine_width or not self._model.is_cover_or_dustjacket():
            return None

        if is_spread:
            x = page_width  # At the edge between pages
            return (x, 0, x, page_height)
        else:
            x = page_width / 2
            return (x, 0, x, page_height)

    def calculate_fold_lines(
        self, page_width: float, page_height: float
    ) -> dict[str, Optional[tuple[float, float, float, float]]]:
        """Calculate fold line positions for dustjackets.

        Args:
            page_width: Page width in points
            page_height: Page height in points

        Returns:
            Dictionary with 'left_fold' and 'right_fold' positions
        """
        fold_lines: dict[str, Optional[tuple[float, float, float, float]]] = {
            "left_fold": None,
            "right_fold": None,
        }

        if self._model.is_dustjacket() and self._model.flap_width:
            x_left = self._model.flap_width
            fold_lines["left_fold"] = (x_left, 0, x_left, page_height)

            x_right = page_width - self._model.flap_width
            fold_lines["right_fold"] = (x_right, 0, x_right, page_height)

        return fold_lines

    def calculate_barcode_area(
        self, page_width: float, page_height: float
    ) -> Optional[tuple[float, float, float, float]]:
        """Calculate barcode area position for covers.

        Args:
            page_width: Page width in points
            page_height: Page height in points

        Returns:
            Tuple of (x, y, width, height) for barcode area, or None
        """
        if not self._model.is_cover():
            return None

        x = page_width - BARCODE_WIDTH_POINTS - BARCODE_MARGIN_POINTS
        y = page_height - BARCODE_HEIGHT_POINTS - BARCODE_MARGIN_POINTS

        return (x, y, BARCODE_WIDTH_POINTS, BARCODE_HEIGHT_POINTS)

    def _on_model_changed(self, event: Any) -> None:
        """Handle model property changes.

        Args:
            event: Property changed event from the model
        """
        if self.has_view:
            self.update_view(**{event.property_name: event.new_value})

    def cleanup(self) -> None:
        """Remove model observer and release resources."""
        self._model.remove_observer(self._on_model_changed)
        super().cleanup()

    @property
    def model(self) -> MarginSettingsModel:
        """Access the underlying margin settings model."""
        return self._model
