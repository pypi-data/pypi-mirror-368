"""
SlackFormat: A utility for converting between Slack's formats.
"""

__version__ = "1.0.0"

# Main conversion functions
from .converters.md_to_richtext import md_to_richtext
from .converters.richtext_to_blockkit import richtext_to_blockkit
from .converters.blockkit_to_richtext import blockkit_to_richtext
from .converters.blockkit_to_md import blockkit_to_markdown
from .converters.richtext_to_md import richtext_to_markdown
from .converters.md_to_blockkit import md_to_blockkit

__all__ = [
    "md_to_richtext",
    "richtext_to_blockkit",
    "blockkit_to_richtext",
    "blockkit_to_markdown",
    "richtext_to_markdown",
    "md_to_blockkit",
] 