"""Simple configuration for Momovu.

This module provides configuration settings for the Momovu application.
"""

from dataclasses import dataclass

from momovu.lib import constants as const


@dataclass
class Config:
    """Application configuration."""

    window_width: int = const.DEFAULT_WINDOW_WIDTH
    window_height: int = const.DEFAULT_WINDOW_HEIGHT
    image_cache_size: int = const.DEFAULT_IMAGE_CACHE_SIZE
    safety_margin_mm: float = const.DEFAULT_SAFETY_MARGIN_MM
    zoom_factor: float = const.ZOOM_IN_FACTOR


config = Config()
