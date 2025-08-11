import re
from typing import Dict, List, Any
from ..parsers.markdown_parser import parse_markdown_to_elements

def md_to_richtext(md_text: str) -> Dict[str, Any]:
    """Converts a Slack Markdown string to a Slack Rich Text object."""
    if not md_text:
        return {"type": "rich_text_section", "elements": []}

    lines = md_text.split('\n')
    sections = []

    for line in lines:
        stripped_line = line.strip()
        if not stripped_line:
            continue

        # Basic list detection
        if re.match(r'^([•*-]|\d+\.)\s+', stripped_line):
            style = "ordered" if re.match(r'^\d+\.\s+', stripped_line) else "bullet"
            content = re.sub(r'^([•*-]|\d+\.)\s+', '', stripped_line)
            elements = parse_markdown_to_elements(content)
            sections.append({
                "type": "rich_text_list",
                "style": style,
                "elements": [{"type": "rich_text_section", "elements": elements}]
            })
        else:
            elements = parse_markdown_to_elements(stripped_line)
            sections.append({"type": "rich_text_section", "elements": elements})
    
    if len(sections) > 1:
        return {"type": "rich_text", "elements": sections}
    if len(sections) == 1:
        return sections[0]
    return {"type": "rich_text_section", "elements": []}