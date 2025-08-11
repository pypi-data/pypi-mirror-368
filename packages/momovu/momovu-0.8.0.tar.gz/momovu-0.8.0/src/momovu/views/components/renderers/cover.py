"""Renderer for cover document margins and overlays."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QPen

from momovu.lib.constants import (
    BARCODE_AREA_COLOR,
    BARCODE_RECT_OPACITY,
    COVER_BLEED,
    POINTS_PER_MM,
    US_TRADE_BARCODE_HEIGHT,
    US_TRADE_BARCODE_WIDTH,
)
from momovu.views.components.renderers.base import BaseRenderer


class CoverRenderer(BaseRenderer):
    """Handles rendering for cover documents."""

    def draw_margins(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        margin: float,
        spine_width: float,
    ) -> None:
        """Render safety margins on front/back covers, excluding spine area.

        Cover layout: [back cover][spine][front cover]

        Args:
            x: Page left edge
            y: Page top edge
            width: Total cover width
            height: Cover height
            margin: Safety margin size
            spine_width: Book spine thickness
        """
        margin_brush = self.get_margin_brush()
        bleed_offset = COVER_BLEED * POINTS_PER_MM

        center_x = width / 2
        spine_left = center_x - spine_width / 2
        spine_right = center_x + spine_width / 2

        # BACK COVER MARGINS
        self.add_margin_rect(
            x + bleed_offset,
            y + bleed_offset,
            spine_left - bleed_offset,
            margin,
            margin_brush,
        )
        self.add_margin_rect(
            x + bleed_offset,
            y + height - margin - bleed_offset,
            spine_left - bleed_offset,
            margin,
            margin_brush,
        )
        self.add_margin_rect(
            x + bleed_offset,
            y + margin + bleed_offset,
            margin,
            height - 2 * margin - 2 * bleed_offset,
            margin_brush,
        )
        self.add_margin_rect(
            x + spine_left - margin,
            y + margin + bleed_offset,
            margin,
            height - 2 * margin - 2 * bleed_offset,
            margin_brush,
        )

        # NO SPINE MARGINS - spine area should be clear

        # FRONT COVER MARGINS
        self.add_margin_rect(
            x + spine_right,
            y + bleed_offset,
            width - spine_right - bleed_offset,
            margin,
            margin_brush,
        )
        self.add_margin_rect(
            x + spine_right,
            y + height - margin - bleed_offset,
            width - spine_right - bleed_offset,
            margin,
            margin_brush,
        )
        self.add_margin_rect(
            x + spine_right,
            y + margin + bleed_offset,
            margin,
            height - 2 * margin - 2 * bleed_offset,
            margin_brush,
        )
        self.add_margin_rect(
            x + width - margin - bleed_offset,
            y + margin + bleed_offset,
            margin,
            height - 2 * margin - 2 * bleed_offset,
            margin_brush,
        )

    def draw_trim_lines(self, x: float, y: float, width: float, height: float) -> None:
        """Add trim marks at cover edges accounting for bleed.

        Args:
            x: Page left edge
            y: Page top edge
            width: Total cover width
            height: Cover height
        """
        pen = self.get_trim_pen()
        bleed = COVER_BLEED * POINTS_PER_MM

        self.graphics_scene.addLine(
            x + bleed, y + bleed, x + width - bleed, y + bleed, pen
        )
        self.graphics_scene.addLine(
            x + bleed,
            y + height - bleed,
            x + width - bleed,
            y + height - bleed,
            pen,
        )

        self.graphics_scene.addLine(
            x + bleed, y + bleed, x + bleed, y + height - bleed, pen
        )
        self.graphics_scene.addLine(
            x + width - bleed, y + bleed, x + width - bleed, y + height - bleed, pen
        )

    def draw_spine_fold_lines(
        self, x: float, y: float, width: float, height: float, spine_width: float
    ) -> None:
        """Mark spine boundaries with dashed purple lines.

        Args:
            x: Page left edge
            y: Page top edge
            width: Total cover width
            height: Cover height
            spine_width: Book spine thickness
        """
        if not spine_width:
            return

        center_x = width / 2
        fold_pen = self.get_fold_pen()

        self.graphics_scene.addLine(
            x + center_x - spine_width / 2,
            y,
            x + center_x - spine_width / 2,
            y + height,
            fold_pen,
        )

        self.graphics_scene.addLine(
            x + center_x + spine_width / 2,
            y,
            x + center_x + spine_width / 2,
            y + height,
            fold_pen,
        )

    def draw_barcode(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        spine_width: float,
        safety_margin: float,
    ) -> None:
        """Highlight barcode placement area on back cover bottom-right.

        Args:
            x: Page left edge
            y: Page top edge
            width: Total cover width
            height: Cover height
            spine_width: Book spine thickness
            safety_margin: Distance from edges
        """
        barcode_width = US_TRADE_BARCODE_WIDTH * POINTS_PER_MM
        barcode_height = US_TRADE_BARCODE_HEIGHT * POINTS_PER_MM
        bleed_offset = COVER_BLEED * POINTS_PER_MM

        back_cover_width = (width - spine_width) / 2

        barcode_x = x + back_cover_width - safety_margin - barcode_width
        barcode_y = y + height - safety_margin - barcode_height - bleed_offset

        pen = QPen(Qt.PenStyle.NoPen)
        brush = QBrush(BARCODE_AREA_COLOR)

        barcode_rect = self.graphics_scene.addRect(
            barcode_x, barcode_y, barcode_width, barcode_height, pen, brush
        )
        barcode_rect.setOpacity(BARCODE_RECT_OPACITY)
