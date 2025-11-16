"""
Venta Plugin

Registers validation methods for Venta entities.

Validations:
    - fecha is not empty
    - items is a non-empty list
    - each item has required fields (hotdog_id, hotdog_nombre, cantidad)
    - cantidad is positive

Author: Rafael Correa
Date: November 16, 2025
"""

from models.core.method_registry import MethodRegistry


# ════════════════════════════════════════════════════════════════════════
# VALIDATORS
# ════════════════════════════════════════════════════════════════════════

def validate_venta_fecha(self) -> bool:
    """Validate that fecha exists and is not empty."""
    if not hasattr(self, 'fecha'):
        raise ValueError(f"Venta must have 'fecha' property")
    
    if not self.fecha or str(self.fecha).strip() == '':
        raise ValueError(f"Venta must have non-empty 'fecha'")
    
    return True


def validate_venta_items(self) -> bool:
    """Validate that items exists and is a non-empty list."""
    if not hasattr(self, 'items'):
        raise ValueError(f"Venta must have 'items' property")
    
    if not isinstance(self.items, list):
        raise ValueError(f"Venta 'items' must be a list, got {type(self.items).__name__}")
    
    if len(self.items) == 0:
        raise ValueError(f"Venta must have at least one item in 'items'")
    
    return True


def validate_venta_item_structure(self) -> bool:
    """Validate that each item in items has the required structure."""
    if not hasattr(self, 'items'):
        # Let validate_venta_items handle this
        return True
    
    for i, item in enumerate(self.items):
        if not isinstance(item, dict):
            raise ValueError(
                f"Venta item at index {i} must be a dict, got {type(item).__name__}"
            )
        
        # Required fields
        required_fields = ['hotdog_id', 'hotdog_nombre', 'cantidad']
        for field in required_fields:
            if field not in item:
                raise ValueError(
                    f"Venta item at index {i} missing required field '{field}'"
                )
        
        # Validate cantidad is positive
        cantidad = item.get('cantidad')
        if not isinstance(cantidad, int) or cantidad <= 0:
            raise ValueError(
                f"Venta item at index {i} must have positive integer 'cantidad', "
                f"got {cantidad}"
            )
        
        # Validate hotdog_id is not empty
        hotdog_id = item.get('hotdog_id')
        if not hotdog_id or str(hotdog_id).strip() == '':
            raise ValueError(
                f"Venta item at index {i} must have non-empty 'hotdog_id'"
            )
        
        # Validate hotdog_nombre is not empty
        hotdog_nombre = item.get('hotdog_nombre')
        if not hotdog_nombre or str(hotdog_nombre).strip() == '':
            raise ValueError(
                f"Venta item at index {i} must have non-empty 'hotdog_nombre'"
            )
    
    return True


# Register all validators for Venta
# They will be composed and executed in sequence by the entity system
MethodRegistry.register_validator('Venta', validate_venta_fecha)
MethodRegistry.register_validator('Venta', validate_venta_items)
MethodRegistry.register_validator('Venta', validate_venta_item_structure)
