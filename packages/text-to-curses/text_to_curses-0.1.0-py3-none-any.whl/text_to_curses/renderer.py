"""
Text to Curses Print Library

A library for extracting text and color information from various document formats
and displaying them in a terminal using curses with proper color formatting.

Supported formats: DOCX, PDF, HTML, RTF, TXT, MD
Color support varies by format - see individual extractor functions for details.

Usage as library:
    renderer = TextRenderer("document.docx")
    curses.wrapper(lambda stdscr: renderer.display(stdscr))
"""

import os
import re
import curses
from bs4 import BeautifulSoup
from docx import Document
import fitz  # PyMuPDF
import webcolors

# Color conversion utilities
def rgb_to_hex(rgb):
    """Convert RGB tuples or floats to #RRGGBB hex format."""
    if isinstance(rgb, tuple) and all(isinstance(x, float) for x in rgb):
        rgb = tuple(int(x * 255) for x in rgb)
    return "#{:02x}{:02x}{:02x}".format(*rgb)

def hex_to_curses(hex_color):
    """Convert hex color (#RRGGBB) to curses RGB format (0-1000)."""
    if not hex_color or not isinstance(hex_color, str):
        return (0, 0, 0)
    
    # Remove '#' if present and handle short form
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join(c*2 for c in hex_color)
    
    if len(hex_color) != 6:
        return (0, 0, 0)
    
    try:
        # Convert hex to RGB (0-255), then to curses (0-1000)
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return tuple(int(c * 1000 / 255) for c in (r, g, b))
    except ValueError:
        return (0, 0, 0)

def normalize_color(val, default="#000000"):
    """Convert various color formats to hex."""
    if not val:
        return default
    try:
        if isinstance(val, str):
            val = val.strip()
            if val.startswith("#"):
                if len(val) == 4:  # #rgb short form
                    val = "#" + "".join(c*2 for c in val[1:])
                return val.lower()
            else:
                # Named color
                return webcolors.name_to_hex(val)
        elif hasattr(val, "rgb"):  # python-docx ColorFormat
            return f"#{val.rgb}" if val.rgb else default
        elif isinstance(val, tuple):
            return rgb_to_hex(val)
    except Exception:
        pass
    return default

# Document extraction functions

def extract_docx(path, default_bg="#181818", default_fg="#cccccc"):
    """
    Extract text and colors from DOCX files.
    
    Color support:
    - ✅ Font colors (when specified)
    - ✅ Highlight colors (predefined Word highlight colors only)
    - ❌ Custom RGB highlights (Word limitation)
    
    Returns: List of rows, each row is list of [char, fg_hex, bg_hex]
    """
    doc = Document(path)
    matrix = []
    # Word highlight color mapping (enum name to hex)
    highlight_map = {
        'YELLOW': '#ffff00',
        'GREEN': '#00ff00',
        'CYAN': '#00ffff',
        'MAGENTA': '#ff00ff',
        'BLUE': '#0000ff',
        'RED': '#ff0000',
        'DARKBLUE': '#000080',
        'DARKCYAN': '#008080',
        'DARKGREEN': '#008000',
        'DARKMAGENTA': '#800080',
        'DARKRED': '#800000',
        'DARKYELLOW': '#808000',
        'BLACK': default_fg,
        'WHITE': '#ffffff',
        'NONE': default_bg,
        None: default_bg,
    }
    for para in doc.paragraphs:
        row = []
        for run in para.runs:
            fg = normalize_color(run.font.color, default_fg)
            highlight = getattr(run.font, 'highlight_color', None)
            bg = default_bg
            # Robust highlight mapping: try .__str__(), .name, or str()
            highlight_name = None
            if highlight is not None:
                if hasattr(highlight, 'name'):
                    highlight_name = highlight.name.upper()
                else:
                    try:
                        highlight_name = highlight if isinstance(highlight, str) else highlight.__str__().upper()
                    except Exception:
                        highlight_name = str(highlight).upper()
                bg = highlight_map.get(highlight_name, default_bg)
            for ch in run.text:
                row.append([ch, fg, bg])
        # Always append a row, even if empty (to preserve empty lines)
        matrix.append(row)
    return matrix

