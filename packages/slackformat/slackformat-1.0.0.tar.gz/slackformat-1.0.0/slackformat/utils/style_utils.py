from typing import Dict

def apply_mrkdwn_style(text: str, style: Dict[str, bool]) -> str:
    """Apply Slack mrkdwn formatting based on a style dict."""
    if style.get("code"):
        text = f"`{text}`"
    if style.get("bold"):
        text = f"*{text}*"
    if style.get("italic"):
        text = f"_{text}_"
    if style.get("strike"):
        text = f"~{text}~"
    return text

def apply_md_style(text: str, style: Dict[str, bool]) -> str:
    """Apply standard Markdown formatting based on a style dict."""
    if style.get("bold") and style.get("italic"):
        text = f"***{text}***"
    elif style.get("bold"):
        text = f"**{text}**"
    elif style.get("italic"):
        text = f"*{text}*"
    
    if style.get("strike"):
        text = f"~~{text}~~"
    if style.get("code"):
        text = f"`{text}`"
    return text