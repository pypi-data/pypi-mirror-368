from typing import Dict, List, Any
from ..parsers.blockkit_parser import extract_text_from_block
from ..formatters.text_formatter import format_rich_text_section_to_md
from ..utils.text_utils import escape_markdown_chars

def blockkit_to_markdown(blockkit_obj: dict) -> str:
    """Converts a single Block Kit block to a Markdown string."""
    if not blockkit_obj:
        return ""

    block_type = blockkit_obj.get("type", "")

    if block_type == "section":
        text_obj = blockkit_obj.get("text", {})
        if text_obj.get("type") == "mrkdwn":
            return text_obj.get("text", "")
        return escape_markdown_chars(text_obj.get("text", ""))
    
    if block_type == "header":
        text = extract_text_from_block(blockkit_obj.get("text"))
        return f"## {text}"
        
    if block_type == "divider":
        return "---"
        
    if block_type == "context":
        text = extract_text_from_block(blockkit_obj.get("elements"))
        return f"_{text}_"

    if block_type == "image":
        url = blockkit_obj.get("image_url", "")
        alt = blockkit_obj.get("alt_text", "image")
        title = extract_text_from_block(blockkit_obj.get("title"))
        if url:
            title_part = f" \"{title}\"" if title else ""
            return f"![{alt}]({url}{title_part})"
        return f"*[{alt}]*"

    if block_type == "rich_text":
        parts = []
        for element in blockkit_obj.get("elements", []):
            if element.get("type") == "rich_text_section":
                parts.append(format_rich_text_section_to_md(element))
            # Add other rich text element types (list, quote, etc.) here
        return "\n\n".join(parts)

    return extract_text_from_block(blockkit_obj)

def convert_blockkit_blocks_to_markdown(blocks: List[Dict[str, Any]]) -> str:
    """Converts a list of Block Kit blocks to a single markdown string."""
    if not blocks:
        return ""
    return "\n\n".join(filter(None, [blockkit_to_markdown(b) for b in blocks]))