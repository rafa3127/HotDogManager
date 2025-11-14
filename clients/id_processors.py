"""
ID processors for different data structures.

Each processor knows how to add stable IDs to a specific data structure format.
IDs are generated deterministically based on natural keys to ensure consistency
across reloads from external sources.

Author: Rafael Correa
Date: November 14, 2025
"""

import hashlib
from typing import Any, List, Dict, Tuple, Optional


def generate_stable_id(natural_key: str, category: str = "") -> str:
    """
    Generate a stable UUID based on natural key and optional category.
    
    Same inputs always produce the same ID, ensuring consistency when
    reloading data from external sources.
    
    Args:
        natural_key: The natural identifier (e.g., 'simple', 'weiner')
        category: Optional category for namespacing (e.g., 'Pan', 'Salchicha')
    
    Returns:
        A UUID-format string that is deterministic
    
    Examples:
        >>> generate_stable_id('simple', 'Pan')
        'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
        >>> generate_stable_id('simple', 'Pan')  # Same input
        'a1b2c3d4-e5f6-7890-abcd-ef1234567890'  # Same output
    """
    # Combine inputs for uniqueness
    seed = f"{category}:{natural_key}" if category else natural_key
    
    # Generate MD5 hash
    hash_digest = hashlib.md5(seed.encode('utf-8')).hexdigest()
    
    # Format as UUID (8-4-4-4-12)
    return (
        f"{hash_digest[:8]}-"
        f"{hash_digest[8:12]}-"
        f"{hash_digest[12:16]}-"
        f"{hash_digest[16:20]}-"
        f"{hash_digest[20:]}"
    )


def process_grouped_structure_ids(
    raw_data: List[Dict],
    category_field: str = 'Categoria',
    items_field: str = 'Opciones',
    natural_key_field: str = 'nombre',
    id_field: str = 'id'
) -> Tuple[List[Dict], bool]:
    """
    Add stable IDs to a GROUPED data structure.
    
    Grouped structure format:
    [
        {
            "Categoria": "Pan",
            "Opciones": [
                {"nombre": "simple", "tipo": "blanco", ...},
                {"nombre": "integral", "tipo": "trigo", ...}
            ]
        },
        {
            "Categoria": "Salchicha",
            "Opciones": [...]
        }
    ]
    
    IDs are generated as: hash(Category:nombre)
    This ensures:
    - Same item always gets same ID
    - Items with same name in different categories get different IDs
    - Pan "simple" and Salsa "simple" have different IDs
    
    Args:
        raw_data: List of category groups
        category_field: Field name for category (default: 'Categoria')
        items_field: Field name for items array (default: 'Opciones')
        natural_key_field: Field used to generate ID (default: 'nombre')
        id_field: Field name for ID (default: 'id')
    
    Returns:
        Tuple of (processed_data, modified)
        - processed_data: Data with IDs added
        - modified: True if any IDs were added, False if all existed
    
    Raises:
        KeyError: If expected fields are missing
        ValueError: If natural_key_field value is missing in an item
    """
    modified = False
    
    for group in raw_data:
        # Validate structure
        if category_field not in group:
            raise KeyError(f"Missing required field '{category_field}' in group")
        if items_field not in group:
            raise KeyError(f"Missing required field '{items_field}' in group")
        
        category = group[category_field]
        items = group[items_field]
        
        for item in items:
            # Check if ID already exists
            if id_field not in item or not item[id_field]:
                # Validate natural key exists
                if natural_key_field not in item:
                    raise ValueError(
                        f"Item in category '{category}' missing required field '{natural_key_field}'"
                    )
                
                natural_key = item[natural_key_field]
                if not natural_key:
                    raise ValueError(
                        f"Item in category '{category}' has empty '{natural_key_field}'"
                    )
                
                # Generate stable ID
                item[id_field] = generate_stable_id(natural_key, category)
                modified = True
    
    return raw_data, modified


def process_flat_structure_ids(
    raw_data: List[Dict],
    natural_key_field: str = 'nombre',
    id_field: str = 'id',
    category_field: Optional[str] = None
) -> Tuple[List[Dict], bool]:
    """
    Add stable IDs to a FLAT data structure.
    
    Flat structure format:
    [
        {"nombre": "simple", "Pan": "simple", "Salchicha": "weiner", ...},
        {"nombre": "inglés", "Pan": "integral", "Salchicha": "breakfast", ...}
    ]
    
    IDs are generated as: hash(nombre) or hash(category:nombre) if category_field provided
    
    Args:
        raw_data: List of items
        natural_key_field: Field used to generate ID (default: 'nombre')
        id_field: Field name for ID (default: 'id')
        category_field: Optional category field for namespacing
    
    Returns:
        Tuple of (processed_data, modified)
        - processed_data: Data with IDs added
        - modified: True if any IDs were added, False if all existed
    
    Raises:
        ValueError: If natural_key_field value is missing in an item
    """
    modified = False
    
    for item in raw_data:
        # Check if ID already exists
        if id_field not in item or not item[id_field]:
            # Validate natural key exists
            if natural_key_field not in item:
                raise ValueError(f"Item missing required field '{natural_key_field}'")
            
            natural_key = item[natural_key_field]
            if not natural_key:
                raise ValueError(f"Item has empty '{natural_key_field}'")
            
            # Generate stable ID (with or without category)
            if category_field and category_field in item:
                category = item[category_field]
                item[id_field] = generate_stable_id(natural_key, category)
            else:
                item[id_field] = generate_stable_id(natural_key)
            
            modified = True
    
    return raw_data, modified