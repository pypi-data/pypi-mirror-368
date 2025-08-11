from typing import Dict
from ..parsers.richtext_parser import parse_rich_text_to_mrkdwn

def richtext_to_blockkit(richtext_obj: dict) -> dict:
    """Converts a Slack Rich Text object to a Block Kit section."""
    if not richtext_obj:
        return {"type": "section", "text": {"type": "mrkdwn", "text": ""}}

    markdown_text = parse_rich_text_to_mrkdwn(richtext_obj)
    
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": markdown_text
        }
    }