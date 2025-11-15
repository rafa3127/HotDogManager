"""
Plugin for Pan (bread) ingredient entities.

Registers validators specific to bread ingredients.

Author: Rafael Correa
Date: November 13, 2025
"""

from models.core.method_registry import MethodRegistry


# Register validators (no need to call super explicitly!)
def validate_pan_tamano(self) -> bool:
    """
    Validate tamano property (normalized from tamaño).
    
    Returns:
        True if valid
    
    Raises:
        ValueError: If tamano is invalid
    """
    if not hasattr(self, 'tamano'):
        raise ValueError(f"Pan '{self.nombre}' must have 'tamano' property")
    
    if self.tamano <= 0:
        raise ValueError(f"Pan '{self.nombre}' must have positive tamano, got {self.tamano}")
    
    return True


def validate_pan_unidad(self) -> bool:
    """
    Validate unidad property.
    
    Returns:
        True if valid
    
    Raises:
        ValueError: If unidad is invalid
    """
    if not hasattr(self, 'unidad'):
        raise ValueError(f"Pan '{self.nombre}' must have 'unidad' property")
    
    if not self.unidad or str(self.unidad).strip() == '':
        raise ValueError(f"Pan '{self.nombre}' must have non-empty 'unidad'")
    
    return True


# Register all validators
MethodRegistry.register_validator('Pan', validate_pan_tamano)
MethodRegistry.register_validator('Pan', validate_pan_unidad)
