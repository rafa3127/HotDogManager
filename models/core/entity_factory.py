# models/core/entity_factory.py
"""
Factory for creating entity classes dynamically with plugin support.

This factory generates entity classes at runtime based on schemas and injects
registered methods and validators, enabling a flexible plugin architecture.

Author: Rafael Correa
Date: November 13, 2025
"""

from dataclasses import make_dataclass
from typing import Any, Dict, List, Type
from .base_entity import Entity
from .method_registry import MethodRegistry


def create_entity_class(
    class_name: str,
    entity_type: str,
    properties: List[str],
    base_class: Type = Entity
) -> Type:
    """
    Create a dynamic entity class with registered methods and validators.
    
    This function generates a new class at runtime using dataclasses and then
    injects methods and validators that were registered in the MethodRegistry.
    The generated validator automatically calls base class validate() first.
    
    Args:
        class_name: Name for the generated class (e.g., 'Pan', 'HotDog')
        entity_type: Entity type identifier used for method lookup in registry
        properties: List of property names this entity should have
        base_class: Base class to inherit from (default: Entity)
    
    Returns:
        Dynamically generated class with injected methods and validators
    """
    # Build fields for dataclass
    # Start with core Entity fields
    fields = [
        ('id', str),
        ('entity_type', str),
    ]
    
    # Add dynamic properties (all typed as Any for flexibility)
    fields.extend([(prop, Any) for prop in properties])
    
    # Generate the class using make_dataclass
    DynamicClass = make_dataclass(
        class_name,
        fields,
        bases=(base_class,),
        frozen=False  # Allow modification after creation
    )
    
    # Inject registered methods from MethodRegistry
    registered_methods = MethodRegistry.get_methods(entity_type)
    for method_name, method_func in registered_methods.items():
        setattr(DynamicClass, method_name, method_func)
    
    # Inject validator if registered
    validator = MethodRegistry.get_validator(entity_type)
    if validator is not None:
        # Wrap validator to automatically call base class validate() first
        def wrapped_validator(self) -> bool:
            """
            Composed validator that calls base class validation first.
            
            Returns:
                True if all validations pass
            
            Raises:
                ValueError: If any validation fails
            """
            # Call base class validate if it exists
            if hasattr(base_class, 'validate') and base_class != Entity:
                base_class.validate(self)
            
            # Then run the entity-specific composed validator
            return validator(self)
        
        setattr(DynamicClass, 'validate', wrapped_validator)
    
    return DynamicClass


def create_base_class(
    class_name: str,
    common_properties: List[str],
    base_class: Type = Entity
) -> Type:
    """
    Create a base class with common properties and validators.
    
    This creates an intermediate base class (e.g., Ingredient) that other
    entity classes will inherit from. The base class gets its own validator
    injected from the registry.
    
    Args:
        class_name: Name for the base class (e.g., 'Ingredient')
        common_properties: Properties common to all subclasses
        base_class: Base class to inherit from (default: Entity)
    
    Returns:
        Base class with common properties and injected validator
    """
    fields = [
        ('id', str),
        ('entity_type', str),
    ] + [(prop, Any) for prop in common_properties]
    
    BaseClass = make_dataclass(
        class_name,
        fields,
        bases=(base_class,),
        frozen=False
    )
    
    # Inject validator if registered for this base class
    # Use class_name as entity_type (e.g., 'Ingredient')
    validator = MethodRegistry.get_validator(class_name)
    if validator is not None:
        # For base classes, we still wrap to call super if base_class has validate
        def wrapped_validator(self) -> bool:
            """
            Composed validator for base class.
            
            Returns:
                True if all validations pass
            
            Raises:
                ValueError: If any validation fails
            """
            # Call parent class validate if it exists
            if hasattr(base_class, 'validate') and base_class != Entity:
                base_class.validate(self)
            
            # Then run the base class-specific composed validator
            return validator(self)
        
        setattr(BaseClass, 'validate', wrapped_validator)
    
    return BaseClass


def create_entities_from_schemas(
    schemas: Dict[str, List[str]],
    base_class: Type = Entity
) -> Dict[str, Type]:
    """
    Create multiple entity classes from a schemas dictionary.
    
    This is a convenience function for batch creation of entity classes.
    Useful when you have multiple entity types defined in a schema file.
    
    Args:
        schemas: Dictionary mapping entity types to their property lists
                 Example: {
                     'Pan': ['tipo', 'tamaño', 'unidad'],
                     'HotDog': ['pan_id', 'salchicha_id']
                 }
        base_class: Base class to inherit from (default: Entity)
    
    Returns:
        Dictionary mapping class names to generated classes
        Example: {
            'Pan': <class 'Pan'>,
            'HotDog': <class 'HotDog'>
        }
    """
    entities = {}
    
    for entity_type, properties in schemas.items():
        EntityClass = create_entity_class(
            class_name=entity_type,
            entity_type=entity_type,
            properties=properties,
            base_class=base_class
        )
        entities[entity_type] = EntityClass
    
    return entities
