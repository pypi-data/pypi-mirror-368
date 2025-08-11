# SlackFormat

[![CI](https://github.com/sbegin0/SlackFormat/actions/workflows/tests.yml/badge.svg)](https://github.com/sbegin0/SlackFormat/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/sbegin0/SlackFormat/branch/main/graph/badge.svg)](https://codecov.io/gh/sbegin0/SlackFormat)

**SlackFormat** is a Python library that enables easy manipulation of Slack messages in any format. It provides a simple and intuitive way to convert between Slack's Markdown, Rich Text, and Block Kit formats.

-----

## Features

  * **Markdown to Rich Text:** Convert Slack's Markdown to a Rich Text object.
  * **Rich Text to Block Kit:** Convert a Rich Text object to a Block Kit JSON structure.
  * **Block Kit to Rich Text:** Convert Block Kit JSON to a Rich Text object.
  * **Block Kit to Markdown:** Convert Block Kit JSON to a Markdown string.
  * **Rich Text to Markdown:** Convert a Rich Text object to a Markdown string.
  * **Markdown to Block Kit:** A convenience function to convert a Markdown string directly to a Block Kit object.
  * **Comprehensive Formatting Support:** Supports various formatting options including bold, italic, strikethrough, code, links, and lists.

-----

## Installation

To install the library, you can use `pip`: (hopefully soon lol -- sorry to get ur hopes up)

```bash
pip install slackformat
```

-----

## Usage

Here are some examples of how to use the **SlackFormat** library.

### Markdown to Rich Text

You can convert a Markdown string to a Slack Rich Text object.

```python
from slackformat import md_to_richtext

md = "Hello *bold* and _italic_ text"
richtext = md_to_richtext(md)
print(richtext)
```

### Rich Text to Block Kit

You can convert a Rich Text object to a Block Kit JSON structure.

```python
from slackformat import richtext_to_blockkit

richtext = {
    "type": "rich_text_section",
    "elements": [
        {"type": "text", "text": "Hello "},
        {"type": "text", "text": "world", "style": {"bold": True}}
    ]
}
blockkit = richtext_to_blockkit(richtext)
print(blockkit)
```

### Block Kit to Rich Text

You can convert a Block Kit JSON structure to a Rich Text object.

```python
from slackformat import blockkit_to_richtext

blockkit = {
    "type": "section",
    "text": {"type": "mrkdwn", "text": "*Bold* text"}
}
richtext = blockkit_to_richtext(blockkit)
print(richtext)
```

### Block Kit to Markdown

You can convert a Block Kit JSON structure to a Markdown string.

```python
from slackformat import blockkit_to_markdown

blockkit = {
    "type": "section",
    "text": {"type": "mrkdwn", "text": "*Bold* text"}
}
markdown = blockkit_to_markdown(blockkit)
print(markdown)
```

### Rich Text to Markdown

You can convert a Rich Text object to a Markdown string.

```python
from slackformat import richtext_to_markdown

richtext = {
    "type": "rich_text_section",
    "elements": [
        {"type": "text", "text": "Hello "},
        {"type": "text", "text": "world", "style": {"bold": True}}
    ]
}
markdown = richtext_to_markdown(richtext)
print(markdown)
```

### Markdown to Block Kit

You can convert a Markdown string directly to a Block Kit object.

```python
from slackformat import md_to_blockkit

md = "Hello *bold* and _italic_ text"
blockkit = md_to_blockkit(md)
print(blockkit)
```

-----

## Testing

To run the tests for this library, you can use `pytest`.

```bash
python -m pytest
```

With coverage reporting (requires `pytest-cov`):

```bash
pytest --cov=slackformat --cov-report=term-missing --cov-report=xml
```

The tests cover the following:

  * **Markdown to Rich Text Converter** (`tests/converters/test_md_to_richtext.py`)
  * **Rich Text to Block Kit Converter** (`tests/converters/test_richtext_to_blockkit.py`)
  * **Block Kit to Rich Text Converter** (`tests/converters/test_blockkit_to_richtext.py`)
  * **Block Kit to Markdown Converter** (`tests/converters/test_blockkit_to_md.py`)
  * **Rich Text to Markdown Converter** (`tests/converters/test_richtext_to_md.py`)
  * **Markdown to Block Kit Converter** (`tests/converters/test_md_to_blockkit.py`)
  * **Integration Tests** (`tests/test_integration.py`)

-----

## License

This project is licensed under the Apache License 2.0.