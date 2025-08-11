from typing import Dict, List, Any
from ..formatters.text_formatter import format_text_element_to_mrkdwn
from ..formatters.link_formatter import format_link_element_to_mrkdwn
from ..formatters.list_formatter import format_list_element_to_mrkdwn

def parse_rich_text_to_mrkdwn(richtext_obj: Dict[str, Any]) -> str:
    """Parses a rich text object and returns a markdown string."""
    if not richtext_obj or not isinstance(richtext_obj, dict):
        return ""
        
    obj_type = richtext_obj.get("type")
    
    if obj_type == "rich_text":
        elements = richtext_obj.get("elements", [])
        return "\n".join(filter(None, [parse_rich_text_to_mrkdwn(elem) for elem in elements]))
    
    if obj_type == "rich_text_section":
        return _parse_rich_text_section(richtext_obj)
        
    if obj_type == "rich_text_list":
        return format_list_element_to_mrkdwn(richtext_obj, _parse_rich_text_section)
        
    return ""

def _parse_rich_text_section(section: Dict[str, Any]) -> str:
    """Convert a rich text section's elements to a markdown string."""
    parts = []
    for element in section.get("elements", []):
        elem_type = element.get("type", "")
        
        if elem_type == "text":
            parts.append(format_text_element_to_mrkdwn(element))
        elif elem_type == "link":
            parts.append(format_link_element_to_mrkdwn(element))
        elif elem_type == "emoji":
            parts.append(f":{element.get('name', '')}:")
        elif elem_type == "user":
            parts.append(f"<@{element.get('user_id', '')}>")
        elif elem_type == "channel":
            parts.append(f"<#{element.get('channel_id', '')}>")
        else:
            parts.append(element.get("text", str(element)))
            
    return "".join(parts)