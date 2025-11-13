"""
Base plugin for Ingredient class.

Registers common validation for all ingredient entities.

Author: Rafael Correa
Date: November 13, 2025
"""

from models.core.method_registry import MethodRegistry


def validate_ingredient_nombre(self) -> bool:
    """
    Validate that ingredient has a valid nombre.
    
    Returns:
        True if valid
    
    Raises:
        ValueError: If nombre is missing or empty
    """
    if not hasattr(self, 'nombre'):
        raise ValueError(f"{self.entity_type} must have 'nombre' property")
    
    if not self.nombre or str(self.nombre).strip() == '':
        raise ValueError(f"{self.entity_type} must have non-empty 'nombre'")
    
    return True


# Register for base Ingredient type
MethodRegistry.register_validator('Ingredient', validate_ingredient_nombre)