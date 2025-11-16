"""
Plugin for HotDog entities.

Registers methods and validators for hot dog menu items.

Author: Rafael Correa
Date: November 13, 2025
"""

from models.core.method_registry import MethodRegistry


# Register methods
# Note: All keys are normalized (lowercase, no accents)
MethodRegistry.register_method(
    'HotDog',
    'has_toppings',
    lambda self: hasattr(self, 'toppings') and isinstance(self.toppings, list) and len(self.toppings) > 0
)

MethodRegistry.register_method(
    'HotDog',
    'has_salsas',
    lambda self: hasattr(self, 'salsas') and isinstance(self.salsas, list) and len(self.salsas) > 0
)

MethodRegistry.register_method(
    'HotDog',
    'is_combo',
    lambda self: hasattr(self, 'acompanante') and self.acompanante is not None  # normalized: Acompañante -> acompanante
)


# Register validators
def validate_hotdog_nombre(self) -> bool:
    """Validate nombre property."""
    if not hasattr(self, 'nombre'):
        raise ValueError("HotDog must have 'nombre' property")
    
    if not self.nombre or str(self.nombre).strip() == '':
        raise ValueError("HotDog must have non-empty 'nombre'")
    
    return True


def validate_hotdog_pan(self) -> bool:
    """Validate pan property (normalized from Pan)."""
    if not hasattr(self, 'pan'):
        raise ValueError(f"HotDog '{self.nombre}' must have 'pan' property")
    
    if not self.pan or str(self.pan).strip() == '':
        raise ValueError(f"HotDog '{self.nombre}' must have non-empty 'pan'")
    
    return True


def validate_hotdog_salchicha(self) -> bool:
    """Validate salchicha property (normalized from Salchicha)."""
    if not hasattr(self, 'salchicha'):
        raise ValueError(f"HotDog '{self.nombre}' must have 'salchicha' property")
    
    if not self.salchicha or str(self.salchicha).strip() == '':
        raise ValueError(f"HotDog '{self.nombre}' must have non-empty 'salchicha'")
    
    return True


def validate_hotdog_lists(self) -> bool:
    """Validate that toppings and salsas are lists."""
    if hasattr(self, 'toppings') and not isinstance(self.toppings, list):
        raise ValueError(f"HotDog '{self.nombre}' toppings must be a list")
    
    if hasattr(self, 'salsas') and not isinstance(self.salsas, list):
        raise ValueError(f"HotDog '{self.nombre}' salsas must be a list")
    
    return True


MethodRegistry.register_validator('HotDog', validate_hotdog_nombre)
MethodRegistry.register_validator('HotDog', validate_hotdog_pan)
MethodRegistry.register_validator('HotDog', validate_hotdog_salchicha)
MethodRegistry.register_validator('HotDog', validate_hotdog_lists)