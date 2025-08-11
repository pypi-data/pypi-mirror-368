import re
from typing import List, Dict, Any

def parse_markdown_to_elements(text: str) -> List[Dict[str, Any]]:
    """Parse inline markdown formatting into a list of rich text elements."""
    elements = []
    i = 0
    
    while i < len(text):
        char = text[i]
        
        # Bold
        if char == '*':
            end = _find_closing_delimiter(text, i, '*')
            if end != -1 and end > i + 1:
                elements.append({"type": "text", "text": text[i+1:end], "style": {"bold": True}})
                i = end + 1
                continue
        # Italic
        elif char == '_':
            end = _find_closing_delimiter(text, i, '_')
            if end != -1 and end > i + 1:
                elements.append({"type": "text", "text": text[i+1:end], "style": {"italic": True}})
                i = end + 1
                continue
        # Strike
        elif char == '~':
            end = _find_closing_delimiter(text, i, '~')
            if end != -1 and end > i + 1:
                elements.append({"type": "text", "text": text[i+1:end], "style": {"strike": True}})
                i = end + 1
                continue
        # Code
        elif char == '`':
            end = _find_closing_delimiter(text, i, '`')
            if end != -1 and end > i + 1:
                elements.append({"type": "text", "text": text[i+1:end], "style": {"code": True}})
                i = end + 1
                continue
        # Link
        elif char == '<':
            end = text.find('>', i)
            if end != -1 and end > i + 1:
                content = text[i+1:end]
                if '|' in content:
                    url, display_text = content.split('|', 1)
                    elements.append({"type": "link", "url": url.strip(), "text": display_text.strip()})
                else:
                    elements.append({"type": "link", "url": content.strip(), "text": content.strip()})
                i = end + 1
                continue

        # Plain text segment
        next_special = _find_next_special_char(text, i + 1)
        if next_special == -1:
            if i < len(text):
                elements.append({"type": "text", "text": text[i:]})
            break
        else:
            elements.append({"type": "text", "text": text[i:next_special]})
            i = next_special

    return elements

def _find_closing_delimiter(text: str, start: int, delimiter: str) -> int:
    """Find the closing delimiter, ignoring escaped ones."""
    i = start + 1
    while i < len(text):
        if text[i] == delimiter and (i == 0 or text[i-1] != '\\'):
            return i
        i += 1
    return -1

def _find_next_special_char(text: str, start: int) -> int:
    """Find the next special markdown character from a starting position."""
    special_chars = ['*', '_', '~', '`', '<']
    positions = [pos for char in special_chars if (pos := text.find(char, start)) != -1]
    return min(positions) if positions else -1