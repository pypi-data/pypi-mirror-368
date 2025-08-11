"""Base strategy for page rendering."""

from abc import ABC, abstractmethod
from typing import Callable, Optional

from PySide6.QtCore import QTimer
from PySide6.QtPdf import QPdfDocument
from PySide6.QtWidgets import QGraphicsScene

from momovu.lib.constants import IMMEDIATE_DELAY, Y_OFFSET_SPACING
from momovu.lib.logger import get_logger
from momovu.presenters.document import DocumentPresenter
from momovu.presenters.margin import MarginPresenter
from momovu.presenters.navigation import NavigationPresenter
from momovu.views.components.margin_renderer import MarginRenderer
from momovu.views.page_item import PageItem

logger = get_logger(__name__)


class BaseStrategy(ABC):
    """Abstract base class for page rendering strategies."""

    def __init__(
        self,
        graphics_scene: QGraphicsScene,
        pdf_document: QPdfDocument,
        document_presenter: DocumentPresenter,
        margin_presenter: MarginPresenter,
        navigation_presenter: NavigationPresenter,
        margin_renderer: MarginRenderer,
    ):
        """Initialize the render strategy.

        Args:
            graphics_scene: The Qt graphics scene to render to
            pdf_document: The Qt PDF document
            document_presenter: Presenter for document operations
            margin_presenter: Presenter for margin operations
            navigation_presenter: Presenter for navigation operations
            margin_renderer: Renderer for margins and overlays
        """
        self.graphics_scene = graphics_scene
        self.pdf_document = pdf_document
        self.document_presenter = document_presenter
        self.margin_presenter = margin_presenter
        self.navigation_presenter = navigation_presenter
        self.margin_renderer = margin_renderer

        self.Y_OFFSET_SPACING = Y_OFFSET_SPACING  # Points between pages/pairs

    @abstractmethod
    def render(
        self,
        current_page: int,
        is_presentation_mode: bool,
        show_fold_lines: bool,
        fit_callback: Optional[Callable[[], None]] = None,
    ) -> None:
        """Render pages according to the strategy.

        Args:
            current_page: Current page index (0-based)
            is_presentation_mode: Whether in presentation mode
            show_fold_lines: Whether to show fold lines
            fit_callback: Optional callback to fit page to view
        """
        pass

    def create_page_item(
        self, page_index: int, x: float, y: float
    ) -> Optional[PageItem]:
        """Instantiate and position a page widget for rendering.

        Args:
            page_index: Zero-based page index
            x: Left edge position in scene coordinates
            y: Top edge position in scene coordinates

        Returns:
            Positioned PageItem ready for scene insertion, None if page invalid
        """
        page_size = self.document_presenter.get_page_size(page_index)
        if not page_size:
            return None

        page_width, page_height = page_size
        page_item = PageItem(
            self.pdf_document,
            page_index,
            page_width,
            page_height,
        )
        page_item.setPos(x, y)
        return page_item

    def draw_overlays(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        skip_trim_edge: Optional[str] = None,
    ) -> None:
        """Render safety margins and trim indicators on top of page.

        Args:
            x: Page left edge in scene coordinates
            y: Page top edge in scene coordinates
            width: Page width in points
            height: Page height in points
            skip_trim_edge: Optional edge to skip when drawing trim lines ("left" or "right")
        """
        self.margin_renderer.draw_page_overlays(x, y, width, height, skip_trim_edge)

    def fit_to_view_if_needed(
        self, is_presentation_mode: bool, fit_callback: Optional[Callable[[], None]]
    ) -> None:
        """Schedule zoom adjustment for presentation mode.

        Args:
            is_presentation_mode: True triggers fit callback
            fit_callback: Function to scale view to page bounds
        """
        if is_presentation_mode and fit_callback:
            QTimer.singleShot(IMMEDIATE_DELAY, fit_callback)

    def update_scene_rect(self) -> None:
        """Expand scene boundaries to include all rendered pages."""
        self.graphics_scene.setSceneRect(self.graphics_scene.itemsBoundingRect())
