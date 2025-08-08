"""Database schema for Melodic."""

V1_TABLES = """
CREATE TABLE IF NOT EXISTS artists (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL CHECK(name <> ''),
    url TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS albums (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL CHECK(title <> ''),
    artist_id INTEGER NOT NULL,
    FOREIGN KEY (artist_id) REFERENCES artists (id)
        ON DELETE CASCADE,
    UNIQUE (artist_id, title)
);

CREATE TABLE IF NOT EXISTS tracks (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL CHECK(title <> ''),
    url TEXT UNIQUE NOT NULL,
    lyrics TEXT,
    album_id INTEGER NOT NULL,
    FOREIGN KEY (album_id) REFERENCES albums (id)
        ON DELETE CASCADE,
    UNIQUE (album_id, title)
);
"""
