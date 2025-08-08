# Text-to-Curses Print Library

A Python library for extracting text and color information from various document formats and displaying them in a terminal using curses with proper color formatting.

## Features

- 🎨 **Color extraction** from documents (DOCX font colors, PDF text colors, HTML inline styles)
- 📄 **Multi-format support**: DOCX, PDF, HTML, RTF, TXT, MD
- 🖥️ **Terminal display** with proper curses color rendering
- 🔄 **Reusable renderers** - load once, display multiple times
- 📦 **Simple API** - just a few lines of code to get started

## Installation

```bash
pip install text-to-curses
```

## Quick Start

```python
from text_to_curses import display_document

# Simple one-liner
display_document("document.docx")
```

## Advanced Usage

```python
from text_to_curses import TextRenderer
import curses

# Load document once, display multiple times
renderer = TextRenderer("document.docx")

def custom_display(stdscr):
    renderer.display(stdscr)
    stdscr.addstr(0, 0, "Press any key to exit", curses.A_REVERSE)
    stdscr.refresh()
    stdscr.getch()

curses.wrapper(custom_display)
```

## Command Line Usage

```bash
text-to-curses document.docx
```

## Supported Formats

| Format | Extension | Color Support | Notes |
|--------|-----------|---------------|-------|
| Word | `.docx` | ✅ Font colors, highlights | Best color support |
| PDF | `.pdf` | ✅ Text colors | Limited background colors |
| HTML | `.html`, `.htm` | ✅ Inline CSS | `color` and `background-color` |
| RTF | `.rtf` | ❌ Plain text only | RTF codes stripped |
| Text | `.txt` | ❌ Plain text only | Default colors |
| Markdown | `.md` | ❌ Plain text only | Formatting stripped |

## Examples

See the `examples/` directory for more usage examples:
- Basic document viewer
- Multi-document slideshow
- Custom display functions

## Development

```bash
git clone https://github.com/yourusername/Text-to-Curses-print.git
cd Text-to-Curses-print
pip install -e .
```

## License

MIT License - see LICENSE file for details.
