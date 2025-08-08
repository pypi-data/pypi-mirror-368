"""
Text to Curses Print Library

A library for extracting text and color information from various document formats
and displaying them in a terminal using curses with proper color formatting.
"""

from .renderer import TextRenderer
from .utils import display_document

__version__ = "0.1.0"
__all__ = ["TextRenderer", "display_document"]
