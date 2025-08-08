"""The Universal Metadata Format (UMF) Python implementation."""

from .metadata import Metadata
from .parse import parse
from .error import UMFError

__version__ = "1.0.0"
__all__ = ["Metadata", "parse", "UMFError"]
