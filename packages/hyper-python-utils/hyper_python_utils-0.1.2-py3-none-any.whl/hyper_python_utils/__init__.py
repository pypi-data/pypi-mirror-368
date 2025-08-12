"""
Hyper Python Utils - AWS S3 and Athena utilities for data processing with Polars
"""

from .file_handler import FileHandler
from .query_manager import QueryManager, EmptyResultError, AthenaQueryError

__version__ = "0.1.2"
__all__ = ["FileHandler", "QueryManager", "EmptyResultError", "AthenaQueryError"]