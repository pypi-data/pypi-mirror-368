import re

def normalize_whitespace(text: str) -> str:
    """Replace multiple spaces with a single space and trim lines."""
    text = re.sub(r' +', ' ', text)
    return '\n'.join([line.strip() for line in text.split('\n')])
    
def escape_markdown_chars(text: str) -> str:
    """Escape special markdown characters in plain text."""
    if not text:
        return ""
    special_chars = r'\`*_{}[]()#+-.!|~'
    return re.sub(f'([{re.escape(special_chars)}])', r'\\\1', text)

def normalize_markdown_output(markdown: str) -> str:
    """Normalize markdown output by cleaning up excessive newlines."""
    if not markdown:
        return ""
    markdown = re.sub(r'\n{3,}', '\n\n', markdown.strip())
    return markdown