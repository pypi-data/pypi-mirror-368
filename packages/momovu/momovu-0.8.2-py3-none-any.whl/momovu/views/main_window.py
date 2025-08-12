"""Main window for the Momovu PDF viewer application.

This refactored version delegates functionality to specialized components,
keeping the main window clean and focused on coordination only.
"""

from typing import TYPE_CHECKING, Optional, Union

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QBrush, QCloseEvent, QKeyEvent, QPainter
from PySide6.QtWidgets import (
    QGraphicsScene,
    QLabel,
    QMainWindow,
    QMessageBox,
    QSpinBox,
    QStatusBar,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from momovu.lib.constants import (
    DEFAULT_WINDOW_HEIGHT,
    DEFAULT_WINDOW_WIDTH,
    MIN_WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH,
)
from momovu.lib.exceptions import PageRenderError
from momovu.lib.logger import get_logger
from momovu.views.components.cleanup_coordinator import CleanupCoordinator
from momovu.views.components.dialog_manager import DialogManager
from momovu.views.components.document_operations import (
    create_error_message,
    extract_filename_from_path,
    format_window_title,
    safe_document_operation,
    should_show_error_dialog,
)
from momovu.views.components.graphics_view import GraphicsView
from momovu.views.components.menu_builder import MenuBuilder
from momovu.views.components.navigation_controller import NavigationController
from momovu.views.components.page_renderer import PageRenderer
from momovu.views.components.signal_connections import SignalConnections
from momovu.views.components.toggle_manager import ToggleManager
from momovu.views.components.toolbar_builder import ToolbarBuilder
from momovu.views.components.ui_state_manager import UIStateManager
from momovu.views.components.window_setup import WindowSetup
from momovu.views.components.zoom_controller import ZoomController

if TYPE_CHECKING:
    from PySide6.QtPdf import QPdfDocument

    from momovu.presenters.document import DocumentPresenter
    from momovu.presenters.margin import MarginPresenter
    from momovu.presenters.navigation import NavigationPresenter
    from momovu.views.components.page_spinbox import PageSpinBox

logger = get_logger(__name__)


class MainWindow(QMainWindow):
    """Main window for the MVP PDF viewer application."""

    # Signals
    open_file_requested = Signal(str)
    page_changed = Signal(int)
    zoom_changed = Signal(float)
    view_mode_toggled = Signal()
    fullscreen_toggled = Signal()
    presentation_toggled = Signal()
    margins_toggled = Signal()
    trim_lines_toggled = Signal()
    document_type_changed = Signal(str)

    def __init__(
        self,
        pdf_path: Optional[str] = None,
        num_pages: Optional[int] = None,
        book_type: Optional[str] = None,
        side_by_side: bool = False,
        show_margins: Optional[bool] = None,
        show_trim_lines: Optional[bool] = None,
        show_barcode: Optional[bool] = None,
        show_fold_lines: Optional[bool] = None,
        start_presentation: bool = False,
        start_fullscreen: bool = False,
    ) -> None:
        """Initialize the main window."""
        super().__init__()

        self.pdf_document: Optional[QPdfDocument] = None
        self.document_presenter: Optional[DocumentPresenter] = None
        self.margin_presenter: Optional[MarginPresenter] = None
        self.navigation_presenter: Optional[NavigationPresenter] = None
        self.page_number_spinbox: Optional[Union[QSpinBox, PageSpinBox]] = None
        self.num_pages_spinbox: Optional[QSpinBox] = None
        self.toolbar: Optional[QToolBar] = None
        self.status_bar: Optional[QStatusBar] = None
        self.show_fold_lines_action: Optional[QAction] = None
        self._show_margins: bool = True
        self._show_trim_lines: bool = True
        self._show_barcode: bool = True
        self._show_fold_lines: bool = True

        self._resources_initialized = False

        try:
            self.window_initializer = WindowSetup(self)

            self.window_initializer.init_models_and_presenters()

            self.window_initializer.store_init_params(
                pdf_path,
                num_pages,
                book_type,
                side_by_side,
                show_margins,
                show_trim_lines,
                show_barcode,
                show_fold_lines,
                start_presentation,
                start_fullscreen,
            )

            self._setup_ui()
            self._setup_components()

            self._resources_initialized = True

            self.window_initializer.apply_initial_settings()
            self.window_initializer.initialize_document()

        except Exception as e:
            logger.error(f"Failed to initialize main window: {e}", exc_info=True)
            self._cleanup_resources()
            raise

    def _setup_ui(self) -> None:
        """Set up the user interface with error handling."""
        try:
            self.setWindowTitle("Momovu")
            self.resize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
            self.setMinimumSize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)

            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)
            layout.setContentsMargins(0, 0, 0, 0)

            self.graphics_view = GraphicsView(self)
            self.graphics_scene = QGraphicsScene()
            self.graphics_view.setScene(self.graphics_scene)
            self.graphics_view.setRenderHint(QPainter.RenderHint.Antialiasing)
            self.graphics_view.setBackgroundBrush(QBrush(Qt.GlobalColor.white))
            layout.addWidget(self.graphics_view)

            self.status_bar = self.statusBar()
            self.page_label = QLabel("Page: 0/0")
            self.status_bar.addPermanentWidget(self.page_label)

        except Exception as e:
            logger.error(f"Failed to setup UI: {e}", exc_info=True)
            raise

    def _setup_components(self) -> None:
        """Set up UI components using builders."""
        self.menu_builder = MenuBuilder(self)
        self.menu_builder.build_menus()
        self.menu_builder.update_initial_states(
            self._show_margins,
            self._show_trim_lines,
            self._show_barcode,
            self._show_fold_lines,
        )

        self.toolbar_builder = ToolbarBuilder(self)
        self.toolbar_builder.build_toolbar(
            self.menu_builder.actions, self.margin_presenter
        )

        if (
            self.pdf_document is None
            or self.document_presenter is None
            or self.margin_presenter is None
            or self.navigation_presenter is None
        ):
            logger.error("Required components not initialized for PageRenderer")
            raise RuntimeError(
                "Cannot create PageRenderer: required components not initialized. "
                "Ensure WindowSetup.init_models_and_presenters() was called."
            )

        self.page_renderer = PageRenderer(
            self.graphics_scene,
            self.pdf_document,
            self.document_presenter,
            self.margin_presenter,
            self.navigation_presenter,
        )

        self.ui_state_manager = UIStateManager(self)
        self.is_presentation_mode = self.ui_state_manager.is_presentation_mode

        self.toggle_manager = ToggleManager(self)

        self.navigation_controller = NavigationController(self)

        self.dialog_manager = DialogManager(self)
        self.dialog_manager.set_file_load_callback(self.load_pdf)
        self.dialog_manager.set_page_navigation_callback(
            self.navigation_controller.navigate_to_page
        )

        self.zoom_controller = ZoomController(
            self.graphics_view, self.graphics_scene, self
        )
        self.zoom_controller.set_presenter_callbacks(
            lambda: self.margin_presenter,
            lambda: self.navigation_presenter,
            lambda: self.document_presenter,
        )
        self.zoom_controller.set_update_callback(self.update_page_label)

        self.cleanup_coordinator = CleanupCoordinator(self)

        self.window_initializer.create_action_aliases()

        self.signal_connector = SignalConnections(self)
        self.signal_connector.connect_all_signals()

    def load_pdf(self, file_path: str) -> None:
        """Load a PDF file with error handling."""
        if not self.document_presenter or not self.navigation_presenter:
            logger.error("Presenters not initialized")
            return

        def _load_document() -> bool:
            """Internal function to load the document."""
            if not self.document_presenter or not self.navigation_presenter:
                return False

            success = self.document_presenter.load_document(file_path)

            if success:
                filename = extract_filename_from_path(file_path)
                self.setWindowTitle(format_window_title("Momovu", filename))

                page_count = self.document_presenter.get_page_count()
                self.navigation_presenter.set_total_pages(page_count)
                if self.page_number_spinbox:
                    self.page_number_spinbox.setMaximum(
                        page_count if page_count > 0 else 1
                    )
                self.update_page_label()

                # Update View menu based on current document type
                if (
                    hasattr(self, "menu_builder")
                    and self.menu_builder
                    and self.margin_presenter
                ):
                    current_doc_type = self.margin_presenter.get_document_type()
                    self.menu_builder.update_view_menu_for_document_type(
                        current_doc_type
                    )

                self.render_current_page()

                # Automatically fit to page after loading to ensure proper centering
                # This fixes the initial view issue caused by scene padding
                from PySide6.QtCore import QTimer

                QTimer.singleShot(100, self.fit_to_page)

                logger.info(f"PDF loaded: {file_path}")
                return True
            else:
                logger.error(f"Failed to load PDF: {file_path}")
                return False

        result = safe_document_operation("load PDF", _load_document)

        if not result.success and should_show_error_dialog(Exception(result.message)):
            error_message = create_error_message(
                Exception(result.message), "loading PDF"
            )
            QMessageBox.critical(self, "Load Error", error_message)

    def render_current_page(self) -> None:
        """Render pages using the page renderer component with error handling."""
        try:
            current_page = (
                self.navigation_presenter.get_current_page()
                if self.navigation_presenter
                else -1
            )
            view_mode = (
                self.navigation_presenter.model.view_mode
                if self.navigation_presenter
                else "unknown"
            )
            logger.info(
                f"[DIAGNOSTIC] render_current_page called - page: {current_page}, view_mode: {view_mode}, presentation: {self.ui_state_manager.is_presentation_mode}"
            )

            self.page_renderer.set_presentation_mode(
                self.ui_state_manager.is_presentation_mode
            )
            if hasattr(self, "show_fold_lines_action") and self.show_fold_lines_action:
                self.page_renderer.set_show_fold_lines(
                    self.show_fold_lines_action.isChecked()
                )
            self.page_renderer.render_current_page(self.zoom_controller.fit_to_page)
            self.update_page_label()

            # Update toolbar visibility based on document type
            # This ensures "Page" and "Pages" spinboxes are shown/hidden appropriately
            if hasattr(self, "toolbar_builder") and self.toolbar_builder:
                self.toolbar_builder.update_toolbar_visibility()

            logger.info("[DIAGNOSTIC] render_current_page completed")
        except PageRenderError as e:
            logger.error(f"Rendering error: {e}", exc_info=True)
            QMessageBox.warning(
                self, "Rendering Error", f"Failed to render page:\n{str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error during rendering: {e}", exc_info=True)

    def update_page_label(self) -> None:
        """Update the page label in the status bar and spinbox."""
        if not self.navigation_presenter:
            return

        current = self.navigation_presenter.get_current_page() + 1
        total = self.navigation_presenter.get_total_pages()

        if hasattr(self, "page_label"):
            self.page_label.setText(f"Page: {current}/{total}")

        if (
            hasattr(self, "page_number_spinbox")
            and self.page_number_spinbox is not None
        ):
            self.page_number_spinbox.blockSignals(True)
            self.page_number_spinbox.setValue(current)
            self.page_number_spinbox.blockSignals(False)

            self.page_number_spinbox.update()
        else:
            logger.warning(
                f"page_number_spinbox not available when updating to page {current}"
            )

    def on_page_number_changed(self, value: int) -> None:
        """Handle page number spinbox change.

        Args:
            value: New page number (1-based)
        """
        # With setKeyboardTracking(False), this is only called when:
        # - User presses Enter after typing
        # - User clicks arrow buttons
        # - Spinbox loses focus after typing
        self.navigation_controller.on_page_number_changed(value)

    def on_num_pages_changed(self, value: int) -> None:
        """Handle number of pages spinbox change."""
        if not self.margin_presenter:
            return

        self.margin_presenter.set_num_pages(value)
        if self.margin_presenter.model.document_type in ["cover", "dustjacket"]:
            self.render_current_page()

    def open_file_dialog(self) -> None:
        """Open a file dialog to select a PDF with error handling."""
        try:
            self.dialog_manager.show_open_file_dialog()
        except Exception as e:
            logger.error(f"Error in file dialog: {e}", exc_info=True)
            QMessageBox.critical(
                self, "File Dialog Error", f"Failed to open file dialog:\n{str(e)}"
            )

    def toggle_fullscreen(self) -> None:
        """Toggle fullscreen mode."""
        self.toggle_manager.toggle_fullscreen()

    def toggle_presentation(self) -> None:
        """Toggle presentation mode."""
        self.toggle_manager.toggle_presentation()

        if hasattr(self, "toolbar_builder") and self.toolbar_builder:
            self.toolbar_builder.update_toolbar_visibility()

    def enter_presentation_mode(self) -> None:
        """Enter presentation mode."""
        self.toggle_manager.enter_presentation_mode()

        if hasattr(self, "toolbar_builder") and self.toolbar_builder:
            self.toolbar_builder.update_toolbar_visibility()

    def exit_presentation_mode(self) -> None:
        """Exit presentation mode."""
        self.toggle_manager.exit_presentation_mode()

        if hasattr(self, "toolbar_builder") and self.toolbar_builder:
            self.toolbar_builder.update_toolbar_visibility()

    def toggle_side_by_side(self) -> None:
        """Toggle side-by-side view mode."""
        self.toggle_manager.toggle_side_by_side()

        if hasattr(self, "toolbar_builder") and self.toolbar_builder:
            self.toolbar_builder.update_toolbar_visibility()

    def toggle_margins(self) -> None:
        """Toggle margin visibility."""
        self.toggle_manager.toggle_margins()

    def toggle_trim_lines(self) -> None:
        """Toggle trim lines visibility."""
        self.toggle_manager.toggle_trim_lines()

    def toggle_barcode(self) -> None:
        """Toggle barcode visibility."""
        self.toggle_manager.toggle_barcode()

    def toggle_fold_lines(self) -> None:
        """Toggle fold lines visibility."""
        self.toggle_manager.toggle_fold_lines()

    def set_document_type(self, doc_type: str) -> None:
        """Set the document type."""
        self.toggle_manager.set_document_type(doc_type)

        if hasattr(self, "toolbar_builder") and self.toolbar_builder:
            self.toolbar_builder.update_toolbar_visibility()

    def zoom_in(self) -> None:
        """Zoom in from viewport center."""
        self.zoom_controller.zoom_in()

    def zoom_out(self) -> None:
        """Zoom out from viewport center."""
        self.zoom_controller.zoom_out()

    def fit_to_page(self) -> None:
        """Fit the current page(s) to the view."""
        self.zoom_controller.fit_to_page()

    def show_shortcuts_dialog(self) -> None:
        """Show the keyboard shortcuts dialog."""
        self.dialog_manager.show_shortcuts_dialog()

    def show_about_dialog(self) -> None:
        """Show the about dialog."""
        self.dialog_manager.show_about_dialog()

    def show_go_to_page_dialog(self) -> None:
        """Show the go to page dialog."""
        self.dialog_manager.show_go_to_page_dialog_with_presenters(
            self.document_presenter, self.navigation_presenter
        )

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle keyboard events by delegating to GraphicsView.

        This exists for compatibility with tests and Qt's event system.
        All actual handling is in GraphicsView.
        """
        if hasattr(self, "graphics_view"):
            self.graphics_view.keyPressEvent(event)
        else:
            super().keyPressEvent(event)

    def go_to_first_page(self) -> None:
        """Navigate to first page."""
        self.navigation_controller.navigate_first()

    def previous_page(self) -> None:
        """Navigate to previous page."""
        self.navigation_controller.navigate_previous()

    def next_page(self) -> None:
        """Navigate to next page."""
        self.navigation_controller.navigate_next()

    def go_to_last_page(self) -> None:
        """Navigate to last page."""
        self.navigation_controller.navigate_last()

    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle window close event and cleanup resources."""
        logger.info("Main window closing, cleaning up resources")
        self._cleanup_resources()
        super().closeEvent(event)

    def _cleanup_resources(self) -> None:
        """Clean up resources when closing or on error.

        This method delegates to the CleanupCoordinator for proper resource cleanup.
        """
        if hasattr(self, "cleanup_coordinator"):
            self.cleanup_coordinator.cleanup_resources()
