"""Keyboard shortcuts dialog for Momovu.

This module provides a dialog that displays all available keyboard shortcuts
to help users learn and use the application more efficiently.
"""

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from momovu.lib.constants import (
    SHORTCUTS_DIALOG_HEIGHT,
    SHORTCUTS_DIALOG_WIDTH,
    SHORTCUTS_TABLE_COLUMNS,
)


class ShortcutsDialog(QDialog):
    """Dialog displaying all keyboard shortcuts."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the shortcuts dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Keyboard Shortcuts")
        self.setModal(True)
        self.resize(SHORTCUTS_DIALOG_WIDTH, SHORTCUTS_DIALOG_HEIGHT)

        self._setup_ui()
        self._populate_shortcuts()

    def _setup_ui(self) -> None:
        """Build table widget with category/action/shortcut columns."""
        layout = QVBoxLayout(self)

        # Title label
        title = QLabel("Keyboard Shortcuts")
        title.setStyleSheet("font-size: 14pt; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        # Shortcuts table
        self.table = QTableWidget()
        self.table.setColumnCount(SHORTCUTS_TABLE_COLUMNS)
        self.table.setHorizontalHeaderLabels(["Category", "Action", "Shortcut"])
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        # Hide row numbers (vertical header)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)

    def _populate_shortcuts(self) -> None:
        """Fill table with all available keyboard shortcuts.

        NOTE: Keep this list synchronized with keyboard handling in
        views/components/graphics_view.py::keyPressEvent()
        """
        shortcuts = [
            # File operations
            ("File", "Open Document", "Ctrl+O"),
            ("File", "Exit Application", "Ctrl+Q"),
            # Navigation
            ("Navigation", "Next Page", "Page Down"),
            ("Navigation", "Next Page (alternative)", "Space"),
            ("Navigation", "Previous Page", "Page Up"),
            ("Navigation", "Previous Page (alternative)", "Shift+Space"),
            ("Navigation", "First Page", "Home"),
            ("Navigation", "Last Page", "End"),
            ("Navigation", "Go to Page", "Ctrl+G"),
            ("Navigation", "Navigate with Arrow Keys", ""),
            ("Navigation", "  • When zoomed", "Arrow Keys = Pan document"),
            (
                "Navigation",
                "  • Interior (not zoomed)",
                "Left/Right = Previous/Next page",
            ),
            ("Navigation", "  • Cover/Dustjacket", "Arrow Keys = No action"),
            ("Navigation", "Navigate Pages", "Mouse Wheel"),
            # View modes
            ("View", "Fullscreen", "F11"),
            ("View", "Presentation Mode", "F5"),
            ("View", "Exit Presentation/Fullscreen", "Escape"),
            ("View", "Side by Side View", "Ctrl+D"),
            # Display options
            ("Display", "Show/Hide Margins", "Ctrl+M"),
            ("Display", "Show/Hide Trim Lines", "Ctrl+T"),
            ("Display", "Show/Hide Barcode", "Ctrl+B (Cover/Dustjacket only)"),
            ("Display", "Show/Hide Fold Lines", "Ctrl+L"),
            # Zoom
            ("Zoom", "Zoom In", "Ctrl+Plus / Ctrl+="),
            ("Zoom", "Zoom Out", "Ctrl+Minus"),
            ("Zoom", "Fit to Page", "Ctrl+0"),
            ("Zoom", "Fit to Page (alternative)", "Ctrl+F"),
            ("Zoom", "Zoom with Mouse", "Ctrl+Mouse Wheel"),
            # Help
            ("Help", "Show Keyboard Shortcuts", "F1 / ?"),
            ("Help", "About", ""),
        ]

        self.table.setRowCount(len(shortcuts))

        for row, (category, action, shortcut) in enumerate(shortcuts):
            # Category column
            category_item = QTableWidgetItem(category)
            category_item.setTextAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            )
            self.table.setItem(row, 0, category_item)

            # Action column
            action_item = QTableWidgetItem(action)
            action_item.setTextAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            )
            self.table.setItem(row, 1, action_item)

            # Shortcut column
            shortcut_item = QTableWidgetItem(shortcut)
            shortcut_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            # Make shortcut text bold
            font = shortcut_item.font()
            font.setBold(True)
            shortcut_item.setFont(font)
            self.table.setItem(row, 2, shortcut_item)

        # Adjust row heights for better readability
        self.table.resizeRowsToContents()
