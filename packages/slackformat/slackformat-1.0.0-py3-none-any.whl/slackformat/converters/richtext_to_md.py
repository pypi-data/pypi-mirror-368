from typing import Dict, Any
from ..formatters.text_formatter import format_rich_text_section_to_md
from ..formatters.list_formatter import format_list_element_to_md

def richtext_to_markdown(richtext_obj: Dict[str, Any]) -> str:
    """Converts a Slack Rich Text object to a markdown string."""
    if not richtext_obj:
        return ""

    obj_type = richtext_obj.get("type")
    elements = richtext_obj.get("elements", [])
    
    if obj_type == "rich_text":
        return "\n\n".join(filter(None, [richtext_to_markdown(elem) for elem in elements]))
    
    if obj_type == "rich_text_section":
        return format_rich_text_section_to_md(richtext_obj)
        
    if obj_type == "rich_text_list":
        return format_list_element_to_md(richtext_obj)
        
    if obj_type == "rich_text_quote":
        text = "\n".join([format_rich_text_section_to_md(elem) for elem in elements])
        return "\n".join([f"> {line}" for line in text.split('\n')])
        
    if obj_type == "rich_text_preformatted":
        text = "".join([elem.get("text", "") for elem in elements if elem.get("type") == "text"])
        return f"```\n{text}\n```"

    return ""