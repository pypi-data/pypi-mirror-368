"""Python client for Spiral"""

# This is here to make sure we load the native extension first
from spiral import _lib

assert _lib

from spiral.client import Spiral  # noqa: E402, I001

__all__ = ["Spiral"]
