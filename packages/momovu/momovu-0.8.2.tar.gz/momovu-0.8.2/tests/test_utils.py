"""
Test utilities and helpers for momovu test suite.

This module provides:
- Custom assertions for domain-specific testing
- Test data builders and generators
- Mock factories for complex objects
- Performance testing utilities
- Property-based testing helpers
"""

import random
import string
import time
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any, Callable, Optional
from unittest.mock import Mock

from PySide6.QtCore import QRectF, QSizeF
from PySide6.QtWidgets import QGraphicsRectItem


class DataBuilder:
    """Builder pattern for creating test data with fluent interface.

    Note: Renamed from TestDataBuilder to DataBuilder to avoid pytest collection warning.
    """

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> "DataBuilder":
        """Reset builder to initial state."""
        self._data: dict[str, Any] = {}
        return self

    def with_page_size(self, width: float, height: float) -> "DataBuilder":
        """Add page size to test data."""
        self._data["page_size"] = QSizeF(width, height)
        return self

    def with_margin(self, margin_mm: float) -> "DataBuilder":
        """Add margin value to test data."""
        self._data["margin_mm"] = margin_mm
        self._data["margin_points"] = margin_mm * 72.0 / 25.4
        return self

    def with_spine_dimensions(
        self,
        width: float,
        flap_width: Optional[float] = None,
        flap_height: Optional[float] = None,
    ) -> "DataBuilder":
        """Add spine dimensions to test data."""
        self._data["spine_width"] = width
        if flap_width is not None:
            self._data["flap_width"] = flap_width
        if flap_height is not None:
            self._data["flap_height"] = flap_height
        return self

    def with_random_page_count(
        self, min_pages: int = 1, max_pages: int = 1000
    ) -> "DataBuilder":
        """Add random page count to test data."""
        self._data["page_count"] = random.randint(min_pages, max_pages)
        return self

    def build(self) -> dict[str, Any]:
        """Build and return the test data."""
        return self._data.copy()


class MockFactory:
    """Factory for creating sophisticated mock objects."""

    @staticmethod
    def create_document_mock(
        page_count: int = 3, page_width: float = 612.0, page_height: float = 792.0
    ) -> Mock:
        """Create a realistic document mock."""
        document = Mock()
        document.load.return_value = True
        document.pageCount.return_value = page_count

        # Create consistent page sizes
        page_size_mock = Mock()
        page_size_mock.width.return_value = page_width
        page_size_mock.height.return_value = page_height
        document.pagePointSize.return_value = page_size_mock

        return document

    @staticmethod
    def create_graphics_item_mock() -> Mock:
        """Create a mock QGraphicsRectItem with all expected methods."""
        item = Mock(spec=QGraphicsRectItem)
        item.setRect = Mock()
        item.setPos = Mock()
        item.show = Mock()
        item.hide = Mock()
        item.setBrush = Mock()
        item.setOpacity = Mock()
        item.setPen = Mock()
        item.boundingRect.return_value = QRectF(0, 0, 100, 100)
        return item

    @staticmethod
    def create_scene_mock() -> Mock:
        """Create a mock QGraphicsScene."""
        scene = Mock()
        scene.addItem = Mock()
        scene.removeItem = Mock()
        scene.itemsBoundingRect.return_value = QRectF(0, 0, 612, 792)
        scene.sceneRect.return_value = QRectF(0, 0, 612, 792)
        scene.setSceneRect = Mock()
        return scene

    @staticmethod
    def create_viewer_mock_with_managers() -> Mock:
        """Create a comprehensive viewer mock with all managers."""
        viewer = Mock()

        # Document setup
        viewer.document = MockFactory.create_document_mock()

        # Scene and view setup
        viewer.scene = MockFactory.create_scene_mock()
        viewer.view = Mock()
        viewer.view.viewport.return_value = Mock()
        viewer.view.viewport.return_value.rect.return_value = Mock()
        viewer.view.mapToScene.return_value = Mock()
        viewer.view.mapToScene.return_value.boundingRect.return_value = Mock()
        viewer.view.mapToScene.return_value.boundingRect.return_value.center.return_value = (
            Mock()
        )
        viewer.view.mapToScene.return_value.boundingRect.return_value.center.return_value.y.return_value = (
            0
        )

        # Manager setup
        viewer.page_manager = Mock()
        viewer.margin_manager = Mock()
        viewer.presentation_manager = Mock()
        viewer.spine_manager = Mock()

        # Properties
        viewer.num_pages = 100
        viewer.safety_margin_mm = 12.7
        viewer.safety_margin = 36.0
        viewer.spine_width = None
        viewer.flap_width = None
        viewer.flap_height = None

        # Item containers
        viewer.spine_items = []
        viewer.spine_margin_items = []
        viewer.barcode_items = []
        viewer.flap_items = []
        viewer.flap_margin_items = []

        # Methods
        viewer.set_safety_margins = Mock()
        viewer.set_spine_dimensions = Mock()
        viewer.clear_viewer_items = Mock()
        viewer.hide_all_flap_items = Mock()
        viewer.show_flap_items_for_page = Mock()
        viewer.add_item_to_scene = Mock()
        viewer.remove_item_from_scene = Mock()

        return viewer