def extract_html(path, default_bg="#181818", default_fg="#cccccc"):
    """
    Extract text and colors from HTML files.
    
    Color support:
    - ✅ Inline CSS color and background-color
    - ❌ External CSS files
    - ❌ Complex CSS selectors
    
    Returns: List of rows, each row is list of [char, fg_hex, bg_hex]
    """
    from bs4.element import Tag
    with open(path, encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    matrix = []
    for elem in soup.find_all(['span', 'div', 'p']):
        if not isinstance(elem, Tag):
            continue
        style = elem.attrs.get('style', None)
        fg = default_fg
        bg = default_bg
        if isinstance(style, str):
            # Basic inline style parsing
            if 'color:' in style:
                try:
                    fg = style.split('color:')[1].split(';')[0].strip()
                    fg = normalize_color(fg, default_fg)
                except Exception:
                    fg = default_fg
            if 'background-color:' in style:
                try:
                    bg = style.split('background-color:')[1].split(';')[0].strip()
                    bg = normalize_color(bg, default_bg)
                except Exception:
                    bg = default_bg
        text = elem.get_text()
        for line in text.splitlines():
            row = []
            for ch in line:
                row.append([ch, fg, bg])
            # Always append a row, even if empty (to preserve empty lines)
            matrix.append(row)
    # Fallback: if no styled elements, just plain text
    if not matrix:
        for line in soup.get_text().splitlines():
            row = []
            for ch in line:
                row.append([ch, default_fg, default_bg])
            # Always append a row, even if empty
            matrix.append(row)
    return matrix

def extract_rtf(path, default_bg="#181818", default_fg="#cccccc"):
    """
    Extract text from RTF files (no color support).
    
    Color support:
    - ❌ RTF color extraction (requires complex parsing)
    - ✅ Strips RTF control codes to plain text
    
    Returns: List of rows, each row is list of [char, fg_hex, bg_hex]
    """
    # Robust fallback: always return plain text with default colors
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            text = f.read()
        # Remove RTF control words and groups
        text_only = re.sub(r"{\\.*?}", "", text)
        text_only = re.sub(r"\\[a-zA-Z]+[0-9]* ?", "", text_only)
        matrix = []
        for line in text_only.splitlines():
            row = []
            for ch in line:
                row.append([ch, default_fg, default_bg])
            # Always append a row, even if empty (to preserve empty lines)
            matrix.append(row)
        return matrix
    except Exception:
        return []

def extract_pdf(path, default_bg="#181818", default_fg="#cccccc"):
    """
    Extract text and colors from PDF files.
    
    Color support:
    - ✅ Text colors from PDF spans (when available)
    - ❌ Background colors (PDF limitation)
    - ✅ Handles both integer and tuple color formats
    
    Returns: List of rows, each row is list of [char, fg_hex, bg_hex]
    """
    doc = fitz.open(path)
    matrix = []
    for page in doc:
        try:
            textpage = page.get_textpage()
            text_dict = textpage.extractDICT()
            for block in text_dict.get("blocks", []):
                for line in block.get("lines", []):
                    row = []
                    for span in line.get("spans", []):
                        color_val = span.get("color", (0, 0, 0))
                        if isinstance(color_val, int):
                            r = (color_val >> 16) & 0xFF
                            g = (color_val >> 8) & 0xFF
                            b = color_val & 0xFF
                            fg = rgb_to_hex((r, g, b))
                        elif isinstance(color_val, tuple) and len(color_val) == 3:
                            fg = rgb_to_hex(color_val)
                        else:
                            fg = default_fg
                        bg = default_bg
                        for ch in span["text"]:
                            row.append([ch, fg, bg])
                    if row:
                        matrix.append(row)
        except Exception:
            try:
                textpage = page.get_textpage()
                text = textpage.extractText()
                for line in text.splitlines():
                    row = []
                    for ch in line:
                        row.append([ch, default_fg, default_bg])
                    if row:
                        matrix.append(row)
            except Exception:
                text = str(page)
                for line in text.splitlines():
                    row = []
                    for ch in line:
                        row.append([ch, default_fg, default_bg])
                    if row:
                        matrix.append(row)
    return matrix
    
def extract_txt(path, default_bg="#181818", default_fg="#cccccc"):
    """
    Extract text from plain text files.
    
    Color support: ❌ None (plain text format)
    
    Returns: List of rows, each row is list of [char, fg_hex, bg_hex]
    """
    matrix = []
    for line in open(path, encoding="utf-8", errors="ignore"):
        # Remove trailing newlines for consistent behavior
        line = line.rstrip("\r\n")
        row = []
        for ch in line:
            row.append([ch, default_fg, default_bg])
        # Always append a row, even if empty (to preserve empty lines)
        matrix.append(row)
    return matrix

def extract_md(path, default_bg="#181818", default_fg="#cccccc"):
    """
    Extract text from Markdown files with formatting stripped.
    
    Color support: ❌ None (formatting is removed)
    Removes: Headers, bold/italic, links, code blocks, lists, etc.
    
    Returns: List of rows, each row is list of [char, fg_hex, bg_hex]
    """
    matrix = []
    with open(path, encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    # Remove markdown formatting
    # Remove headers (# ## ###)
    content = re.sub(r'^#{1,6}\s+', '', content, flags=re.MULTILINE)
    # Remove bold/italic (**text** *text*)
    content = re.sub(r'\*{1,2}([^*]+)\*{1,2}', r'\1', content)
    # Remove code blocks (```code```)
    content = re.sub(r'```[^`]*```', '', content, flags=re.DOTALL)
    # Remove inline code (`code`)
    content = re.sub(r'`([^`]+)`', r'\1', content)
    # Remove links ([text](url))
    content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)
    # Remove images (![alt](url))
    content = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'\1', content)
    # Remove list markers (- * +)
    content = re.sub(r'^[\s]*[-*+]\s+', '', content, flags=re.MULTILINE)
    # Remove numbered list markers (1. 2. etc)
    content = re.sub(r'^[\s]*\d+\.\s+', '', content, flags=re.MULTILINE)
    # Remove blockquotes (>)
    content = re.sub(r'^>\s*', '', content, flags=re.MULTILINE)
    # Remove horizontal rules (--- ***)
    content = re.sub(r'^[-*_]{3,}$', '', content, flags=re.MULTILINE)
    
    for line in content.splitlines():
        row = []
        for ch in line:
            row.append([ch, default_fg, default_bg])
        # Always append a row, even if empty (to preserve empty lines)
        matrix.append(row)
    return matrix

