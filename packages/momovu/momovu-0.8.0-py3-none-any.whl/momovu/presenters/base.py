"""Base presenter class for MVP architecture.

This module provides the foundation for all presenters.
Presenters handle business logic and coordinate between models and views.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Protocol


class IView(Protocol):
    """Interface that all views must implement for presenter interaction."""

    def update_display(self, **kwargs: Any) -> None:
        """Receive property updates from presenter.

        Args:
            **kwargs: Changed properties as key-value pairs
        """
        ...


class BasePresenter(ABC):
    """Base class for all presenters in the MVP architecture.

    This class provides:
    - View reference management
    - Model coordination
    - Common presenter functionality
    """

    def __init__(self, view: Optional[IView] = None) -> None:
        """Initialize the base presenter.

        Args:
            view: Optional view to attach to this presenter
        """
        self._view = view
        self._is_initialized = False

    def attach_view(self, view: IView) -> None:
        """Connect view and trigger initialization if first attachment.

        Args:
            view: View implementing IView protocol
        """
        self._view = view
        if not self._is_initialized:
            self.initialize()
            self._is_initialized = True

    def detach_view(self) -> None:
        """Remove view reference to break circular dependencies."""
        self._view = None

    @property
    def view(self) -> Optional[IView]:
        """Access the currently attached view instance."""
        return self._view

    @property
    def has_view(self) -> bool:
        """Check if presenter has an active view connection."""
        return self._view is not None

    def update_view(self, **kwargs: Any) -> None:
        """Push property changes to attached view if present.

        Args:
            **kwargs: Property updates to send
        """
        if self._view:
            self._view.update_display(**kwargs)

    @abstractmethod
    def initialize(self) -> None:
        """Set up presenter state when first view attaches.

        Subclasses implement this to sync initial model state to view.
        """
        pass

    def cleanup(self) -> None:  # noqa: B027
        """Release resources and remove model observers.

        Subclasses override to disconnect from models and clear state.
        """
