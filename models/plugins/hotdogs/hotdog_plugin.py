"""
Plugin for HotDog entities.

Registers methods and validators for hot dog menu items.

Author: Rafael Correa
Date: November 13, 2025
"""

from models.core.method_registry import MethodRegistry


# Register methods
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
    lambda self: hasattr(self, 'Acompañante') and self.Acompañante is not None
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
    """Validate Pan property."""
    if not hasattr(self, 'Pan'):
        raise ValueError(f"HotDog '{self.nombre}' must have 'Pan' property")
    
    if not self.Pan or str(self.Pan).strip() == '':
        raise ValueError(f"HotDog '{self.nombre}' must have non-empty 'Pan'")
    
    return True


def validate_hotdog_salchicha(self) -> bool:
    """Validate Salchicha property."""
    if not hasattr(self, 'Salchicha'):
        raise ValueError(f"HotDog '{self.nombre}' must have 'Salchicha' property")
    
    if not self.Salchicha or str(self.Salchicha).strip() == '':
        raise ValueError(f"HotDog '{self.nombre}' must have non-empty 'Salchicha'")
    
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