"""Base renderer class for margin and overlay drawing."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QPen
from PySide6.QtWidgets import QGraphicsScene

from momovu.lib.constants import (
    FOLD_LINE_COLOR,
    FOLD_LINE_PEN_WIDTH,
    MARGIN_OVERLAY_COLOR,
    MARGIN_RECT_OPACITY,
    TRIM_LINE_COLOR,
    TRIM_LINE_PEN_WIDTH,
)
from momovu.lib.logger import get_logger

logger = get_logger(__name__)


class BaseRenderer:
    """Base class for all margin renderers."""

    def __init__(self, graphics_scene: QGraphicsScene) -> None:
        """Initialize the base renderer.

        Args:
            graphics_scene: The Qt graphics scene to render to
        """
        self.graphics_scene = graphics_scene

    def add_margin_rect(
        self, x: float, y: float, w: float, h: float, brush: QBrush
    ) -> None:
        """Draw semi-transparent colored rectangle for margin visualization.

        Args:
            x: Rectangle left edge
            y: Rectangle top edge
            w: Rectangle width
            h: Rectangle height
            brush: Fill color/pattern
        """
        rect = self.graphics_scene.addRect(x, y, w, h, QPen(Qt.PenStyle.NoPen), brush)
        rect.setOpacity(MARGIN_RECT_OPACITY)

    def get_margin_brush(self) -> QBrush:
        """Create brush for safety margin overlay rendering.

        Returns:
            Semi-transparent blue/purple brush
        """
        return QBrush(MARGIN_OVERLAY_COLOR)

    def get_fold_pen(self) -> QPen:
        """Create pen for spine/flap fold indicators.

        Returns:
            2px purple dashed line pen
        """
        pen = QPen(FOLD_LINE_COLOR)
        pen.setWidth(FOLD_LINE_PEN_WIDTH)
        pen.setStyle(Qt.PenStyle.DashLine)
        return pen

    def get_trim_pen(self) -> QPen:
        """Create pen for page edge trim marks.

        Returns:
            1px solid black line pen
        """
        pen = QPen(TRIM_LINE_COLOR)
        pen.setWidth(TRIM_LINE_PEN_WIDTH)
        pen.setStyle(Qt.PenStyle.SolidLine)
        return pen