class PropertyBasedTestHelper:
    """Helper for property-based testing."""

    @staticmethod
    def generate_page_sizes(count: int = 10) -> list[QSizeF]:
        """Generate random but realistic page sizes."""
        common_sizes = [
            (612.0, 792.0),  # US Letter
            (595.0, 842.0),  # A4
            (420.0, 595.0),  # A5
            (297.0, 420.0),  # A6
            (612.0, 1008.0),  # US Legal
        ]

        sizes = []
        for _ in range(count):
            if random.random() < 0.7:  # 70% chance of common size
                width, height = random.choice(common_sizes)
            else:  # 30% chance of random size
                width = random.uniform(200.0, 1000.0)
                height = random.uniform(200.0, 1400.0)
            sizes.append(QSizeF(width, height))

        return sizes

    @staticmethod
    def generate_margin_values(count: int = 10) -> list[float]:
        """Generate realistic margin values in mm."""
        common_margins = [6.35, 12.7, 19.05, 25.4]  # 1/4", 1/2", 3/4", 1"

        margins = []
        for _ in range(count):
            if random.random() < 0.6:  # 60% chance of common margin
                margin = random.choice(common_margins)
            else:  # 40% chance of random margin
                margin = random.uniform(3.0, 50.0)
            margins.append(margin)

        return margins

    @staticmethod
    def generate_rectangles(count: int = 10, max_size: float = 1000.0) -> list[QRectF]:
        """Generate random rectangles for testing."""
        rectangles = []
        for _ in range(count):
            x = random.uniform(0, max_size / 2)
            y = random.uniform(0, max_size / 2)
            width = random.uniform(10, max_size / 2)
            height = random.uniform(10, max_size / 2)
            rectangles.append(QRectF(x, y, width, height))

        return rectangles


