from typing import Any, Dict

def extract_text_from_block(block: Any) -> str:
    """Recursively extract any text content from a block object."""
    if isinstance(block, str):
        return block
    elif isinstance(block, dict):
        # Look for common text fields first
        for field in ["text", "value", "content", "title", "alt_text"]:
            if field in block:
                value = block[field]
                if isinstance(value, str):
                    return value
                elif isinstance(value, dict):
                    # Recurse into the nested dictionary
                    extracted = extract_text_from_block(value)
                    if extracted:
                        return extracted
        
        # If specific fields are not found, iterate through all values
        for key, value in block.items():
            if key != "type":  # Avoid extracting the block type name itself
                result = extract_text_from_block(value)
                if result:
                    return result

    elif isinstance(block, list):
        # Join text from all items in the list
        return " ".join(filter(None, [extract_text_from_block(item) for item in block]))
    
    return ""