from typing import Dict, Any
from ..utils.style_utils import apply_mrkdwn_style, apply_md_style

def format_text_element_to_mrkdwn(element: Dict[str, Any]) -> str:
    """Formats a text element to Slack's mrkdwn."""
    text = element.get("text", "")
    style = element.get("style", {})
    return apply_mrkdwn_style(text, style)

def format_text_element_to_md(element: Dict[str, Any]) -> str:
    """Formats a text element to standard Markdown."""
    text = element.get("text", "")
    style = element.get("style", {})
    return apply_md_style(text, style)

def format_rich_text_section_to_md(section: Dict[str, Any]) -> str:
    """Converts a rich_text_section to a Markdown string."""
    from .link_formatter import format_link_element_to_md # avoid circular import
    
    parts = []
    for element in section.get("elements", []):
        elem_type = element.get("type", "")
        if elem_type == "text":
            parts.append(format_text_element_to_md(element))
        elif elem_type == "link":
            parts.append(format_link_element_to_md(element))
        elif elem_type == "emoji":
            parts.append(f":{element.get('name', '')}:")
        elif elem_type == "user":
            parts.append(f"<@{element.get('user_id', '')}>")
        # Add other types as needed
    return "".join(parts)