class CustomAssertions:
    """Custom assertions for domain-specific testing."""

    @staticmethod
    def assert_rectangles_equal(
        actual: QRectF, expected: QRectF, tolerance: float = 0.01
    ) -> None:
        """Assert that two rectangles are equal within tolerance."""
        assert (
            abs(actual.x() - expected.x()) < tolerance
        ), f"X coordinates differ: {actual.x()} vs {expected.x()}"
        assert (
            abs(actual.y() - expected.y()) < tolerance
        ), f"Y coordinates differ: {actual.y()} vs {expected.y()}"
        assert (
            abs(actual.width() - expected.width()) < tolerance
        ), f"Widths differ: {actual.width()} vs {expected.width()}"
        assert (
            abs(actual.height() - expected.height()) < tolerance
        ), f"Heights differ: {actual.height()} vs {expected.height()}"

    @staticmethod
    def assert_margin_conversion_accurate(
        mm_value: float, points_value: float, tolerance: float = 0.01
    ) -> None:
        """Assert that mm to points conversion is accurate."""
        expected_points = mm_value * 72.0 / 25.4
        assert (
            abs(points_value - expected_points) < tolerance
        ), f"Conversion inaccurate: {mm_value}mm should be {expected_points:.2f}pt, got {points_value:.2f}pt"

    @staticmethod
    def assert_mock_called_with_rect(
        mock_call: Any, expected_rect: QRectF, tolerance: float = 0.01
    ) -> None:
        """Assert that a mock was called with a rectangle argument."""
        args, kwargs = mock_call
        assert len(args) > 0, "Mock was not called with any arguments"
        actual_rect = args[0]
        assert isinstance(
            actual_rect, QRectF
        ), f"Expected QRectF, got {type(actual_rect)}"
        CustomAssertions.assert_rectangles_equal(actual_rect, expected_rect, tolerance)

    @staticmethod
    def assert_all_items_hidden(items: list[Mock]) -> None:
        """Assert that all items in the list have hide() called."""
        for i, item in enumerate(items):
            item.hide.assert_called_once(), f"Item {i} was not hidden"

    @staticmethod
    def assert_all_items_shown(items: list[Mock]) -> None:
        """Assert that all items in the list have show() called."""
        for i, item in enumerate(items):
            item.show.assert_called_once(), f"Item {i} was not shown"

    @staticmethod
    def assert_items_positioned_correctly(
        items: list[Mock], expected_positions: list[tuple[float, float]]
    ) -> None:
        """Assert that items are positioned at expected coordinates."""
        assert len(items) == len(
            expected_positions
        ), f"Item count mismatch: {len(items)} items, {len(expected_positions)} positions"

        for i, (item, (x, y)) in enumerate(zip(items, expected_positions)):
            item.setPos.assert_called_with(
                x, y
            ), f"Item {i} not positioned at ({x}, {y})"


class PerformanceTestHelper:
    """Helper for performance testing."""

    @staticmethod
    @contextmanager
    def measure_time() -> Generator[Callable[[], float], None, None]:
        """Context manager to measure execution time."""
        start_time = time.time()
        yield lambda: time.time() - start_time
        # Time measurement is available via the yielded function

    @staticmethod
    def assert_performance_within_limit(
        operation: Callable[..., Any], max_time: float, *args: Any, **kwargs: Any
    ) -> Any:
        """Assert that an operation completes within a time limit."""
        start_time = time.time()
        result = operation(*args, **kwargs)
        elapsed_time = time.time() - start_time

        assert (
            elapsed_time < max_time
        ), f"Operation took {elapsed_time:.3f}s, expected < {max_time:.3f}s"

        return result

    @staticmethod
    def benchmark_operation(
        operation: Callable[..., Any], iterations: int = 100, *args: Any, **kwargs: Any
    ) -> dict[str, float]:
        """Benchmark an operation and return timing statistics."""
        times = []

        for _ in range(iterations):
            start_time = time.time()
            operation(*args, **kwargs)
            elapsed_time = time.time() - start_time
            times.append(elapsed_time)

        return {
            "min_time": min(times),
            "max_time": max(times),
            "avg_time": sum(times) / len(times),
            "total_time": sum(times),
            "iterations": iterations,
        }


