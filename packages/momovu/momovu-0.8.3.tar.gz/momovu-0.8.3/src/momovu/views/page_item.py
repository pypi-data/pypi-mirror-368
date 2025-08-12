"""PDF page item for MVP viewer - renders dynamically based on zoom level."""

import time
from collections import OrderedDict
from typing import Optional

from PySide6.QtCore import QRectF, Qt, QTimer
from PySide6.QtGui import QImage, QPainter
from PySide6.QtPdf import QPdfDocument
from PySide6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget

from momovu.lib.constants import (
    ZOOM_ACTIVE_THRESHOLD,
    ZOOM_BUFFER_FACTOR,
    ZOOM_BUFFER_REDUCTION_MAX,
    ZOOM_BUFFER_REDUCTION_THRESHOLD,
    ZOOM_CACHE_LEVELS,
    ZOOM_CACHE_MAX_ENTRIES,
    ZOOM_CACHE_MAX_MEMORY_MB,
    ZOOM_MAX_DIMENSION,
    ZOOM_MAX_RENDER_PIXELS,
    ZOOM_MAX_USEFUL_SCALE,
    ZOOM_PROGRESSIVE_RENDER_DELAY,
    ZOOM_QUALITY_THRESHOLD,
    ZOOM_SAFE_FALLBACK_SCALE,
)
from momovu.lib.logger import get_logger

logger = get_logger(__name__)


