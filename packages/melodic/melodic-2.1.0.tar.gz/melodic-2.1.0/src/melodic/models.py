"""Dataclasses for representing music data."""

from dataclasses import dataclass, field


@dataclass
class Track:
    """A music track."""

    title: str
    url: str
    lyrics: str | None = None


@dataclass
class Album:
    """An album, containing a list of tracks."""

    title: str
    tracks: list[Track] = field(default_factory=list)


@dataclass
class Artist:
    """An artist, containing their name, URL, and albums."""

    name: str
    url: str
    albums: list[Album] = field(default_factory=list)
