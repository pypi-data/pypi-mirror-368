from typing import Dict, Any

def format_link_element_to_mrkdwn(element: Dict[str, Any]) -> str:
    """Formats a link element to Slack mrkdwn."""
    url = element.get("url", "")
    text = element.get("text", url)
    return f"<{url}|{text}>" if text != url else f"<{url}>"

def format_link_element_to_md(element: Dict[str, Any]) -> str:
    """Formats a link element to standard Markdown."""
    url = element.get("url", "")
    text = element.get("text", url)
    return f"[{text}]({url})"