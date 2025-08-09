"""
Clio - Playwright Automation Monitoring SDK

Simple SDK for monitoring Playwright test executions with automatic video and trace uploads.
"""

from .client import ClioMonitor
from .exceptions import ClioError, ClioAuthError, ClioUploadError

__version__ = "0.1.8"
__all__ = ["ClioMonitor", "ClioError", "ClioAuthError", "ClioUploadError"]