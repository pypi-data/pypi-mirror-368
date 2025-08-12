"""
SAGE Utils Module

This module provides a compatibility layer for sage.utils imports.
It re-exports functionality from sage.common.utils to maintain backward compatibility.
"""

import datetime
import logging as std_logging

try:
    # Try to import from sage.common.utils first
    from sage.common.utils.logging import get_logger as common_get_logger
    
    def get_logger(name: str = "sage"):
        """Get a logger instance"""
        return common_get_logger(name)
        
except ImportError:
    # Fallback implementations if sage-common is not available
    def get_logger(name: str = "sage"):
        """Get a logger instance"""
        return std_logging.getLogger(name)

def now():
    """Get current timestamp"""
    return datetime.datetime.now()

# Import submodules
from . import logging, serialization, network, system

__all__ = [
    "get_logger",
    "now", 
    "logging",
    "serialization",
    "network", 
    "system"
]

__all__ = [
    "get_logger",
    "now", 
    "logging",
    "serialization",
    "network", 
    "system"
]
