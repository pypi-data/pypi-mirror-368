"""Configuration for Clio SDK"""

from typing import Dict, Optional
import urllib.parse
from .utils import mask_sensitive_data
import warnings


class Config:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.cliomonitoring.com",
        retry_attempts: int = 3,
        raise_on_error: bool = False,
        timeout: int = 30,
        verify_ssl: bool = True,
        debug: bool = False
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.retry_attempts = retry_attempts
        self.raise_on_error = raise_on_error
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.debug = debug

        # Validate configuration
        if not api_key:
            raise ValueError("API key is required")

        if not api_key.startswith("clio_"):
            raise ValueError("Invalid API key format")

        # Validate base_url format
        parsed_url = urllib.parse.urlparse(self.base_url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError(f"Invalid base_url format: {self.base_url}")

        if parsed_url.scheme not in ('http', 'https'):
            raise ValueError(
                f"base_url must use http or https scheme, got: {parsed_url.scheme}")

        # Warn about insecure connections
        if parsed_url.scheme == 'http' and 'localhost' not in parsed_url.netloc and '127.0.0.1' not in parsed_url.netloc:

            warnings.warn(
                "Using HTTP for non-localhost connections is insecure", warnings.SecurityWarning)

    @property
    def headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def __repr__(self):
        """Safe representation that masks sensitive data"""
        masked_key = mask_sensitive_data(self.api_key)
        return f"Config(api_key='{masked_key}', base_url='{self.base_url}', retry_attempts={self.retry_attempts})"
