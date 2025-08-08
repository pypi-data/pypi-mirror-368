"""SQLite implementation of the storage backend."""

import logging
from contextlib import suppress
from pathlib import Path

import aiosqlite

from ..exceptions import MelodicDatabaseConnectionError, MelodicDatabaseError
from ..models import Album, Artist, Track
from . import schema
from .base import BaseStorage

logger = logging.getLogger(__name__)


class SQLiteStorage(BaseStorage):
    """A SQLite implementation of the storage backend."""

    def __init__(self, db_path: Path) -> None:
        """Initialize the SQLiteStorage.

        Args:
            db_path: The file path for the SQLite database.

        """
        self._db_path = db_path
        self._conn: aiosqlite.Connection | None = None

    async def initialize(self) -> None:
        """Establish connection and initialize the database schema.

        Raises:
            MelodicDatabaseConnectionError: If the connection to the database fails.

        """
        if self._conn:
            return

        logger.debug("Connecting to database at %s.", self._db_path)
        try:
            self._conn = await aiosqlite.connect(self._db_path)
            await self._conn.execute("PRAGMA foreign_keys = ON;")
            await self._conn.execute("PRAGMA synchronous = NORMAL;")
            await self._conn.execute("PRAGMA temp_store = MEMORY;")
            await self._conn.executescript(schema.V1_TABLES)
            await self._conn.commit()

            logger.info("Database connection established and schema verified.")
        except aiosqlite.Error as e:
            raise MelodicDatabaseConnectionError("Failed to connect to database") from e

    async def close(self) -> None:
        """Close the database connection."""
        if self._conn:
            logger.debug("Closing database connection.")
            await self._conn.close()
            self._conn = None
            logger.debug("Database connection closed.")

    async def save_artist(self, artist: Artist) -> None:
        """Insert an artist and their complete discography into the database.

        Args:
            artist: The artist object containing all albums and tracks.

        Raises:
            MelodicDatabaseConnectionError: If there is no active database
                connection.
            MelodicDatabaseError: If the database insertion fails.

        """
        if not self._conn:
            raise MelodicDatabaseConnectionError("No active database connection")

        logger.debug("Attempting to save artist '%s' to database.", artist.name)
        cursor = None
        try:
            cursor = await self._conn.cursor()
            artist_id = await self._insert_artist_record(cursor, artist)

            await self._insert_albums(cursor, artist_id, artist.albums)
            await self._conn.commit()

            logger.info(
                "Successfully saved artist '%s' (ID: %s) to the database.",
                artist.name,
                artist_id,
            )
        except aiosqlite.Error as e:
            if self._conn:
                with suppress(Exception):
                    await self._conn.rollback()
            raise MelodicDatabaseError(f"Error saving artist '{artist.name}'") from e
        finally:
            if cursor:
                await cursor.close()

    async def _insert_artist_record(
        self, cursor: aiosqlite.Cursor, artist: Artist
    ) -> int:
        """Insert an artist record and return its ID.

        Args:
            cursor: The database cursor for the transaction.
            artist: The artist to insert.

        Returns:
            The database ID of the artist.

        Raises:
            MelodicDatabaseError: If the artist ID cannot be retrieved after
                insertion.

        """
        await cursor.execute(
            "INSERT OR IGNORE INTO artists (name, url) VALUES (?, ?)",
            (artist.name, artist.url),
        )
        if cursor.rowcount > 0:
            if cursor.lastrowid is None:
                raise MelodicDatabaseError("Failed to get lastrowid for new artist.")
            return int(cursor.lastrowid)

        await cursor.execute("SELECT id FROM artists WHERE url = ?", (artist.url,))
        result = await cursor.fetchone()
        if not result:
            raise MelodicDatabaseError(f"Could not retrieve ID for '{artist.name}'")
        return int(result[0])

    async def _insert_albums(
        self, cursor: aiosqlite.Cursor, artist_id: int, albums: list[Album]
    ) -> None:
        """Insert all albums for an artist.

        Args:
            cursor: The database cursor for the transaction.
            artist_id: The ID of the artist.
            albums: A list of albums to insert.

        """
        for album in albums:
            album_id = await self._insert_album_record(cursor, artist_id, album)
            await self._insert_tracks(cursor, album_id, album.tracks)

    async def _insert_album_record(
        self, cursor: aiosqlite.Cursor, artist_id: int, album: Album
    ) -> int:
        """Insert an album record and return its ID.

        Args:
            cursor: The database cursor for the transaction.
            artist_id: The ID of the artist for this album.
            album: The album to insert.

        Returns:
            The database ID of the album.

        Raises:
            MelodicDatabaseError: If the album ID cannot be retrieved after
                insertion.

        """
        await cursor.execute(
            "INSERT OR IGNORE INTO albums (artist_id, title) VALUES (?, ?)",
            (artist_id, album.title),
        )
        if cursor.rowcount > 0:
            if cursor.lastrowid is None:
                raise MelodicDatabaseError("Failed to get lastrowid for new album.")
            return int(cursor.lastrowid)

        await cursor.execute(
            "SELECT id FROM albums WHERE artist_id = ? AND title = ?",
            (artist_id, album.title),
        )
        result = await cursor.fetchone()
        if not result:
            raise MelodicDatabaseError(f"Could not retrieve ID for '{album.title}'")
        return int(result[0])

    async def _insert_tracks(
        self, cursor: aiosqlite.Cursor, album_id: int, tracks: list[Track]
    ) -> None:
        """Insert all tracks for an album.

        Args:
            cursor: The database cursor for the transaction.
            album_id: The ID of the album for these tracks.
            tracks: A list of tracks to insert.

        """
        for track in tracks:
            await cursor.execute(
                "INSERT OR IGNORE INTO tracks (album_id, title, url, lyrics) "
                "VALUES (?, ?, ?, ?)",
                (album_id, track.title, track.url, track.lyrics),
            )
