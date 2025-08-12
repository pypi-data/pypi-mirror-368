"""Top-level package for oai-rfsim.

This module exposes a few constants like the package version.  The
functionality of the package is implemented in :mod:`oai_rfsim.cli`.
"""

__author__ = "OpenAI Assistant"
__email__ = ""
__version__ = "0.1.0"

from .cli import main  # noqa: F401

__all__ = ["main"]