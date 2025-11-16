"""
Venta Entity Creator

Creates Venta entity classes dynamically using the entity factory system.

Author: Rafael Correa
Date: November 16, 2025
"""

from typing import Dict, Type
from models.core.entity_factory import create_entities_from_schemas
from models.schemas.venta_schemas import get_venta_schemas


def create_venta_entities() -> Dict[str, Type]:
    """
    Create and return Venta entity classes.
    
    Unlike ingredient/hotdog entities which can infer schemas from data,
    Venta schemas are always hardcoded as there's no external data source.
    
    Returns:
        Dict with entity classes: {'Venta': VentaClass}
    
    Example:
        >>> entities = create_venta_entities()
        >>> Venta = entities['Venta']
        >>> 
        >>> venta = Venta(
        ...     id='venta-001',
        ...     entity_type='Venta',
        ...     fecha='2024-11-16T14:30:00',
        ...     items=[
        ...         {
        ...             'hotdog_id': 'hotdog-simple',
        ...             'hotdog_nombre': 'simple',
        ...             'cantidad': 2
        ...         }
        ...     ]
        ... )
        >>> 
        >>> venta.validate()  # Runs all registered validators
        >>> print(venta.fecha)
        2024-11-16T14:30:00
    """
    # ─── STEP 1: Import plugins (registers validators) ───
    import models.plugins.ventas
    
    # ─── STEP 2: Get hardcoded schemas ───
    schemas = get_venta_schemas()
    # schemas = {'Venta': ['fecha', 'items']}
    
    # ─── STEP 3: Create entity classes ───
    # Base class is Entity (no intermediate base like Ingredient)
    entities = create_entities_from_schemas(schemas)
    # entities = {'Venta': VentaClass}
    
    return entities
