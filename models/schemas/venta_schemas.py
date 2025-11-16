"""
Venta Schema Module

Defines the schema for Venta (Sales/Orders) entities.

Unlike ingredient and hotdog schemas which are inferred from external data,
Venta schemas are hardcoded as there's no external data source for sales.

Author: Rafael Correa
Date: November 16, 2025
"""

from typing import Dict, List


VENTA_SCHEMA = {
    'Venta': [
        'fecha',    # str - ISO format datetime: '2024-11-16T14:30:00'
        'items',    # List[Dict] - Array of items in the order
    ]
}

# Structure of each item in the 'items' array:
# {
#     'hotdog_id': str,       # ID of the hot dog ordered
#     'hotdog_nombre': str,   # Name of the hot dog (for readability)
#     'cantidad': int         # Quantity ordered
# }

# Note: 'id' field is NOT included in schema as it's added automatically
# by the entity system (excluded in schema inference logic)


# ════════════════════════════════════════════════════════════════════════
# PUBLIC API
# ════════════════════════════════════════════════════════════════════════

def get_venta_schemas() -> Dict[str, List[str]]:
    """
    Get Venta entity schemas.
    
    Unlike ingredient/hotdog schemas, this is hardcoded as there's no
    external data source to infer from.
    
    Returns:
        Dict mapping entity type to list of property names.
        Example: {'Venta': ['fecha', 'items']}
    
    Example:
        >>> schemas = get_venta_schemas()
        >>> print(schemas)
        {'Venta': ['fecha', 'items']}
    """
    return VENTA_SCHEMA.copy()
