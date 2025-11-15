"""  
Plugin for Toppings ingredient entities.

Registers validators for topping ingredients.

Author: Rafael Correa
Date: November 13, 2025
"""

from models.core.method_registry import MethodRegistry


def validate_toppings_tipo(self) -> bool:
    """
    Validate tipo property.
    
    Returns:
        True if valid
    
    Raises:
        ValueError: If tipo is invalid
    """
    if not hasattr(self, 'tipo'):
        raise ValueError(f"Toppings '{self.nombre}' must have 'tipo' property")
    
    if not self.tipo or str(self.tipo).strip() == '':
        raise ValueError(f"Toppings '{self.nombre}' must have non-empty 'tipo'")
    
    return True


def validate_toppings_presentacion(self) -> bool:
    """
    Validate presentacion property.
    
    Returns:
        True if valid
    
    Raises:
        ValueError: If presentacion is invalid
    """
    if not hasattr(self, 'presentacion'):
        raise ValueError(f"Toppings '{self.nombre}' must have 'presentacion' property")
    
    if not self.presentacion or str(self.presentacion).strip() == '':
        raise ValueError(f"Toppings '{self.nombre}' must have non-empty 'presentacion'")
    
    return True


# Note: entity_type is 'Toppings' (plural), not 'Topping'
MethodRegistry.register_validator('Toppings', validate_toppings_tipo)
MethodRegistry.register_validator('Toppings', validate_toppings_presentacion)