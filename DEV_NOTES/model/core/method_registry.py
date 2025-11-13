"""
Central registry for entity-specific methods and validators.

This registry allows dynamic registration of functionality for any entity type,
enabling a plugin architecture where behavior can be added without modifying
the core entity classes.

Author: Rafael Correa
Date: November 13, 2025
"""

from typing import Callable, Dict, Optional


class MethodRegistry:
    """
    Central registry for entity-specific methods and validators.
    
    This class maintains a registry of methods and validators that can be
    dynamically injected into entity classes. Supports any entity type,
    making it completely domain-independent.
    
    The registry uses class-level storage, meaning all registrations are
    shared across the application lifecycle.
    """
    
    # Class-level storage for all registered methods and validators
    _methods: Dict[str, Dict[str, Callable]] = {}
    _validators: Dict[str, Callable] = {}
    
    @classmethod
    def register_method(cls, entity_type: str, method_name: str, func: Callable) -> None:
        """
        Register a method for a specific entity type.
        
        The registered function will be injected into all instances of the
        specified entity type, making it available as a regular method.
        
        Args:
            entity_type: Type of entity (e.g., 'Pan', 'HotDog', 'VentaRegistro')
            method_name: Name of the method (e.g., 'es_largo', 'tiene_toppings')
            func: Function to register (can be lambda or regular function)
                  Should accept 'self' as first parameter
        """
        if entity_type not in cls._methods:
            cls._methods[entity_type] = {}
        
        cls._methods[entity_type][method_name] = func
    
    @classmethod
    def register_validator(cls, entity_type: str, func: Callable) -> None:
        """
        Register a validator function for a specific entity type.
        
        The validator will replace the default validate() method in the entity.
        Should raise ValueError if validation fails, return True if valid.
        
        Args:
            entity_type: Type of entity
            func: Validator function that accepts 'self' as parameter
                  Should raise ValueError on validation failure
        """
        cls._validators[entity_type] = func
    
    @classmethod
    def get_methods(cls, entity_type: str) -> Dict[str, Callable]:
        """
        Get all registered methods for an entity type.
        
        Args:
            entity_type: Type of entity
        
        Returns:
            Dictionary mapping method names to functions
            Empty dict if no methods registered
        """
        return cls._methods.get(entity_type, {})
    
    @classmethod
    def get_validator(cls, entity_type: str) -> Optional[Callable]:
        """
        Get validator for an entity type.
        
        Args:
            entity_type: Type of entity
        
        Returns:
            Validator function if registered, None otherwise
        """
        return cls._validators.get(entity_type)
    
    @classmethod
    def has_methods(cls, entity_type: str) -> bool:
        """
        Check if entity type has any registered methods.
        
        Args:
            entity_type: Type of entity
        
        Returns:
            True if entity has registered methods
        """
        return entity_type in cls._methods and len(cls._methods[entity_type]) > 0
    
    @classmethod
    def has_validator(cls, entity_type: str) -> bool:
        """
        Check if entity type has a registered validator.
        
        Args:
            entity_type: Type of entity
        
        Returns:
            True if entity has a registered validator
        """
        return entity_type in cls._validators
    
    @classmethod
    def clear(cls) -> None:
        """
        Clear all registrations.
        
        Useful for testing to ensure clean state between tests.
        Should not be used in production code.
        """
        cls._methods.clear()
        cls._validators.clear()
    
    @classmethod
    def get_all_registered_types(cls) -> set:
        """
        Get all entity types that have registrations.
        
        Returns:
            Set of entity type names
        """
        method_types = set(cls._methods.keys())
        validator_types = set(cls._validators.keys())
        return method_types | validator_types