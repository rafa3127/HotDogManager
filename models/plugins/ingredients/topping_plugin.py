"""
Plugin for Topping ingredient entities.

Registers validators for topping ingredients.

Author: Rafael Correa
Date: November 13, 2025
"""

from models.core.method_registry import MethodRegistry


def validate_topping_tipo(self) -> bool:
    """
    Validate tipo property.
    
    Returns:
        True if valid
    
    Raises:
        ValueError: If tipo is invalid
    """
    if not hasattr(self, 'tipo'):
        raise ValueError(f"Topping '{self.nombre}' must have 'tipo' property")
    
    if not self.tipo or str(self.tipo).strip() == '':
        raise ValueError(f"Topping '{self.nombre}' must have non-empty 'tipo'")
    
    return True


MethodRegistry.register_validator('Topping', validate_topping_tipo)