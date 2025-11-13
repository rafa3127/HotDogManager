"""
Plugin for Salchicha (sausage) ingredient entities.

Registers methods and validators specific to sausage ingredients.

Author: Rafael Correa
Date: November 13, 2025
"""

from models.core.method_registry import MethodRegistry


# Register method to compare sizes with Pan
MethodRegistry.register_method(
    'Salchicha',
    'matches_size',
    lambda self, other: hasattr(self, 'tamaño') and hasattr(other, 'tamaño') and self.tamaño == other.tamaño
)


# Register validators
def validate_salchicha_tamaño(self) -> bool:
    """
    Validate tamaño property.
    
    Returns:
        True if valid
    
    Raises:
        ValueError: If tamaño is invalid
    """
    if not hasattr(self, 'tamaño'):
        raise ValueError(f"Salchicha '{self.nombre}' must have 'tamaño' property")
    
    if self.tamaño <= 0:
        raise ValueError(f"Salchicha '{self.nombre}' must have positive tamaño, got {self.tamaño}")
    
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


MethodRegistry.register_validator('Salchicha', validate_salchicha_tamaño)
MethodRegistry.register_validator('Salchicha', validate_salchicha_unidad)
