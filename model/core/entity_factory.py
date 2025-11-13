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
    
    Args:
        class_name: Name for the generated class
        entity_type: Entity type identifier used for method lookup in registry
        properties: List of property names this entity should have
        base_class: Base class to inherit from (default: Entity)
    
    Returns:
        Dynamically generated class with injected methods
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
        setattr(DynamicClass, 'validate', validator)
    
    return DynamicClass


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
        base_class: Base class to inherit from (default: Entity)
    
    Returns:
        Dictionary mapping class names to generated classes
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