from typing import List, Dict, Any

def merge_text_elements(elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Merge consecutive text elements that have the same style."""
    if not elements:
        return []
    
    merged = [elements[0].copy()]
    for element in elements[1:]:
        last = merged[-1]
        if (element.get("type") == "text" and 
            last.get("type") == "text" and 
            element.get("style", {}) == last.get("style", {})):
            last["text"] += element["text"]
        else:
            merged.append(element.copy())
            
    return merged

def clean_empty_elements(elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove empty text elements from a list."""
    return [elem for elem in elements if not (elem.get("type") == "text" and not elem.get("text", "").strip())]