class PageItem(QGraphicsItem):
    """PDF page graphics item that renders dynamically based on zoom level.

    This is a simplified version of PageItem specifically for the MVP viewer.
    It renders the PDF page at the appropriate resolution for the current zoom level.
    """

    # Use constants from config - can be overridden there
    MAX_CACHE_ENTRIES = ZOOM_CACHE_MAX_ENTRIES
    MAX_CACHE_MEMORY_MB = ZOOM_CACHE_MAX_MEMORY_MB
    BUFFER_FACTOR = ZOOM_BUFFER_FACTOR
    CACHE_ZOOM_LEVELS = ZOOM_CACHE_LEVELS
    MAX_USEFUL_SCALE = ZOOM_MAX_USEFUL_SCALE

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

        # Disable Qt's cache since we're doing our own
        self.setCacheMode(QGraphicsItem.CacheMode.NoCache)

        # Cache for rendered regions: (scale, x, y, w, h) -> QImage
        self._render_cache: OrderedDict[
            tuple[float, float, float, float, float], QImage
        ] = OrderedDict()
        self._cache_memory_usage: float = 0.0

        # Progressive rendering state
        self._last_rendered_image: Optional[QImage] = None
        self._last_rendered_rect: Optional[QRectF] = None
        self._is_rendering = False
        self._pending_render_timer: Optional[QTimer] = None
        self._last_paint_time: float = 0.0

    def boundingRect(self) -> QRectF:
        """Define item's scene space boundaries for Qt rendering."""
        return self.bounding_rect

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: Optional[QWidget] = None,
    ) -> None:
        """Render only the visible portion of the PDF page for optimal performance.

        Uses caching and buffer zones for smooth panning experience.
        """
        # Get the visible rectangle in item coordinates
        visible_rect = option.exposedRect  # type: ignore[attr-defined]
        if visible_rect.isEmpty():
            return

        # Get current scale first
        transform = painter.transform()
        scale = max(transform.m11(), transform.m22())

        # Check if we're in presentation mode
        is_presentation = self._is_presentation_mode()

        # For normal viewing (low zoom) or presentation, use original high-quality rendering
        # Threshold is configurable in constants
        if scale <= ZOOM_QUALITY_THRESHOLD or is_presentation:
            # Original full-page rendering for best quality
            self._render_full_page_original(painter, scale)
            return

        # High zoom - use optimized visible-area rendering
        # Snap scale early for cache consistency
        scale = self._snap_to_cache_level(scale)
        # Add buffer around visible area for smooth panning
        # Reduce buffer at high zoom to maintain quality
        buffer_factor = self.BUFFER_FACTOR
        if (
            scale > ZOOM_BUFFER_REDUCTION_THRESHOLD
            and ZOOM_BUFFER_REDUCTION_THRESHOLD > 0
        ):
            # At high zoom, reduce buffer to maintain render quality
            # Protected against division by zero
            buffer_factor = min(
                ZOOM_BUFFER_REDUCTION_MAX,
                self.BUFFER_FACTOR / (scale / ZOOM_BUFFER_REDUCTION_THRESHOLD),
            )

        buffer_width = visible_rect.width() * buffer_factor
        buffer_height = visible_rect.height() * buffer_factor
        render_rect = visible_rect.adjusted(
            -buffer_width, -buffer_height, buffer_width, buffer_height
        )

        # Clamp to page bounds
        render_rect = render_rect.intersected(self.bounding_rect)

        # Check cache - use rect coordinates as key since QRectF isn't hashable
        cache_key = (
            scale,
            render_rect.x(),
            render_rect.y(),
            render_rect.width(),
            render_rect.height(),
        )
        cached_image = self._get_from_cache(cache_key)

        if cached_image:
            # Use cached image with quality hints
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
            painter.drawImage(
                render_rect,
                cached_image,
                QRectF(0, 0, cached_image.width(), cached_image.height()),
            )
            self._last_rendered_image = cached_image
            self._last_rendered_rect = QRectF(render_rect)  # Store a copy
            return

        # Need to render - calculate size
        render_width = int(render_rect.width() * scale)
        render_height = int(render_rect.height() * scale)

        # Check if render size is reasonable
        if render_width * render_height > ZOOM_MAX_RENDER_PIXELS:
            # Don't reduce quality! Instead, render without buffer
            logger.debug(
                f"Render size {render_width}x{render_height} exceeds limit, removing buffer"
            )
            # Just render the visible area without buffer
            render_rect = visible_rect
            render_width = int(render_rect.width() * scale)
            render_height = int(render_rect.height() * scale)

            # If still too large, we need to cap the scale
            if render_width * render_height > ZOOM_MAX_RENDER_PIXELS:
                max_scale = (
                    ZOOM_MAX_RENDER_PIXELS
                    / (render_rect.width() * render_rect.height())
                ) ** 0.5
                scale = min(scale, max_scale)
                render_width = int(render_rect.width() * scale)
                render_height = int(render_rect.height() * scale)
                logger.debug(
                    f"Even without buffer, size too large. Capping scale to {scale:.1f}x"
                )

            # Update cache key for the new rect
            cache_key = (
                scale,
                render_rect.x(),
                render_rect.y(),
                render_rect.width(),
                render_rect.height(),
            )

        # Check if we're actively zooming (multiple paints in quick succession)
        current_time = time.time()
        is_active_zoom = (current_time - self._last_paint_time) < ZOOM_ACTIVE_THRESHOLD
        self._last_paint_time = current_time

        if is_active_zoom and self._last_rendered_image:
            # Store local copy to avoid race condition
            last_rect = self._last_rendered_rect
            try:
                if last_rect and not last_rect.isNull():
                    # Progressive rendering: show stretched previous image immediately
                    source_rect = self._calculate_source_rect(render_rect, last_rect)
                    painter.drawImage(
                        render_rect, self._last_rendered_image, source_rect
                    )
            except (RuntimeError, AttributeError):
                # Rect was deleted or became invalid, skip progressive rendering
                pass

            # Queue high-quality render
            self._queue_high_quality_render(
                render_rect, render_width, render_height, scale, cache_key
            )
        else:
            # Not actively zooming - render normally but cap scale
            actual_scale = min(scale, self.MAX_USEFUL_SCALE)
            if actual_scale < scale:
                # Recalculate dimensions with capped scale
                render_width = int(render_rect.width() * actual_scale)
                render_height = int(render_rect.height() * actual_scale)
                # Update cache key to use actual scale
                cache_key = (
                    actual_scale,
                    render_rect.x(),
                    render_rect.y(),
                    render_rect.width(),
                    render_rect.height(),
                )

            # Render the visible region
            image = self._render_region(
                render_rect, render_width, render_height, actual_scale
            )

            if image and not image.isNull():
                # Cache the result with correct key
                self._add_to_cache(cache_key, image)

                # Draw the image with high quality hints
                painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
                painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
                painter.drawImage(
                    render_rect, image, QRectF(0, 0, image.width(), image.height())
                )

                # Update last rendered for progressive rendering
                self._last_rendered_image = image
                self._last_rendered_rect = QRectF(render_rect)  # Store a copy

                # Queue predictive renders
                self._queue_predictive_renders(render_rect, scale)
            else:
                self._draw_error_placeholder(painter, render_rect)

    def _draw_error_placeholder(self, painter: QPainter, rect: QRectF) -> None:
        """Draw error placeholder when rendering fails."""
        painter.fillRect(rect, Qt.GlobalColor.red)
        painter.setPen(Qt.GlobalColor.white)
        painter.drawText(
            rect,
            Qt.AlignmentFlag.AlignCenter,
            f"Error\nPage {self.page_number + 1}",
        )

    def _render_region(
        self, region: QRectF, width: int, height: int, scale: float
    ) -> Optional[QImage]:
        """Render a specific region of the page.

        Since QPdfDocument doesn't support partial rendering, we render
        the full page and extract the needed region.
        """
        from PySide6.QtCore import QSize

        try:
            # We need to render enough of the page to include our region
            # For now, render the full page (QPdfDocument limitation)
            # In the future, we could optimize by rendering a smaller portion
            full_width = int(self.page_width * scale)
            full_height = int(self.page_height * scale)

            # Safety check - configurable for different systems
            if full_width * full_height > ZOOM_MAX_RENDER_PIXELS:
                # Too large, reduce scale
                max_scale = (
                    ZOOM_MAX_RENDER_PIXELS / (self.page_width * self.page_height)
                ) ** 0.5
                scale = min(scale, max_scale)
                full_width = int(self.page_width * scale)
                full_height = int(self.page_height * scale)
                logger.debug(
                    f"Reduced render scale to {scale:.1f}x to stay within memory limits"
                )

            # Additional safety check for extreme cases
            if full_width > ZOOM_MAX_DIMENSION or full_height > ZOOM_MAX_DIMENSION:
                logger.warning(
                    f"Extreme render size detected: {full_width}x{full_height}"
                )
                # Cap at max dimension
                if full_width > ZOOM_MAX_DIMENSION:
                    scale = scale * (ZOOM_MAX_DIMENSION / full_width)
                    full_width = ZOOM_MAX_DIMENSION
                    full_height = int(self.page_height * scale)
                if full_height > ZOOM_MAX_DIMENSION:
                    scale = scale * (ZOOM_MAX_DIMENSION / full_height)
                    full_height = ZOOM_MAX_DIMENSION
                    full_width = int(self.page_width * scale)

            # Render full page with exception handling
            try:
                full_image = self.document.render(
                    self.page_number, QSize(full_width, full_height)
                )

                if full_image.isNull():
                    raise RuntimeError("Render returned null image")
            except Exception as render_error:
                logger.error(
                    f"PDF render failed at {full_width}x{full_height}: {render_error}"
                )
                # Try one more time at a safe resolution
                if scale > ZOOM_SAFE_FALLBACK_SCALE:
                    safe_scale = ZOOM_SAFE_FALLBACK_SCALE  # Use local variable instead of modifying parameter
                    safe_width = int(self.page_width * safe_scale)
                    safe_height = int(self.page_height * safe_scale)
                    try:
                        full_image = self.document.render(
                            self.page_number, QSize(safe_width, safe_height)
                        )
                        if full_image.isNull():
                            return None
                        # Use safe_scale for extraction calculations
                        source_x = int(region.x() * safe_scale)
                        source_y = int(region.y() * safe_scale)
                        # Recalculate dimensions with safe scale
                        width = int(region.width() * safe_scale)
                        height = int(region.height() * safe_scale)
                        source_rect = QRectF(source_x, source_y, width, height)

                        # Ensure source rect is within image bounds
                        source_rect = source_rect.intersected(
                            QRectF(0, 0, full_image.width(), full_image.height())
                        )

                        # Copy the region
                        return full_image.copy(source_rect.toRect())
                    except Exception:
                        return None
                else:
                    return None

            else:
                # Normal case - extract the region we need
                source_x = int(region.x() * scale)
                source_y = int(region.y() * scale)
                source_rect = QRectF(source_x, source_y, width, height)

                # Ensure source rect is within image bounds
                source_rect = source_rect.intersected(
                    QRectF(0, 0, full_image.width(), full_image.height())
                )

                # Copy the region
                return full_image.copy(source_rect.toRect())

        except (RuntimeError, MemoryError, Exception) as e:
            logger.warning(
                f"Failed to render region at {scale:.1f}x for page {self.page_number + 1}: {e}"
            )

            # Try with reduced scale
            if scale > ZOOM_SAFE_FALLBACK_SCALE:
                try:
                    return self._render_region(
                        region,
                        int(width * ZOOM_SAFE_FALLBACK_SCALE / scale),
                        int(height * ZOOM_SAFE_FALLBACK_SCALE / scale),
                        ZOOM_SAFE_FALLBACK_SCALE,
                    )
                except Exception:
                    logger.error("Even fallback render failed")
                    return None
            return None

    def _get_from_cache(
        self, key: tuple[float, float, float, float, float]
    ) -> Optional[QImage]:
        """Get image from cache if available."""
        if key in self._render_cache:
            # Move to end (LRU)
            self._render_cache.move_to_end(key)
            return self._render_cache[key]
        return None

    def _add_to_cache(
        self, key: tuple[float, float, float, float, float], image: QImage
    ) -> None:
        """Add image to cache with memory management."""
        # Calculate image memory usage (approximate) with overflow protection
        width = min(image.width(), 65536)  # Cap at reasonable max
        height = min(image.height(), 65536)
        bytes_per_pixel = 4
        total_bytes = width * height * bytes_per_pixel
        image_size_mb = total_bytes / (1024.0 * 1024.0)

        # Remove old entries if needed
        while (
            len(self._render_cache) >= self.MAX_CACHE_ENTRIES
            or self._cache_memory_usage + image_size_mb > self.MAX_CACHE_MEMORY_MB
        ):
            if not self._render_cache:
                break
            # Remove oldest
            old_key, old_image = self._render_cache.popitem(last=False)
            old_size_mb = (old_image.width() * old_image.height() * 4) / (
                1024.0 * 1024.0
            )
            self._cache_memory_usage -= old_size_mb

        # Add new entry
        self._render_cache[key] = image
        self._cache_memory_usage += image_size_mb

    def _snap_to_cache_level(self, scale: float) -> float:
        """Snap scale to nearest cache level for better hit rate."""
        if scale <= self.CACHE_ZOOM_LEVELS[0]:
            return self.CACHE_ZOOM_LEVELS[0]
        if scale >= self.CACHE_ZOOM_LEVELS[-1]:
            return self.CACHE_ZOOM_LEVELS[-1]

        # Find nearest level
        for i in range(len(self.CACHE_ZOOM_LEVELS) - 1):
            if self.CACHE_ZOOM_LEVELS[i] <= scale < self.CACHE_ZOOM_LEVELS[i + 1]:
                # Return closer one
                if (scale - self.CACHE_ZOOM_LEVELS[i]) < (
                    self.CACHE_ZOOM_LEVELS[i + 1] - scale
                ):
                    return self.CACHE_ZOOM_LEVELS[i]
                else:
                    return self.CACHE_ZOOM_LEVELS[i + 1]
        return scale

    def _calculate_source_rect(
        self, target_rect: QRectF, source_rect: QRectF
    ) -> QRectF:
        """Calculate source rectangle for progressive rendering stretch."""
        if not self._last_rendered_image:
            return QRectF(0, 0, 1, 1)

        # Protect against division by zero
        if source_rect.width() == 0 or source_rect.height() == 0:
            return QRectF(0, 0, 1, 1)

        # Map target rect to source image coordinates
        scale_x = self._last_rendered_image.width() / source_rect.width()
        scale_y = self._last_rendered_image.height() / source_rect.height()

        # Calculate intersection
        intersect = target_rect.intersected(source_rect)
        if intersect.isEmpty():
            return QRectF(
                0,
                0,
                self._last_rendered_image.width(),
                self._last_rendered_image.height(),
            )

        # Map to source coordinates
        x = (intersect.x() - source_rect.x()) * scale_x
        y = (intersect.y() - source_rect.y()) * scale_y
        w = intersect.width() * scale_x
        h = intersect.height() * scale_y

        return QRectF(x, y, w, h)

    def _queue_high_quality_render(
        self,
        rect: QRectF,
        width: int,
        height: int,
        scale: float,
        cache_key: tuple[float, float, float, float, float],
    ) -> None:
        """Queue a high-quality render after a short delay."""
        # Cancel any pending render
        if self._pending_render_timer:
            self._pending_render_timer.stop()

        # Copy rect values to avoid deletion issues
        rect_copy = QRectF(rect)

        def do_render() -> None:
            # Check if item is still in scene
            if not self.scene():
                return

            self._pending_render_timer = None
            if self._is_rendering:
                return

            self._is_rendering = True
            try:
                # Cap scale for rendering
                actual_scale = min(scale, self.MAX_USEFUL_SCALE)
                # Calculate dimensions with actual scale
                render_width = int(rect_copy.width() * actual_scale)
                render_height = int(rect_copy.height() * actual_scale)

                image = self._render_region(
                    rect_copy, render_width, render_height, actual_scale
                )
                if image and not image.isNull():
                    # Update cache key if scale was capped
                    if actual_scale < scale:
                        cache_key = (
                            actual_scale,
                            rect_copy.x(),
                            rect_copy.y(),
                            rect_copy.width(),
                            rect_copy.height(),
                        )
                    self._add_to_cache(cache_key, image)
                    self._last_rendered_image = image
                    self._last_rendered_rect = QRectF(rect_copy)  # Store a copy
                    # Trigger repaint if item still exists
                    try:
                        self.update(rect_copy)
                    except RuntimeError:
                        # Item was deleted, ignore
                        pass
            finally:
                self._is_rendering = False

        # Cancel any existing timer first
        if self._pending_render_timer:
            self._pending_render_timer.stop()
            self._pending_render_timer.deleteLater()

        # Queue render after configurable delay
        # Store timer reference to ensure cleanup
        timer = QTimer()  # Cannot use self as parent - PageItem is not QObject
        self._pending_render_timer = timer

        # Use a weak reference to avoid circular references
        import weakref

        weak_self = weakref.ref(self)

        def safe_do_render() -> None:
            strong_self = weak_self()
            if strong_self:
                do_render()
            else:
                # Item was deleted, clean up timer
                timer.stop()
                timer.deleteLater()

        timer.timeout.connect(safe_do_render)
        timer.setSingleShot(True)
        timer.start(ZOOM_PROGRESSIVE_RENDER_DELAY)

    def _queue_predictive_renders(self, current_rect: QRectF, scale: float) -> None:
        """Queue predictive renders for likely next views."""
        # For now, just a placeholder - could pre-render adjacent areas
        # or next zoom levels in the future
        pass

    def _is_presentation_mode(self) -> bool:
        """Check if we're in presentation mode.

        The UIStateManager sets is_presentation_mode on the scene when entering/exiting
        presentation mode. We safely check for this attribute.
        """
        scene = self.scene()
        if scene:
            # Use getattr with default to handle case where attribute doesn't exist yet
            return getattr(scene, "is_presentation_mode", False)
        return False

    def _render_full_page_original(self, painter: QPainter, scale: float) -> None:
        """Render full page at original quality (no optimizations)."""
        # Don't snap scale - use exact value for best quality
        render_width = int(self.page_width * scale)
        render_height = int(self.page_height * scale)

        # Add safety limits to prevent crashes in presentation mode
        if render_width * render_height > ZOOM_MAX_RENDER_PIXELS:
            # Need to cap the scale
            max_scale = (
                ZOOM_MAX_RENDER_PIXELS / (self.page_width * self.page_height)
            ) ** 0.5
            scale = min(scale, max_scale)
            render_width = int(self.page_width * scale)
            render_height = int(self.page_height * scale)
            logger.debug(f"Capped full page render to {scale:.1f}x for safety")

        # Also check dimensions
        if render_width > ZOOM_MAX_DIMENSION or render_height > ZOOM_MAX_DIMENSION:
            if render_width > ZOOM_MAX_DIMENSION:
                scale = scale * (ZOOM_MAX_DIMENSION / render_width)
                render_width = ZOOM_MAX_DIMENSION
                render_height = int(self.page_height * scale)
            if render_height > ZOOM_MAX_DIMENSION:
                scale = scale * (ZOOM_MAX_DIMENSION / render_height)
                render_height = ZOOM_MAX_DIMENSION
                render_width = int(self.page_width * scale)

        from PySide6.QtCore import QSize

        try:
            # Render at exact scale
            image = self.document.render(
                self.page_number, QSize(render_width, render_height)
            )

            if image and not image.isNull():
                # Use high-quality scaling
                painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
                painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
                target_rect = QRectF(0, 0, self.page_width, self.page_height)
                painter.drawImage(target_rect, image)
            else:
                self._draw_error_placeholder(painter, self.bounding_rect)

        except (RuntimeError, MemoryError, Exception) as e:
            logger.warning(
                f"Full page render failed at {render_width}x{render_height}: {e}"
            )
            # Try at a safe resolution
            if scale > ZOOM_SAFE_FALLBACK_SCALE:
                try:
                    safe_width = int(self.page_width * ZOOM_SAFE_FALLBACK_SCALE)
                    safe_height = int(self.page_height * ZOOM_SAFE_FALLBACK_SCALE)
                    image = self.document.render(
                        self.page_number, QSize(safe_width, safe_height)
                    )
                    if image and not image.isNull():
                        painter.drawImage(
                            QRectF(0, 0, self.page_width, self.page_height), image
                        )
                    else:
                        self._draw_error_placeholder(painter, self.bounding_rect)
                except Exception:
                    self._draw_error_placeholder(painter, self.bounding_rect)
            else:
                self._draw_error_placeholder(painter, self.bounding_rect)

    def cleanup(self) -> None:
        """Clean up resources when page item is being removed.

        This is called when the scene is cleared or the item is removed.
        Ensures timers are stopped to prevent crashes.
        """
        # Stop any pending render timer and ensure it's deleted
        if self._pending_render_timer:
            try:
                self._pending_render_timer.stop()
                # Disconnect all signals to prevent callbacks
                self._pending_render_timer.timeout.disconnect()
            except Exception:
                pass  # Timer might already be deleted

            try:
                self._pending_render_timer.deleteLater()
            except Exception:
                pass  # Timer might already be deleted

            self._pending_render_timer = None

        # Clear cache to free memory
        self._render_cache.clear()
        self._cache_memory_usage = 0

        # Clear references
        self._last_rendered_image = None
        self._last_rendered_rect = None

        # Clear document reference to help with cleanup
        self.document = None  # type: ignore[assignment]
