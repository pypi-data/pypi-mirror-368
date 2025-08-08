"""A Python client for fetching artist lyrical discographies."""

import logging
import types
from pathlib import Path

from .exceptions import MelodicConfigError

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Melodic:
    """A client for fetching artist lyrical discographies."""

    def __init__(
        self,
        *,
        enable_storage: bool = False,
        storage_path: str | Path | None = None,
        proxies: list[str] | None = None,
    ) -> None:
        """Initialize the Melodic client.

        Args:
            enable_storage: Enable or disable database storage.
            storage_path: The path for the database file. If None and
                enable_storage is True, a default path is used.
            proxies: A list of proxy strings to use for requests.

        Raises:
            MelodicConfigError: If storage_path is provided when enable_storage
                is False.

        """
        # Storage configuration
        if enable_storage:
            pass

        elif storage_path:
            raise MelodicConfigError(
                "storage_path was provided, but enable_storage is False. "
                "Set enable_storage=True to use a custom storage path."
            )

        logger.info("Melodic instance has been initialized.")

    async def __aenter__(self) -> "Melodic":
        """Enter the async context manager and initialize resources."""
        logger.debug("Melodic context entered.")
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None:
        """Exit the async context manager and close resources."""
        logger.debug("Melodic context exited.")

    async def get_discography(self, artist_name: str) -> None:
        """Fetch and process the discography for a given artist.

        Args:
            artist_name: The name of the artist.

        """
        logger.info("Fetching discography for artist: %s", artist_name)
