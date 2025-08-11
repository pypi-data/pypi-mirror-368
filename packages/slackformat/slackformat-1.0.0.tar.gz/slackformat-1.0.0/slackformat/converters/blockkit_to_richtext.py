from typing import Dict, Any, List
from .md_to_richtext import md_to_richtext
from ..parsers.blockkit_parser import extract_text_from_block

def blockkit_to_richtext(blockkit_obj: dict) -> dict:
    """Converts a single Block Kit block to a Slack Rich Text object."""
    if not blockkit_obj:
        return {"type": "rich_text_section", "elements": []}

    block_type = blockkit_obj.get("type", "")

    if block_type == "rich_text":
        return blockkit_obj
    
    text_content = ""
    if block_type == "section":
        text_obj = blockkit_obj.get("text", {})
        if text_obj.get("type") == "mrkdwn":
            # If it's markdown, convert it fully
            return md_to_richtext(text_obj.get("text", ""))
        else:
            text_content = text_obj.get("text", "")
    elif block_type == "header":
        text_content = extract_text_from_block(blockkit_obj.get("text"))
        return {
            "type": "rich_text_section",
            "elements": [{"type": "text", "text": text_content, "style": {"bold": True}}]
        }
    elif block_type == "context":
        elements = blockkit_obj.get("elements", [])
        all_elements = []
        for elem in elements:
            rt_obj = md_to_richtext(extract_text_from_block(elem))
            all_elements.extend(rt_obj.get("elements", []))
        return {"type": "rich_text_section", "elements": all_elements}
    else:
        text_content = extract_text_from_block(blockkit_obj)

    return {"type": "rich_text_section", "elements": [{"type": "text", "text": text_content}]}