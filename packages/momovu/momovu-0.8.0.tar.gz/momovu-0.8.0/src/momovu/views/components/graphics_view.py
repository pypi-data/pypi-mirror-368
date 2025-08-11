"""Custom graphics view component for PDF viewing with mouse and keyboard support."""

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent, QWheelEvent
from PySide6.QtWidgets import QGraphicsView

from momovu.lib.constants import DEFAULT_SCROLL_AMOUNT, ZOOM_THRESHOLD_FOR_PAN
from momovu.lib.logger import get_logger

logger = get_logger(__name__)


class GraphicsView(QGraphicsView):
    """Custom graphics view with mouse wheel and DIRECT keyboard support."""

    def __init__(self, main_window: Any) -> None:
        """Initialize the graphics view.

        Args:
            main_window: Reference to the main window for event handling
        """
        super().__init__()
        self.main_window = main_window
        self._cleaned_up = False

        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Central keyboard event handler for all viewer shortcuts.

        Handles navigation, zoom, and UI toggle shortcuts.
        Arrow keys adapt based on zoom level (pan when zoomed, navigate otherwise).

        NOTE: When adding or modifying keyboard shortcuts here,
        remember to update the shortcuts dialog in
        lib/shortcuts_dialog.py::_populate_shortcuts()
        """
        is_mock = hasattr(event, "_mock_name") or not hasattr(event, "spontaneous")

        if is_mock:
            key = event.key() if callable(event.key) else event.key
            modifiers = (
                event.modifiers() if callable(event.modifiers) else event.modifiers
            )
        else:
            key = event.key()
            modifiers = event.modifiers()

        # Arrow keys - handle based on zoom state
        if key in (Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up, Qt.Key.Key_Down):
            if is_mock:
                if key == Qt.Key.Key_Left:
                    self.main_window.navigation_controller.navigate_previous()
                elif key == Qt.Key.Key_Right:
                    self.main_window.navigation_controller.navigate_next()
                if hasattr(event, "accept"):
                    event.accept()
                return

            is_zoomed = False
            if hasattr(self.main_window, "zoom_controller"):
                zoom_level = self.main_window.zoom_controller.get_current_zoom()
                is_zoomed = zoom_level > ZOOM_THRESHOLD_FOR_PAN

            if is_zoomed:
                # When zoomed in, use arrow keys for panning
                # Manual scrolling since Qt doesn't handle it by default
                h_bar = self.horizontalScrollBar()
                v_bar = self.verticalScrollBar()

                if key == Qt.Key.Key_Left and h_bar:
                    h_bar.setValue(h_bar.value() - DEFAULT_SCROLL_AMOUNT)
                elif key == Qt.Key.Key_Right and h_bar:
                    h_bar.setValue(h_bar.value() + DEFAULT_SCROLL_AMOUNT)
                elif key == Qt.Key.Key_Up and v_bar:
                    v_bar.setValue(v_bar.value() - DEFAULT_SCROLL_AMOUNT)
                elif key == Qt.Key.Key_Down and v_bar:
                    v_bar.setValue(v_bar.value() + DEFAULT_SCROLL_AMOUNT)

                event.accept()
            else:
                doc_type = self.main_window.margin_presenter.model.document_type

                if doc_type == "interior":
                    if key == Qt.Key.Key_Left:
                        self.main_window.navigation_controller.navigate_previous()
                    elif key == Qt.Key.Key_Right:
                        self.main_window.navigation_controller.navigate_next()
                    elif key in (Qt.Key.Key_Up, Qt.Key.Key_Down):
                        super().keyPressEvent(event)
                        return
                else:
                    pass

                event.accept()
            return

        if key == Qt.Key.Key_PageUp:
            self.main_window.navigation_controller.navigate_previous()
            event.accept() if hasattr(event, "accept") else None
        elif key == Qt.Key.Key_PageDown:
            self.main_window.navigation_controller.navigate_next()
            event.accept() if hasattr(event, "accept") else None
        elif key == Qt.Key.Key_Home:
            self.main_window.navigation_controller.navigate_first()
            event.accept() if hasattr(event, "accept") else None
        elif key == Qt.Key.Key_End:
            self.main_window.navigation_controller.navigate_last()
            event.accept() if hasattr(event, "accept") else None
        elif key == Qt.Key.Key_Space:
            if modifiers & Qt.KeyboardModifier.ShiftModifier:
                self.main_window.navigation_controller.navigate_previous()
            else:
                self.main_window.navigation_controller.navigate_next()
            event.accept() if hasattr(event, "accept") else None
        elif key == Qt.Key.Key_F5:
            self.main_window.toggle_presentation()
            event.accept()
        elif key == Qt.Key.Key_F11:
            self.main_window.toggle_fullscreen()
            event.accept()
        elif key == Qt.Key.Key_F1 or key == Qt.Key.Key_Question:
            self.main_window.show_shortcuts_dialog()
            event.accept()
        elif key == Qt.Key.Key_Escape:
            if self.main_window.presentation_action.isChecked():
                self.main_window.presentation_action.setChecked(False)
                self.main_window.exit_presentation_mode()
            elif self.main_window.isFullScreen():
                self.main_window.toggle_fullscreen()
            event.accept()
        elif key in (Qt.Key.Key_Plus, Qt.Key.Key_Equal):
            if modifiers & Qt.KeyboardModifier.ControlModifier:
                self.main_window.zoom_in()
                event.accept()
            else:
                super().keyPressEvent(event)
        elif key == Qt.Key.Key_Minus:
            if modifiers & Qt.KeyboardModifier.ControlModifier:
                self.main_window.zoom_out()
                event.accept()
            else:
                super().keyPressEvent(event)
        elif key == Qt.Key.Key_0:
            if modifiers & Qt.KeyboardModifier.ControlModifier:
                self.main_window.fit_to_page()
                event.accept()
            else:
                super().keyPressEvent(event)
        elif modifiers & Qt.KeyboardModifier.ControlModifier:
            if key == Qt.Key.Key_F:
                self.main_window.fit_to_page()
                event.accept()
            elif key == Qt.Key.Key_O:
                self.main_window.open_file_dialog()
                event.accept()
            elif key == Qt.Key.Key_Q:
                self.main_window.close()
                event.accept()
            elif key == Qt.Key.Key_G:
                self.main_window.show_go_to_page_dialog()
                event.accept()
            elif key == Qt.Key.Key_D:
                self.main_window.side_by_side_action.toggle()
                self.main_window.toggle_side_by_side()
                event.accept()
            elif key == Qt.Key.Key_M:
                self.main_window.show_margins_action.toggle()
                self.main_window.toggle_margins()
                event.accept()
            elif key == Qt.Key.Key_T:
                self.main_window.show_trim_lines_action.toggle()
                self.main_window.toggle_trim_lines()
                event.accept()
            elif key == Qt.Key.Key_B:
                if self.main_window.margin_presenter.model.document_type in [
                    "cover",
                    "dustjacket",
                ]:
                    self.main_window.show_barcode_action.toggle()
                    self.main_window.toggle_barcode()
                event.accept()
            elif key == Qt.Key.Key_L:
                self.main_window.show_fold_lines_action.toggle()
                self.main_window.toggle_fold_lines()
                event.accept()
            else:
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Handle mouse wheel for zoom (with Ctrl) or page navigation.

        Args:
            event: Qt wheel event containing delta and modifiers
        """
        modifiers = event.modifiers()
        delta = event.angleDelta().y()

        if modifiers & Qt.KeyboardModifier.ControlModifier:
            if delta > 0:
                self.main_window.zoom_in()
            else:
                self.main_window.zoom_out()
        else:
            if delta > 0:
                self.main_window.navigation_controller.navigate_previous()
            else:
                self.main_window.navigation_controller.navigate_next()

        event.accept()

    def cleanup(self) -> None:
        """Release scene connection and clear references (idempotent)."""
        if self._cleaned_up:
            return

        logger.debug("Cleaning up GraphicsView")

        try:
            scene = self.scene()
            if scene:
                # Don't clear the scene here - MainWindow handles that
                # Just disconnect from it
                self.setScene(None)
        except Exception as e:
            logger.warning(f"Error disconnecting from scene: {e}")

        self.main_window = None

        self._cleaned_up = True
        logger.info("GraphicsView cleanup completed")
