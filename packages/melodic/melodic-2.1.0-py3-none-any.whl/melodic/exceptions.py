"""Custom exceptions for the Melodic library."""


class MelodicError(Exception):
    """A base exception for all library specific errors."""


class MelodicConfigError(MelodicError):
    """An exception for configuration related errors."""


class MelodicDatabaseError(MelodicError):
    """An exception for general database errors."""


class MelodicDatabaseConnectionError(MelodicDatabaseError):
    """An exception for database connection specific errors."""
