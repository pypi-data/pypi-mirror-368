#!/usr/bin/env python3
"""Manual test script to verify viewport stability during overlay toggles.

This script helps verify that the 1-pixel shift bug is fixed when toggling
overlays with ctrl-l, ctrl-m, ctrl-t, ctrl-b.

Usage:
    python test_manual_viewport_stability.py samples/pingouins-dustjacket.pdf
"""

import sys
import time
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QTimer, QPointF
from PySide6.QtGui import QKeyEvent

from momovu.views.main_window import MainWindow


def test_viewport_stability():
    """Test that viewport doesn't shift when toggling overlays."""
    app = QApplication(sys.argv)
    
    # Get PDF path from command line or use default
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "samples/pingouins-dustjacket.pdf"
    
    # Create main window with dustjacket document
    window = MainWindow(
        pdf_path=pdf_path,
        book_type="dustjacket",
        show_margins=True,
        show_trim_lines=True,
        show_barcode=True,
        show_fold_lines=True
    )
    window.show()
    
    def log_viewport_position():
        """Log current viewport position for debugging."""
        view = window.graphics_view
        if view:
            h_bar = view.horizontalScrollBar()
            v_bar = view.verticalScrollBar()
            if h_bar and v_bar:
                h_pos = h_bar.value()
                v_pos = v_bar.value()
                
                # Also get the center point in scene coordinates
                center = view.mapToScene(view.viewport().rect().center())
                
                print(f"Viewport position - H: {h_pos}, V: {v_pos}, Center: ({center.x():.2f}, {center.y():.2f})")
                return h_pos, v_pos, center
        return None, None, None
    
    def simulate_toggle_and_check(key, modifier=Qt.KeyboardModifier.ControlModifier):
        """Simulate a key press and check if viewport moved."""
        print(f"\n--- Testing {Qt.Key(key).name} ---")
        
        # Record position before toggle
        h_before, v_before, center_before = log_viewport_position()
        
        # Simulate key press
        event = QKeyEvent(
            QKeyEvent.Type.KeyPress,
            key,
            modifier
        )
        window.graphics_view.keyPressEvent(event)
        
        # Give Qt time to process the event
        QApplication.processEvents()
        time.sleep(0.1)
        
        # Record position after toggle
        h_after, v_after, center_after = log_viewport_position()
        
        # Check if position changed
        if h_before is not None and h_after is not None:
            h_diff = abs(h_after - h_before)
            v_diff = abs(v_after - v_before)
            
            if h_diff > 0 or v_diff > 0:
                print(f"⚠️  VIEWPORT SHIFTED! H: {h_diff}px, V: {v_diff}px")
            else:
                print("✓ Viewport position stable")
                
            # Also check scene coordinates
            if center_before and center_after:
                x_diff = abs(center_after.x() - center_before.x())
                y_diff = abs(center_after.y() - center_before.y())
                if x_diff > 0.1 or y_diff > 0.1:
                    print(f"⚠️  Scene center shifted: X: {x_diff:.2f}, Y: {y_diff:.2f}")
    
    def run_tests():
        """Run all toggle tests after window is ready."""
        print("=== Testing Viewport Stability During Overlay Toggles ===")
        print(f"Document: {pdf_path}")
        
        # Initial position
        print("\nInitial viewport position:")
        log_viewport_position()
        
        # Test each toggle twice (on/off)
        for _ in range(2):
            simulate_toggle_and_check(Qt.Key.Key_L)  # Fold lines
            simulate_toggle_and_check(Qt.Key.Key_M)  # Margins
            simulate_toggle_and_check(Qt.Key.Key_T)  # Trim lines
            simulate_toggle_and_check(Qt.Key.Key_B)  # Barcode
        
        print("\n=== Test Complete ===")
        print("If you saw any '⚠️ VIEWPORT SHIFTED!' messages, the bug is still present.")
        print("Otherwise, the fix is working correctly!")
        
        # Keep window open for manual testing
        print("\nWindow will stay open for manual testing. Press Ctrl+Q to quit.")
    
    # Run tests after window is fully loaded
    QTimer.singleShot(500, run_tests)
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(test_viewport_stability())