import pytest
from slackformat.converters.md_to_richtext import md_to_richtext
from slackformat.converters.richtext_to_blockkit import richtext_to_blockkit
from slackformat.converters.blockkit_to_richtext import blockkit_to_richtext
from slackformat.converters.blockkit_to_md import blockkit_to_markdown

class TestIntegration:
    
    def test_roundtrip_md_to_richtext_to_blockkit(self):
        """Test converting markdown -> rich text -> blockkit."""
        md = "Hello *bold* and _italic_ text"
        richtext = md_to_richtext(md)
        blockkit = richtext_to_blockkit(richtext)
        
        assert blockkit["type"] == "section"
        assert "Hello *bold* and _italic_ text" in blockkit["text"]["text"]

    def test_roundtrip_blockkit_to_richtext_to_blockkit(self):
        """Test converting blockkit -> rich text -> blockkit."""
        original_blockkit = {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "*Bold* text"}
        }
        
        richtext = blockkit_to_richtext(original_blockkit)
        new_blockkit = richtext_to_blockkit(richtext)
        
        assert new_blockkit["type"] == "section"
        assert "*Bold* text" in new_blockkit["text"]["text"]
    
    def test_full_roundtrip_md_to_md(self):
        """Test a full round trip: md -> rich text -> blockkit -> md"""
        md_in = "## Title\n\n- *Item 1*\n- `Item 2`"

        # This is a conceptual test. A perfect 1:1 round-trip is hard
        # because markdown has multiple valid representations.
        # md -> rich text
        rich_text = md_to_richtext(md_in)
        # rich text -> blockkit
        blockkit_from_rich = richtext_to_blockkit(rich_text)
        # blockkit -> md
        md_out = blockkit_to_markdown(blockkit_from_rich)

        # The output might not be identical but should be semantically similar.
        # For example, "•" might become "-" in lists.
        # "## Title" might become just bold text.
        assert "Item 1" in md_out
        assert "Item 2" in md_out

class TestEdgeCases:
    
    def test_very_long_text(self):
        long_text = "A" * 5000
        result = md_to_richtext(long_text)
        assert result["elements"][0]["text"] == long_text

    def test_malformed_links(self):
        md = "<incomplete link"
        result = md_to_richtext(md)
        assert result["elements"][0]["text"] == "<incomplete link"

    def test_unicode_text(self):
        md = "Hello 🌍 *世界*"
        blockkit = md_to_richtext(md)
        richtext = richtext_to_blockkit(blockkit)
        
        assert "🌍" in richtext["text"]["text"]
        assert "*世界*" in richtext["text"]["text"]