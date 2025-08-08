"""Abstract base class for storage backends."""

from abc import ABC, abstractmethod

from ..models import Artist


class BaseStorage(ABC):
    """Define the abstract interface for storage implementations."""

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the storage backend."""
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        """Close any open connections."""
        raise NotImplementedError

    @abstractmethod
    async def save_artist(self, artist: Artist) -> None:
        """Save a complete artist object to storage."""
        raise NotImplementedError
