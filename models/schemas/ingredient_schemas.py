# models/schemas/ingredient_schemas.py
"""
Schema definitions for ingredient entities.

Schemas are inferred from raw data structure to maintain data independence.
Automatically detects common properties to create base ingredient class.

Author: Rafael Correa
Date: November 13, 2025
"""

from typing import Dict, List, Any, Optional, Tuple


def find_common_properties(schemas: Dict[str, List[str]]) -> List[str]:
    """
    Find properties that are common across all entity types.
    
    Args:
        schemas: Dict mapping entity types to their properties
    
    Returns:
        List of property names present in ALL entity types
    """
    if not schemas:
        return []
    
    # Get first schema's properties as starting point
    common = set(next(iter(schemas.values())))
    
    # Intersect with all other schemas
    for properties in schemas.values():
        common &= set(properties)
    
    return list(common)


def infer_schemas_from_data(raw_data: List[Dict[str, Any]]) -> Tuple[Dict[str, List[str]], List[str]]:
    """
    Infer entity schemas from raw ingredient data structure.
    
    Analyzes the structure and identifies common properties across all categories
    to create a base class schema.
    
    Args:
        raw_data: List of categories with options
                  Structure: [{'Categoria': 'Pan', 'Opciones': [{...}]}, ...]
    
    Returns:
        Tuple of (schemas dict, common properties list)
        - schemas: Dict mapping entity types to their SPECIFIC properties
        - common: List of properties present in ALL categories
    """
    all_schemas = {}
    
    for category_data in raw_data:
        categoria = category_data.get('categoria')
        opciones = category_data.get('opciones', [])
        if not categoria:
            continue
        
        # Capitalize entity_type to follow Python class naming conventions
        entity_type = categoria.capitalize()
        
        if opciones and len(opciones) > 0:
            first_option = opciones[0]
            
            # Extract all property names (excluding technical metadata)
            properties = []
            if 'nombre' in first_option:
                properties.append('nombre')
            
            for key in first_option.keys():
                if key not in properties and key not in ['categoria', 'id', 'entity_type']:
                    properties.append(key)
            
            all_schemas[entity_type] = properties
    # Find common properties
    common_properties = find_common_properties(all_schemas)
    
    # Remove common properties from individual schemas to avoid duplication
    print(all_schemas)
    specific_schemas = {}
    for entity_type, properties in all_schemas.items():
        print(entity_type)
        print(properties)
        specific_props = [p for p in properties if p not in common_properties]
        specific_schemas[entity_type] = specific_props
    
    return specific_schemas, common_properties


# Hardcoded fallback schemas if data inference fails
# Note: Keys are normalized (no accents, capitalized)
INGREDIENT_SCHEMAS_FALLBACK = {
    'Pan': ['tipo', 'tamano', 'unidad'],
    'Salchicha': ['tipo', 'tamano', 'unidad'],
    'Acompanante': ['tipo', 'tamano', 'unidad'],  # Normalized: no ñ
    'Salsa': ['base', 'color'],
    'Toppings': ['tipo', 'presentacion']
}

INGREDIENT_BASE_PROPERTIES_FALLBACK = ['nombre']


def get_ingredient_schemas(
    raw_data: Optional[List[Dict[str, Any]]] = None
) -> Tuple[Dict[str, List[str]], List[str]]:
    """
    Get ingredient schemas, preferring inference from data.
    
    Returns both specific schemas for each category and common properties
    that should be in a base Ingredient class.
    
    Args:
        raw_data: Optional raw ingredient data from external source
    
    Returns:
        Tuple of (specific schemas dict, common properties list)
    """
    if raw_data:
        try:
            specific, common = infer_schemas_from_data(raw_data)
            if specific:  # Only use if we got results
                return specific, common
        except Exception as e:
            print(f"⚠️  Schema inference failed: {e}")
            print("🔄 Using fallback schemas")
    
    return INGREDIENT_SCHEMAS_FALLBACK, INGREDIENT_BASE_PROPERTIES_FALLBACK