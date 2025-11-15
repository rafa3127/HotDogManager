"""  
Plugin for Acompañante (side dish) ingredient entities.

Registers validators for side dish ingredients.

Author: Rafael Correa
Date: November 13, 2025
"""

from models.core.method_registry import MethodRegistry


def validate_acompanante_tipo(self) -> bool:
    """
    Validate tipo property.
    
    Returns:
        True if valid
    
    Raises:
        ValueError: If tipo is invalid
    """
    if not hasattr(self, 'tipo'):
        raise ValueError(f"Acompanante '{self.nombre}' must have 'tipo' property")
    
    if not self.tipo or str(self.tipo).strip() == '':
        raise ValueError(f"Acompanante '{self.nombre}' must have non-empty 'tipo'")
    
    return True


def validate_acompanante_tamano(self) -> bool:
    """
    Validate tamano property (normalized from tamaño).
    
    Returns:
        True if valid
    
    Raises:
        ValueError: If tamano is invalid
    """
    if not hasattr(self, 'tamano'):
        raise ValueError(f"Acompanante '{self.nombre}' must have 'tamano' property")
    
    if self.tamano <= 0:
        raise ValueError(f"Acompanante '{self.nombre}' must have positive tamano, got {self.tamano}")
    
    return True


def validate_acompanante_unidad(self) -> bool:
    """
    Validate unidad property.
    
    Returns:
        True if valid
    
    Raises:
        ValueError: If unidad is invalid
    """
    if not hasattr(self, 'unidad'):
        raise ValueError(f"Acompanante '{self.nombre}' must have 'unidad' property")
    
    if not self.unidad or str(self.unidad).strip() == '':
        raise ValueError(f"Acompanante '{self.nombre}' must have non-empty 'unidad'")
    
    return True


# Note: entity_type is 'Acompanante' (normalized, no ñ)
MethodRegistry.register_validator('Acompanante', validate_acompanante_tipo)
MethodRegistry.register_validator('Acompanante', validate_acompanante_tamano)
MethodRegistry.register_validator('Acompanante', validate_acompanante_unidad)