class SentinelError(Exception):
    """Base exception for Sentinel Client errors."""

    pass


class SentinelAuthError(SentinelError):
    """Authentication failed."""

    pass


class SentinelNetworkError(SentinelError):
    """Network communication failed."""

    pass


class SentinelTimeoutError(SentinelError):
    """Operation timed out."""

    pass


class SentinelDeniedError(SentinelError):
    """Request was denied."""

    pass
