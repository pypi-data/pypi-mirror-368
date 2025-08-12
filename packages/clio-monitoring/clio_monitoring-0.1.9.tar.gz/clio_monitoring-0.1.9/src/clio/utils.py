"""Utility functions for Clio SDK"""

import re
from typing import Any, Dict


def mask_sensitive_data(data: str) -> str:
    """Mask sensitive data like API keys in strings"""
    # Mask API keys (clio_*)
    data = re.sub(r'(clio_)[A-Za-z0-9_-]{20,}', r'\1****', data)
    # Mask Bearer tokens
    data = re.sub(r'(Bearer\s+)[A-Za-z0-9_-]{20,}', r'\1****', data)
    # Mask authorization headers
    data = re.sub(r'("Authorization":\s*")(Bearer\s+)?[^"]{20,}(")', r'\1\2****\3', data)
    return data


def mask_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively mask sensitive data in dictionaries"""
    if not isinstance(data, dict):
        return data
    
    masked = {}
    sensitive_keys = {'api_key', 'authorization', 'password', 'secret', 'token'}
    
    for key, value in data.items():
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            if isinstance(value, str) and len(value) > 0:
                # Keep first 4 chars for debugging
                masked[key] = value[:4] + '****' if len(value) > 4 else '****'
            else:
                masked[key] = '****'
        elif isinstance(value, dict):
            masked[key] = mask_dict(value)
        elif isinstance(value, list):
            masked[key] = [mask_dict(item) if isinstance(item, dict) else item for item in value]
        elif isinstance(value, str):
            masked[key] = mask_sensitive_data(value)
        else:
            masked[key] = value
    
    return masked


def safe_repr(obj: Any, mask_sensitive: bool = True) -> str:
    """Create a safe string representation of an object with masked sensitive data"""
    try:
        repr_str = repr(obj)
        if mask_sensitive:
            return mask_sensitive_data(repr_str)
        return repr_str
    except Exception:
        return "<unprintable object>"