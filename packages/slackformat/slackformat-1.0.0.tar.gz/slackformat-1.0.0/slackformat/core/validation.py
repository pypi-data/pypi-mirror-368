from typing import Dict, Any, List

def validate_rich_text_structure(obj: Dict[str, Any]) -> bool:
    """Validate that an object has a valid rich text structure."""
    if not isinstance(obj, dict):
        return False
    
    obj_type = obj.get("type")
    if obj_type not in ["rich_text", "rich_text_section", "rich_text_list"]:
        return False
    
    elements = obj.get("elements", [])
    if not isinstance(elements, list):
        return False
        
    if obj_type == "rich_text":
        for element in elements:
            if not validate_rich_text_structure(element):
                return False
    elif obj_type == "rich_text_section":
        for element in elements:
            if not isinstance(element, dict) or not element.get("type"):
                return False
    elif obj_type == "rich_text_list":
        if obj.get("style") not in ["bullet", "ordered"]:
            return False
    
    return True

def validate_blockkit_structure(obj: Dict[str, Any]) -> bool:
    """Validate that an object has a valid Block Kit structure."""
    if not isinstance(obj, dict) or not obj.get("type"):
        return False
    
    obj_type = obj.get("type")
    valid_types = ["section", "divider", "image", "actions", "context", "header", "rich_text"]
    
    if obj_type not in valid_types:
        return False
    
    if obj_type == "section" and not isinstance(obj.get("text"), dict):
        return False
        
    return True