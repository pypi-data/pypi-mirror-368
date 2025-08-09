"""Centralized logging configuration for Clio SDK"""

import logging


# Create a parent logger for all Clio modules
_clio_logger = logging.getLogger("clio")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the given module name
    
    Args:
        name: Module name (e.g., "client", "uploader")
    
    Returns:
        Logger instance as child of the clio logger
    """
    return logging.getLogger(f"clio.{name}")


def configure_logging(debug: bool = False):
    """Configure logging level for the Clio SDK
    
    Args:
        debug: If True, sets level to DEBUG. Otherwise WARNING.
    """
    # Set level for the clio logger and all its children
    level = logging.DEBUG if debug else logging.WARNING
    _clio_logger.setLevel(level)