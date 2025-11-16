"""
Schema definitions for hotdog entities.

Schemas are inferred from raw menu data structure to maintain data independence.
Falls back to hardcoded schemas if data is not available.

Author: Rafael Correa
Date: November 13, 2025
"""

from typing import Dict, List, Any, Optional


def infer_hotdog_schema(raw_data: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    Infer hotdog schema from raw menu data structure.
    
    Menu data is a flat list of hot dogs, each with direct properties.
    We extract property names from the first item.
    
    Args:
        raw_data: List of hot dog objects
                  Structure: [{'nombre': '...', 'Pan': '...', ...}, ...]
    
    Returns:
        Dictionary with single 'HotDog' entity type and its properties
    """
    if not raw_data or len(raw_data) == 0:
        return {}
    
    # Get properties from first hot dog
    first_hotdog = raw_data[0]
    
    # Extract all property names (excluding technical metadata)
    # Keep 'nombre' first if it exists
    properties = []
    if 'nombre' in first_hotdog:
        properties.append('nombre')
    
    # Add remaining properties (excluding 'id' and 'entity_type' which are technical metadata)
    for key in first_hotdog.keys():
        if key not in properties and key not in ['id', 'entity_type']:
            properties.append(key)
    
    return {'HotDog': properties}


# Hardcoded fallback schema if data inference fails
HOTDOG_SCHEMAS_FALLBACK = {
    'HotDog': ['nombre', 'pan', 'salchicha', 'toppings', 'salsas', 'acompanante']
}


def get_hotdog_schemas(raw_data: Optional[List[Dict[str, Any]]] = None) -> Dict[str, List[str]]:
    """
    Get hotdog schemas, preferring inference from data.
    
    Attempts to infer schema from raw menu data first. If data is not provided
    or inference fails, falls back to hardcoded schema.
    
    Args:
        raw_data: Optional raw menu data from external source
    
    Returns:
        Dictionary mapping 'HotDog' to its property list
    """
    if raw_data:
        try:
            inferred = infer_hotdog_schema(raw_data)
            if inferred:  # Only use if we got results
                return inferred
        except Exception as e:
            # Log error but continue with fallback
            print(f"⚠️  Schema inference failed: {e}")
            print("🔄 Using fallback schemas")
    
    return HOTDOG_SCHEMAS_FALLBACK