# Main TextRenderer class for library usage

class TextRenderer:
    """
    Text-to-Curses renderer that loads a document once and can display it multiple times.
    
    Usage:
        renderer = TextRenderer("document.docx")
        curses.wrapper(lambda stdscr: renderer.display(stdscr))
    
    Supported formats: .docx, .pdf, .html, .htm, .rtf, .txt, .md
    """
    
    def __init__(self, file_path, default_bg="#181818"):
        """
        Initialize the renderer with a document.
        
        Args:
            file_path: Path to the document file
            default_bg: Default background color (hex format)
        """
        self.file_path = os.path.abspath(file_path)
        self.default_bg = default_bg
        self.default_fg = "#cccccc"  # Light gray default foreground
        
        # Load and process the document
        self.text_matrix = self._extract_text_matrix()
        self.curses_matrix = self._convert_matrix_to_curses()
        self.color_pair_map = None  # Will be initialized on first display
    
    def _extract_text_matrix(self):
        """Extract text matrix from the document file."""
        ext = os.path.splitext(self.file_path)[1].lower()
        
        extractors = {
            ".docx": extract_docx,
            ".html": extract_html,
            ".htm": extract_html,
            ".rtf": extract_rtf,
            ".pdf": extract_pdf,
            ".txt": extract_txt,
            ".md": extract_md,
        }
        
        extractor = extractors.get(ext)
        if not extractor:
            raise ValueError(f"Unsupported file type: {ext}")
        
        return extractor(self.file_path, 
                        default_bg=self.default_bg, 
                        default_fg=self.default_fg)
    
    def _convert_matrix_to_curses(self):
        """Convert hex color matrix to curses RGB format."""
        curses_matrix = []
        for row in self.text_matrix:
            curses_row = []
            for char, fg_hex, bg_hex in row:
                fg_curses = hex_to_curses(fg_hex)
                bg_curses = hex_to_curses(bg_hex)
                curses_row.append([char, fg_curses, bg_curses])
            curses_matrix.append(curses_row)
        return curses_matrix
    
    def _init_color_pairs(self, start_pair=1, start_color=16):
        """Initialize all unique color pairs needed for the curses_matrix."""
        color_pair_map = {}
        color_map = {}
        pair_idx = start_pair
        color_idx = start_color

        can_change = curses.can_change_color()
        for row in self.curses_matrix:
            for _, fg, bg in row:
                fg = tuple(fg)
                bg = tuple(bg)
                if (fg, bg) not in color_pair_map:
                    # Assign color indexes for fg and bg if not already assigned
                    if fg not in color_map:
                        color_map[fg] = color_idx
                        if can_change:
                            curses.init_color(color_idx, *fg)
                        color_idx += 1
                    if bg not in color_map:
                        color_map[bg] = color_idx
                        if can_change:
                            curses.init_color(color_idx, *bg)
                        color_idx += 1
                    # Assign a color pair index
                    curses.init_pair(pair_idx, color_map[fg], color_map[bg])
                    color_pair_map[(fg, bg)] = pair_idx
                    pair_idx += 1
        return color_pair_map
    
    def display(self, stdscr, clear_screen=True):
        """
        Display the document in the provided curses screen.
        
        Args:
            stdscr: Curses screen object from curses.wrapper()
            clear_screen: Whether to clear screen before displaying
        """
        # Initialize color pairs on first display
        if self.color_pair_map is None:
            self.color_pair_map = self._init_color_pairs()
        
        if clear_screen:
            stdscr.clear()
        
        # Display each character with its color
        for row in self.curses_matrix:
            for char, fg_curses, bg_curses in row:
                pair_idx = self.color_pair_map[(tuple(fg_curses), tuple(bg_curses))]
                try:
                    stdscr.addstr(char, curses.color_pair(pair_idx))
                except curses.error:
                    # Handle screen boundary errors gracefully
                    pass
            try:
                stdscr.addstr("\n")
            except curses.error:
                # Handle screen boundary errors gracefully
                pass
        
        stdscr.refresh()
    
    def display_and_wait(self, stdscr):
        """Display the document and wait for user input before returning."""
        self.display(stdscr)
        stdscr.getch()  # Wait for user input
