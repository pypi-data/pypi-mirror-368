"""Command line interface for text-to-curses."""

import sys
import argparse
from .utils import display_document


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Display documents in terminal with colors using curses"
    )
    parser.add_argument(
        "file",
        help="Path to the document file (supports .docx, .pdf, .html, .rtf, .txt, .md)"
    )
    
    args = parser.parse_args()
    
    try:
        display_document(args.file)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
