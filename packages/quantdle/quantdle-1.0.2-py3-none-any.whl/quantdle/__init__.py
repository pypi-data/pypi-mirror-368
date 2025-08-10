# coding: utf-8

"""
Quantdle Python Client

A user-friendly Python client for downloading financial market data from Quantdle.
"""

from __future__ import absolute_import

# Get version from package metadata (single source of truth in pyproject.toml)
from importlib.metadata import version

__version__ = version("quantdle")

# Import main client (only thing users need)
from .client import Client

__all__ = [
    "Client",
]