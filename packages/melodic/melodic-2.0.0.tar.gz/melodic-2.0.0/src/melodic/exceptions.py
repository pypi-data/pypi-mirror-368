"""Custom exceptions for the Melodic library."""


class MelodicError(Exception):
    """A base exception for all library specific errors."""


class MelodicConfigError(MelodicError):
    """An exception for configuration related errors."""
