"""PDF page item for MVP viewer - renders dynamically based on zoom level."""

from typing import Optional

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QPainter
from PySide6.QtPdf import QPdfDocument
from PySide6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget

from momovu.lib.constants import MAX_RENDER_SCALE


class PageItem(QGraphicsItem):
    """PDF page graphics item that renders dynamically based on zoom level.

    This is a simplified version of PageItem specifically for the MVP viewer.
    It renders the PDF page at the appropriate resolution for the current zoom level.
    """

    def __init__(
        self,
        document: QPdfDocument,
        page_number: int,
        page_width: float,
        page_height: float,
    ):
        """Initialize the PDF page item.

        Args:
            document: The PDF document
            page_number: Zero-based page number
            page_width: Page width in points
            page_height: Page height in points
        """
        super().__init__()

        self.document = document
        self.page_number = page_number
        self.page_width = page_width
        self.page_height = page_height
        self.bounding_rect = QRectF(0, 0, page_width, page_height)

        self.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)

    def boundingRect(self) -> QRectF:
        """Define item's scene space boundaries for Qt rendering."""
        return self.bounding_rect

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: Optional[QWidget] = None,
    ) -> None:
        """Render PDF page dynamically scaled to current zoom level.

        Extracts zoom from painter transform and renders at appropriate
        resolution (capped at 4x to prevent memory issues).
        """
        transform = painter.transform()
        scale = max(transform.m11(), transform.m22())

        # Limit to reasonable maximum to avoid memory issues
        render_scale = min(scale, MAX_RENDER_SCALE)

        render_width = int(self.page_width * render_scale)
        render_height = int(self.page_height * render_scale)

        from PySide6.QtCore import QSize

        image = self.document.render(
            self.page_number, QSize(render_width, render_height)
        )

        if not image.isNull():
            target_rect = QRectF(0, 0, self.page_width, self.page_height)
            painter.drawImage(target_rect, image)
        else:
            painter.fillRect(self.bounding_rect, Qt.GlobalColor.red)
            painter.setPen(Qt.GlobalColor.white)
            painter.drawText(
                self.bounding_rect,
                Qt.AlignmentFlag.AlignCenter,
                f"Error\nPage {self.page_number + 1}",
            )
