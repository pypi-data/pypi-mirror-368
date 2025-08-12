"""Comprehensive tests for config module."""

from dataclasses import fields
from typing import Any

import pytest

from momovu.lib import constants as const
from momovu.lib.config import Config, config


class TestConfig:
    """Test Config dataclass."""

    def test_config_default_values(self) -> None:
        """Test that Config initializes with correct default values."""
        c = Config()

        # Test window settings
        assert c.window_width == const.DEFAULT_WINDOW_WIDTH
        assert c.window_height == const.DEFAULT_WINDOW_HEIGHT

        # Test cache settings
        assert c.image_cache_size == const.DEFAULT_IMAGE_CACHE_SIZE

        # Test margin settings
        assert c.safety_margin_mm == const.DEFAULT_SAFETY_MARGIN_MM

        # Test UI settings
        assert c.zoom_factor == const.ZOOM_IN_FACTOR

    def test_config_custom_values(self) -> None:
        """Test that Config can be initialized with custom values."""
        custom_config = Config(
            window_width=1920,
            window_height=1080,
            image_cache_size=200,
            safety_margin_mm=20.0,
            zoom_factor=1.5,
        )

        assert custom_config.window_width == 1920
        assert custom_config.window_height == 1080
        assert custom_config.image_cache_size == 200
        assert custom_config.safety_margin_mm == 20.0
        assert custom_config.zoom_factor == 1.5

    def test_config_is_dataclass(self) -> None:
        """Test that Config is a proper dataclass."""
        # Check that it has dataclass fields
        field_names = {f.name for f in fields(Config)}
        expected_fields = {
            "window_width",
            "window_height",
            "image_cache_size",
            "safety_margin_mm",
            "zoom_factor",
        }
        assert field_names == expected_fields

    def test_config_field_types(self) -> None:
        """Test that Config fields have correct types."""
        field_types = {f.name: f.type for f in fields(Config)}

        assert field_types["window_width"] is int
        assert field_types["window_height"] is int
        assert field_types["image_cache_size"] is int
        assert field_types["safety_margin_mm"] is float
        assert field_types["zoom_factor"] is float

    def test_global_config_instance(self) -> None:
        """Test that global config instance exists and has correct type."""
        assert isinstance(config, Config)

        # Test that it has default values
        assert config.window_width == const.DEFAULT_WINDOW_WIDTH
        assert config.window_height == const.DEFAULT_WINDOW_HEIGHT
        assert config.image_cache_size == const.DEFAULT_IMAGE_CACHE_SIZE
        assert config.safety_margin_mm == const.DEFAULT_SAFETY_MARGIN_MM
        assert config.zoom_factor == const.ZOOM_IN_FACTOR

    def test_config_equality(self) -> None:
        """Test Config equality comparison."""
        config1 = Config()
        config2 = Config()
        config3 = Config(window_width=1920)

        assert config1 == config2
        assert config1 != config3

    def test_config_repr(self) -> None:
        """Test Config string representation."""
        c = Config(window_width=1920, window_height=1080)
        repr_str = repr(c)

        # Check that repr contains class name and key values
        assert "Config" in repr_str
        assert "window_width=1920" in repr_str
        assert "window_height=1080" in repr_str

    @pytest.mark.parametrize(
        "field_name,value",
        [
            ("window_width", 1920),
            ("window_height", 1080),
            ("image_cache_size", 200),
            ("safety_margin_mm", 20.0),
            ("zoom_factor", 1.5),
        ],
    )
    def test_config_field_assignment(self, field_name: Any, value: Any) -> None:
        """Test that Config fields can be assigned after initialization."""
        c = Config()
        setattr(c, field_name, value)
        assert getattr(c, field_name) == value

    def test_config_immutability_not_enforced(self) -> None:
        """Test that Config is mutable (not frozen)."""
        c = Config()
        # This should not raise an error
        c.window_width = 1920
        assert c.window_width == 1920

    def test_config_copy(self) -> None:
        """Test creating a copy of Config."""
        import copy

        original = Config(window_width=1920)
        copied = copy.copy(original)

        assert copied == original
        assert copied is not original

        # Modify copy shouldn't affect original
        copied.window_width = 1280
        assert original.window_width == 1920
        assert copied.window_width == 1280
