"""Custom exceptions for Clio SDK"""


class ClioError(Exception):
    """Base exception for all Clio errors"""
    pass


class ClioAuthError(ClioError):
    """Raised when authentication fails"""
    pass


class ClioUploadError(ClioError):
    """Raised when file upload fails"""
    pass


class ClioRateLimitError(ClioError):
    """Raised when rate limit is exceeded"""
    pass


class ClioConfigError(ClioError):
    """Raised when configuration is invalid"""
    pass