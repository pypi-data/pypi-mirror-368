"""Utility functions for the text-to-curses library."""

import curses
from .renderer import TextRenderer


def display_document(file_path):
    """Simple function to display a document in curses."""
    renderer = TextRenderer(file_path)
    curses.wrapper(lambda stdscr: renderer.display_and_wait(stdscr))
