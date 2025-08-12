"""Margin settings model for MVP architecture.

This model handles margin configuration without any UI dependencies.
"""

from typing import Optional, cast

from momovu.lib.constants import DEFAULT_SAFETY_MARGIN_MM, MM_TO_POINTS
from momovu.models.base import BaseModel


class MarginSettingsModel(BaseModel):
    """Model for margin settings data.

    This model stores:
    - Safety margins (in mm and points)
    - Spine width
    - Flap dimensions
    - Document type

    It does NOT handle:
    - Margin rendering (that's a view concern)
    - Margin calculation (that's a presenter concern)
    """

    # Document type constants
    DOCUMENT_TYPE_INTERIOR = "interior"
    DOCUMENT_TYPE_COVER = "cover"
    DOCUMENT_TYPE_DUSTJACKET = "dustjacket"

    def __init__(self) -> None:
        """Initialize margin settings with publishing industry defaults."""
        super().__init__()

        # Define validation rules
        self.add_validator(
            "document_type",
            lambda x: x
            in [
                self.DOCUMENT_TYPE_INTERIOR,
                self.DOCUMENT_TYPE_COVER,
                self.DOCUMENT_TYPE_DUSTJACKET,
            ],
        )
        self.add_validator("num_pages", lambda x: isinstance(x, int) and x > 0)
        self.add_validator(
            "safety_margin_mm", lambda x: isinstance(x, (int, float)) and x >= 0
        )
        self.add_validator(
            "safety_margin_points", lambda x: isinstance(x, (int, float)) and x >= 0
        )
        self.add_validator(
            "spine_width",
            lambda x: x is None or (isinstance(x, (int, float)) and x >= 0),
        )
        self.add_validator(
            "flap_width",
            lambda x: x is None or (isinstance(x, (int, float)) and x >= 0),
        )
        self.add_validator(
            "flap_height",
            lambda x: x is None or (isinstance(x, (int, float)) and x >= 0),
        )
        # Boolean visibility flags must be true/false
        self.add_validator("show_margins", lambda x: isinstance(x, bool))
        self.add_validator("show_trim_lines", lambda x: isinstance(x, bool))
        self.add_validator("show_barcode", lambda x: isinstance(x, bool))
        self.add_validator("show_fold_lines", lambda x: isinstance(x, bool))

        # Initialize properties with defaults
        self.set_property("document_type", self.DOCUMENT_TYPE_INTERIOR, validate=True)
        self.set_property("num_pages", 100, validate=True)  # Default page count
        self.set_property(
            "safety_margin_mm", DEFAULT_SAFETY_MARGIN_MM, validate=True
        )  # 0.5 inches default
        self.set_property(
            "safety_margin_points",
            DEFAULT_SAFETY_MARGIN_MM * MM_TO_POINTS,
            validate=True,
        )  # 12.7mm in points
        self.set_property("spine_width", None, validate=True)
        self.set_property("flap_width", None, validate=True)
        self.set_property("flap_height", None, validate=True)
        self.set_property("show_margins", True, validate=True)
        self.set_property("show_trim_lines", True, validate=True)
        self.set_property("show_barcode", True, validate=True)
        self.set_property("show_fold_lines", True, validate=True)

    @property
    def document_type(self) -> str:
        """Current document type: 'interior', 'cover', or 'dustjacket'."""
        return cast(
            "str", self.get_property("document_type", self.DOCUMENT_TYPE_INTERIOR)
        )

    @document_type.setter
    def document_type(self, value: str) -> None:
        """Change document type (affects available overlays)."""
        self.set_property("document_type", value)

    @property
    def num_pages(self) -> int:
        """Get number of pages."""
        return cast("int", self.get_property("num_pages", 100))

    @num_pages.setter
    def num_pages(self, value: int) -> None:
        """Set number of pages."""
        self.set_property("num_pages", value)

    @property
    def safety_margin_mm(self) -> float:
        """Get safety margin in millimeters."""
        return cast(
            "float", self.get_property("safety_margin_mm", DEFAULT_SAFETY_MARGIN_MM)
        )

    @safety_margin_mm.setter
    def safety_margin_mm(self, value: float) -> None:
        """Set safety margin in millimeters."""
        self.set_property("safety_margin_mm", value)

    @property
    def safety_margin_points(self) -> float:
        """Get safety margin in points."""
        return cast(
            "float",
            self.get_property(
                "safety_margin_points", DEFAULT_SAFETY_MARGIN_MM * MM_TO_POINTS
            ),
        )

    @safety_margin_points.setter
    def safety_margin_points(self, value: float) -> None:
        """Set safety margin in points."""
        self.set_property("safety_margin_points", value)

    @property
    def spine_width(self) -> Optional[float]:
        """Get spine width."""
        return cast("Optional[float]", self.get_property("spine_width"))

    @spine_width.setter
    def spine_width(self, value: Optional[float]) -> None:
        """Set spine width."""
        self.set_property("spine_width", value)

    @property
    def flap_width(self) -> Optional[float]:
        """Get flap width."""
        return cast("Optional[float]", self.get_property("flap_width"))

    @flap_width.setter
    def flap_width(self, value: Optional[float]) -> None:
        """Set flap width."""
        self.set_property("flap_width", value)

    @property
    def flap_height(self) -> Optional[float]:
        """Get flap height."""
        return cast("Optional[float]", self.get_property("flap_height"))

    @flap_height.setter
    def flap_height(self, value: Optional[float]) -> None:
        """Set flap height."""
        self.set_property("flap_height", value)

    @property
    def show_margins(self) -> bool:
        """Get show margins flag."""
        return cast("bool", self.get_property("show_margins", True))

    @show_margins.setter
    def show_margins(self, value: bool) -> None:
        """Set show margins flag."""
        self.set_property("show_margins", value)

    @property
    def show_trim_lines(self) -> bool:
        """Get show trim lines flag."""
        return cast("bool", self.get_property("show_trim_lines", True))

    @show_trim_lines.setter
    def show_trim_lines(self, value: bool) -> None:
        """Set show trim lines flag."""
        self.set_property("show_trim_lines", value)

    @property
    def show_barcode(self) -> bool:
        """Get show barcode flag."""
        return cast("bool", self.get_property("show_barcode", True))

    @show_barcode.setter
    def show_barcode(self, value: bool) -> None:
        """Set show barcode flag."""
        self.set_property("show_barcode", value)

    @property
    def show_fold_lines(self) -> bool:
        """Get show fold lines flag."""
        return cast("bool", self.get_property("show_fold_lines", True))

    @show_fold_lines.setter
    def show_fold_lines(self, value: bool) -> None:
        """Set show fold lines flag."""
        self.set_property("show_fold_lines", value)

    def is_interior(self) -> bool:
        """True if document is interior pages (book content)."""
        return self.document_type == self.DOCUMENT_TYPE_INTERIOR

    def is_cover(self) -> bool:
        """True if document is a book cover."""
        return self.document_type == self.DOCUMENT_TYPE_COVER

    def is_dustjacket(self) -> bool:
        """True if document is a dustjacket with flaps."""
        return self.document_type == self.DOCUMENT_TYPE_DUSTJACKET

    def is_cover_or_dustjacket(self) -> bool:
        """True if document has spine (not interior pages)."""
        return self.document_type in [
            self.DOCUMENT_TYPE_COVER,
            self.DOCUMENT_TYPE_DUSTJACKET,
        ]

    def update_margins(
        self, safety_margin_mm: float, safety_margin_points: float
    ) -> None:
        """Batch update margin values in both units.

        Args:
            safety_margin_mm: Safety margin in millimeters
            safety_margin_points: Same margin converted to points
        """
        self.begin_batch_update()
        try:
            self.safety_margin_mm = safety_margin_mm
            self.safety_margin_points = safety_margin_points
        finally:
            self.end_batch_update()

    def update_spine_dimensions(
        self,
        spine_width: Optional[float] = None,
        flap_width: Optional[float] = None,
        flap_height: Optional[float] = None,
    ) -> None:
        """Batch update cover/dustjacket physical dimensions.

        Args:
            spine_width: Book spine thickness in points
            flap_width: Dustjacket flap width in points
            flap_height: Dustjacket flap height in points
        """
        self.begin_batch_update()
        try:
            if spine_width is not None:
                self.spine_width = spine_width
            if flap_width is not None:
                self.flap_width = flap_width
            if flap_height is not None:
                self.flap_height = flap_height
        finally:
            self.end_batch_update()

    def __repr__(self) -> str:
        """Developer-friendly string representation of margin settings."""
        return (
            f"MarginSettingsModel(document_type={self.document_type!r}, "
            f"safety_margin_mm={self.safety_margin_mm}, "
            f"spine_width={self.spine_width})"
        )