class TestScenarioGenerator:
    """Generator for complex test scenarios."""

    @staticmethod
    def generate_margin_test_scenarios() -> list[dict[str, Any]]:
        """Generate comprehensive margin test scenarios."""
        scenarios = []

        # Basic scenarios
        scenarios.extend(
            [
                {
                    "name": "standard_letter_page",
                    "page_size": QSizeF(612.0, 792.0),
                    "margin_mm": 12.7,
                    "spine_width": None,
                    "expected_margin_count": 4,
                },
                {
                    "name": "a4_page_with_spine",
                    "page_size": QSizeF(595.0, 842.0),
                    "margin_mm": 15.0,
                    "spine_width": 10.0,
                    "expected_margin_count": 6,
                },
                {
                    "name": "dustjacket_with_flaps",
                    "page_size": QSizeF(612.0, 792.0),
                    "margin_mm": 12.7,
                    "spine_width": 8.0,
                    "flap_width": 75.0,
                    "flap_height": 792.0,
                    "expected_margin_count": 10,
                },
            ]
        )

        # Edge case scenarios
        scenarios.extend(
            [
                {
                    "name": "minimal_page_size",
                    "page_size": QSizeF(100.0, 100.0),
                    "margin_mm": 5.0,
                    "spine_width": None,
                    "expected_margin_count": 4,
                },
                {
                    "name": "zero_margin",
                    "page_size": QSizeF(612.0, 792.0),
                    "margin_mm": 0.0,
                    "spine_width": None,
                    "expected_margin_count": 4,
                },
                {
                    "name": "large_margin",
                    "page_size": QSizeF(612.0, 792.0),
                    "margin_mm": 100.0,
                    "spine_width": None,
                    "expected_margin_count": 4,
                },
            ]
        )

        return scenarios

    @staticmethod
    def generate_presentation_test_scenarios() -> list[dict[str, Any]]:
        """Generate presentation mode test scenarios."""
        return [
            {
                "name": "single_page_document",
                "page_count": 1,
                "initial_page": 0,
                "navigation_sequence": [],
                "expected_final_page": 0,
            },
            {
                "name": "multi_page_forward_navigation",
                "page_count": 5,
                "initial_page": 0,
                "navigation_sequence": ["next", "next", "next"],
                "expected_final_page": 3,
            },
            {
                "name": "multi_page_backward_navigation",
                "page_count": 5,
                "initial_page": 4,
                "navigation_sequence": ["previous", "previous"],
                "expected_final_page": 2,
            },
            {
                "name": "boundary_navigation_forward",
                "page_count": 3,
                "initial_page": 2,
                "navigation_sequence": ["next", "next"],  # Should stay at page 2
                "expected_final_page": 2,
            },
            {
                "name": "boundary_navigation_backward",
                "page_count": 3,
                "initial_page": 0,
                "navigation_sequence": [
                    "previous",
                    "previous",
                ],  # Should stay at page 0
                "expected_final_page": 0,
            },
        ]


def create_test_pdf_content() -> bytes:
    """Create minimal valid PDF content for testing."""
    return (
        b"%PDF-1.4\n"
        b"1 0 obj\n"
        b"<< /Type /Catalog /Pages 2 0 R >>\n"
        b"endobj\n"
        b"2 0 obj\n"
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>\n"
        b"endobj\n"
        b"3 0 obj\n"
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\n"
        b"endobj\n"
        b"xref\n"
        b"0 4\n"
        b"0000000000 65535 f \n"
        b"0000000010 00000 n \n"
        b"0000000053 00000 n \n"
        b"0000000100 00000 n \n"
        b"trailer\n"
        b"<< /Size 4 /Root 1 0 R >>\n"
        b"startxref\n"
        b"149\n"
        b"%%EOF"
    )


def generate_random_string(length: int = 10) -> str:
    """Generate a random string for testing."""
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


# Decorators for test categorization and setup
def requires_qt(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to mark tests that require Qt components."""
    func._requires_qt = True  # type: ignore[attr-defined]
    return func


def slow_test(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to mark slow tests."""
    func._slow_test = True  # type: ignore[attr-defined]
    return func


def integration_test(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to mark integration tests."""
    func._integration_test = True  # type: ignore[attr-defined]
    return func
