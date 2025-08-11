from typing import Dict, Any, Callable

def format_list_element_to_mrkdwn(list_obj: Dict[str, Any], section_parser: Callable) -> str:
    """Formats a rich_text_list to a mrkdwn string."""
    style = list_obj.get("style", "bullet")
    parts = []
    for i, item in enumerate(list_obj.get("elements", [])):
        item_text = section_parser(item)
        prefix = f"{i+1}. " if style == "ordered" else "• "
        parts.append(f"{prefix}{item_text}")
    return "\n".join(parts)

def format_list_element_to_md(list_obj: Dict[str, Any]) -> str:
    """Formats a rich_text_list to a standard Markdown string."""
    from .text_formatter import format_rich_text_section_to_md # avoid circular import

    style = list_obj.get("style", "bullet")
    parts = []
    for i, item in enumerate(list_obj.get("elements", [])):
        item_text = format_rich_text_section_to_md(item)
        prefix = f"{i+1}. " if style == "ordered" else "- "
        parts.append(f"{prefix}{item_text}")
    return "\n".join(parts)