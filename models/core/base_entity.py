"""
Generic base entity class for dynamic domain modeling.

This class serves as the foundation for any domain entity (ingredients, hot dogs, 
sales, customers, etc.) allowing complete data independence and reusability across 
different projects.

Author: Rafael Correa
Date: November 13, 2025
"""

from typing import Any, Dict


class Entity:
    """
    generic base class for any domain entity.
    
    This class can represent any business object by accepting dynamic properties
    through **kwargs. Properties are set as real attributes (not dict lookup),
    allowing natural access like entity.property_name.
    
    """
    
    def __init__(self, id: str, entity_type: str, **kwargs):
        """
        Initialize entity with core fields and dynamic properties.
        
        Args:
            id: Unique identifier (UUID)
            entity_type: Type/category of entity (e.g., 'Pan', 'HotDog', 'Dog')
            **kwargs: Dynamic properties specific to this entity type
        
        """
        self.id = id
        self.entity_type = entity_type
        
        # Set all additional properties as real attributes
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert entity to dictionary including all dynamic attributes.
        
        Excludes private attributes (starting with _) and methods.
        Useful for serialization to JSON.
        
        Returns:
            Dictionary with all public attributes
        
        """
        return {
            key: value 
            for key, value in self.__dict__.items() 
            if not key.startswith('_') and not callable(value)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Entity':
        """
        Create entity instance from dictionary.
        
        Useful for deserializing from JSON or database records.
        
        Args:
            data: Dictionary containing at minimum 'id' and 'entity_type'
        
        Returns:
            Entity instance with all properties from dict
        
        """
        return cls(**data)
    
    def validate(self) -> bool:
        """
        Validate entity state.
        
        This is a hook method that will be overridden by plugins through
        dynamic method injection. By default, returns True (valid).
        
        Returns:
            True if entity is valid, raises ValueError if invalid
        
        Raises:
            ValueError: If validation fails (injected by plugins)
        """
        return True
    
    def __repr__(self) -> str:
        """
        String representation for debugging.
        
        Shows class name and all attributes in a readable format.
        
        Returns:
            String representation of entity
        
        """
        attrs = ', '.join(
            f"{k}='{v}'" if isinstance(v, str) else f"{k}={v}"
            for k, v in self.__dict__.items()
        )
        return f"{self.__class__.__name__}({attrs})"
    
    def __eq__(self, other: Any) -> bool:
        """
        Compare entities by ID.
        
        Two entities are equal if they have the same ID.
        
        Args:
            other: Another entity to compare with
        
        Returns:
            True if entities have same ID
        
        """
        if not isinstance(other, Entity):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """
        Hash based on ID.
        
        Allows entities to be used in sets and as dict keys.
        
        Returns:
            Hash value based on ID
        """
        return hash(self.id)