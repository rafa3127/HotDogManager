"""
Base Collection Module

This module provides the abstract base class for all collections in the system.
A collection manages a group of entities of the same type, providing CRUD operations
with deferred persistence through the Unit of Work pattern.

Classes:
    BaseCollection: Abstract base class for entity collections

Author: Rafael Correa
Date: November 15, 2025
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from models.core.base_entity import Entity


class BaseCollection(ABC):
    """
    Abstract base class for all entity collections.
    
    Provides generic CRUD operations (Create, Read, Update, Delete) with deferred
    persistence. Subclasses must implement loading and saving logic specific to
    their data structure.
    
    The collection tracks changes in memory and only persists when flush() is called,
    implementing the Unit of Work pattern for better performance and transactional
    behavior.
    
    Attributes:
        _data_source: DataSourceClient instance for persistence
        _source_name: Name of the data source (e.g., 'ingredientes', 'menu')
        _items: Internal storage as {id: Entity}
        _dirty: Flag indicating if there are unsaved changes
    """
    
    def __init__(self, data_source, source_name: str):
        """
        Initialize the collection.
        
        Args:
            data_source: DataSourceClient instance for persistence
            source_name: Name of the data source (e.g., 'ingredientes', 'menu')
        """
        self._data_source = data_source
        self._source_name = source_name
        self._items: Dict[str, Entity] = {}  # {id: Entity}
        self._dirty = False  # Track if there are unsaved changes
        
        # Load initial data
        self._load()
    
    # ────────────────────────────────────────────────────────────
    # Abstract Methods (Must be implemented by subclasses)
    # ────────────────────────────────────────────────────────────
    
    @abstractmethod
    def _load(self) -> None:
        """
        Load data from data source and populate self._items.
        
        Each collection must implement this method to handle its specific
        data structure (GROUPED, FLAT, etc.) and convert it to {id: Entity}.
        
        This method is called automatically during __init__.
        """
        pass
    
    @abstractmethod
    def _prepare_for_save(self) -> Any:
        """
        Prepare internal data for persistence.
        
        Each collection must implement this method to convert {id: Entity}
        back to its specific data structure (GROUPED, FLAT, etc.) for saving.
        
        Returns:
            Data in the format expected by the data source
        """
        pass
    
    # ────────────────────────────────────────────────────────────
    # CRUD Operations - READ
    # ────────────────────────────────────────────────────────────
    
    def get(self, id: str) -> Optional[Entity]:
        """
        Get an entity by its ID.
        
        Args:
            id: Unique identifier of the entity
            
        Returns:
            Entity if found, None otherwise
        """
        return self._items.get(id)
    
    def get_all(self) -> List[Entity]:
        """
        Get all entities in the collection.
        
        Returns:
            List of all entities
        """
        return list(self._items.values())
    
    def find(self, **criteria) -> List[Entity]:
        """
        Find entities matching the given criteria.
        
        Performs a simple equality-based search on entity attributes.
        All criteria must match for an entity to be included in results.
        
        Args:
            **criteria: Keyword arguments where key is attribute name
                       and value is the value to match
        
        Returns:
            List of entities matching all criteria
            
        Example:
            # Find all Panes with tipo='blanco'
            collection.find(entity_type='Pan', tipo='blanco')
        """
        results = []
        
        for item in self._items.values():
            match = True
            
            # Check if all criteria match
            for key, value in criteria.items():
                if not hasattr(item, key) or getattr(item, key) != value:
                    match = False
                    break
            
            if match:
                results.append(item)
        
        return results
    
    def exists(self, id: str) -> bool:
        """
        Check if an entity with the given ID exists.
        
        Args:
            id: Unique identifier to check
            
        Returns:
            True if entity exists, False otherwise
        """
        return id in self._items
    
    def count(self) -> int:
        """
        Get the total number of entities in the collection.
        
        Returns:
            Number of entities
        """
        return len(self._items)
    
    # ────────────────────────────────────────────────────────────
    # CRUD Operations - CREATE
    # ────────────────────────────────────────────────────────────
    
    def add(self, entity: Entity) -> None:
        """
        Add a new entity to the collection.
        
        The entity is validated before being added. If validation fails,
        a ValueError is raised and the collection remains unchanged.
        
        Args:
            entity: Entity instance to add
            
        Raises:
            ValueError: If entity with same ID already exists
            ValueError: If entity validation fails
        """
        if entity.id in self._items:
            raise ValueError(
                f"Entity with id '{entity.id}' already exists in collection"
            )
        
        # Validate before adding
        entity.validate()
        
        # Add to internal storage
        self._items[entity.id] = entity
        
        # Mark as dirty (needs flush)
        self._dirty = True
    
    # ────────────────────────────────────────────────────────────
    # CRUD Operations - UPDATE
    # ────────────────────────────────────────────────────────────
    
    def update(self, entity: Entity) -> None:
        """
        Update an existing entity in the collection.
        
        The entity must exist (same ID) and will be validated before update.
        If validation fails, a ValueError is raised and the collection
        remains unchanged.
        
        Args:
            entity: Entity instance with updated data
            
        Raises:
            ValueError: If entity with that ID doesn't exist
            ValueError: If entity validation fails
        """
        if entity.id not in self._items:
            raise ValueError(
                f"Entity with id '{entity.id}' not found in collection"
            )
        
        # Validate before updating
        entity.validate()
        
        # Update in internal storage
        self._items[entity.id] = entity
        
        # Mark as dirty
        self._dirty = True
    
    # ────────────────────────────────────────────────────────────
    # CRUD Operations - DELETE
    # ────────────────────────────────────────────────────────────
    
    def delete(self, id: str) -> None:
        """
        Delete an entity from the collection by ID.
        
        Args:
            id: Unique identifier of entity to delete
            
        Raises:
            ValueError: If entity with that ID doesn't exist
        """
        if id not in self._items:
            raise ValueError(
                f"Entity with id '{id}' not found in collection"
            )
        
        # Remove from internal storage
        del self._items[id]
        
        # Mark as dirty
        self._dirty = True
    
    def delete_where(self, **criteria) -> int:
        """
        Delete all entities matching the given criteria.
        
        Args:
            **criteria: Keyword arguments for matching (same as find())
            
        Returns:
            Number of entities deleted
            
        Example:
            # Delete all Panes with tipo='blanco'
            deleted_count = collection.delete_where(entity_type='Pan', tipo='blanco')
        """
        # Find entities to delete
        to_delete = self.find(**criteria)
        
        # Delete each one
        for entity in to_delete:
            del self._items[entity.id]
        
        # Mark as dirty if any deleted
        if to_delete:
            self._dirty = True
        
        return len(to_delete)
    
    # ────────────────────────────────────────────────────────────
    # Persistence (Unit of Work Pattern)
    # ────────────────────────────────────────────────────────────
    
    @property
    def is_dirty(self) -> bool:
        """
        Check if there are unsaved changes.
        
        Returns:
            True if there are changes that need to be flushed, False otherwise
        """
        return self._dirty
    
    def flush(self) -> None:
        """
        Persist all changes to the data source.
        
        This method is typically called by DataHandler.commit() to save
        all collections at once. If there are no changes (_dirty=False),
        this method does nothing.
        
        The flush operation:
        1. Prepares data using _prepare_for_save()
        2. Delegates persistence to DataSourceClient
        3. Clears the dirty flag
        """
        if not self._dirty:
            return  # Nothing to save
        
        # Prepare data for persistence
        data = self._prepare_for_save()
        
        # Delegate saving to DataSource
        self._data_source.save(self._source_name, data)
        
        # Clear dirty flag
        self._dirty = False
    
    def reload(self) -> None:
        """
        Discard all unsaved changes and reload from data source.
        
        This method is typically called by DataHandler.rollback() to
        revert all collections to their last saved state.
        
        The reload operation:
        1. Clears internal storage
        2. Resets dirty flag
        3. Reloads data from source using _load()
        """
        # Clear internal state
        self._items.clear()
        self._dirty = False
        
        # Reload from source
        self._load()
    
    # ────────────────────────────────────────────────────────────
    # Utility Methods
    # ────────────────────────────────────────────────────────────
    
    def clear(self) -> None:
        """
        Remove all entities from the collection.
        
        This marks the collection as dirty. Call flush() to persist the
        empty state, or reload() to discard this change.
        """
        if self._items:
            self._items.clear()
            self._dirty = True
    
    def __len__(self) -> int:
        """
        Get the number of entities in the collection.
        
        Returns:
            Number of entities
        """
        return len(self._items)
    
    def __contains__(self, id: str) -> bool:
        """
        Check if an entity with given ID exists in the collection.
        
        Args:
            id: Entity ID to check
            
        Returns:
            True if entity exists, False otherwise
            
        Example:
            if 'some-id' in collection:
                print("Entity exists")
        """
        return id in self._items
    
    def __repr__(self) -> str:
        """
        Get a string representation of the collection.
        
        Returns:
            String showing collection type, count, and dirty state
        """
        dirty_marker = " (*)" if self._dirty else ""
        return f"{self.__class__.__name__}(count={len(self._items)}, source='{self._source_name}'{dirty_marker})"
