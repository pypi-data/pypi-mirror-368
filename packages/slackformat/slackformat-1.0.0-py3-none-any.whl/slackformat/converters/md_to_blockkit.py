from typing import Dict, Any
from .md_to_richtext import md_to_richtext
from .richtext_to_blockkit import richtext_to_blockkit

def md_to_blockkit(md_text: str) -> Dict[str, Any]:
    """
    Converts a Markdown string directly to a Block Kit object.
    This is a convenience function that chains md_to_richtext and richtext_to_blockkit.
    """
    if not md_text:
        return {"type": "section", "text": {"type": "mrkdwn", "text": ""}}
        
    # Step 1: Convert Markdown to Rich Text
    rich_text_obj = md_to_richtext(md_text)
    
    # Step 2: Convert Rich Text to Block Kit
    blockkit_obj = richtext_to_blockkit(rich_text_obj)
    
    return blockkit_obj