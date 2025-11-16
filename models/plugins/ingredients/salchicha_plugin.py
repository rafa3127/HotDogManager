"""
Plugin for Salchicha (sausage) ingredient entities.

Registers methods and validators specific to sausage ingredients.

Author: Rafael Correa
Date: November 13, 2025
"""

from models.core.method_registry import MethodRegistry


# Register method to compare sizes with Pan
# Note: Uses normalized key 'tamano' (no accent)
MethodRegistry.register_method(
    'Salchicha',
    'matches_size',
    lambda self, other: hasattr(self, 'tamano') and hasattr(other, 'tamano') and self.tamano == other.tamano
)


# Register validators
def validate_salchicha_tamano(self) -> bool:
    """
    Validate tamano property (normalized from tamaño).
    
    Returns:
        True if valid
    
    Raises:
        ValueError: If tamano is invalid
    """
    if not hasattr(self, 'tamano'):
        raise ValueError(f"Salchicha '{self.nombre}' must have 'tamano' property")
    
    if self.tamano <= 0:
        raise ValueError(f"Salchicha '{self.nombre}' must have positive tamano, got {self.tamano}")
    
    return True


def validate_salchicha_unidad(self) -> bool:
    """
    Validate unidad property.
    
    Returns:
        True if valid
    
    Raises:
        ValueError: If unidad is invalid
    """
    if not hasattr(self, 'unidad'):
        raise ValueError(f"Salchicha '{self.nombre}' must have 'unidad' property")
    
    if not self.unidad or str(self.unidad).strip() == '':
        raise ValueError(f"Salchicha '{self.nombre}' must have non-empty 'unidad'")
    
    return True


MethodRegistry.register_validator('Salchicha', validate_salchicha_tamano)
MethodRegistry.register_validator('Salchicha', validate_salchicha_unidad)
