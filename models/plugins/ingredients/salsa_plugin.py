"""  
Plugin for Salsa (sauce) ingredient entities.

Registers validators for sauce ingredients.

Author: Rafael Correa
Date: November 13, 2025
"""

from models.core.method_registry import MethodRegistry


def validate_salsa_base(self) -> bool:
    """
    Validate base property.
    
    Returns:
        True if valid
    
    Raises:
        ValueError: If base is invalid
    """
    if not hasattr(self, 'base'):
        raise ValueError(f"Salsa '{self.nombre}' must have 'base' property")
    
    if not self.base or str(self.base).strip() == '':
        raise ValueError(f"Salsa '{self.nombre}' must have non-empty 'base'")
    
    return True


def validate_salsa_color(self) -> bool:
    """
    Validate color property.
    
    Returns:
        True if valid
    
    Raises:
        ValueError: If color is invalid
    """
    if not hasattr(self, 'color'):
        raise ValueError(f"Salsa '{self.nombre}' must have 'color' property")
    
    if not self.color or str(self.color).strip() == '':
        raise ValueError(f"Salsa '{self.nombre}' must have non-empty 'color'")
    
    return True


MethodRegistry.register_validator('Salsa', validate_salsa_base)
MethodRegistry.register_validator('Salsa', validate_salsa_color)