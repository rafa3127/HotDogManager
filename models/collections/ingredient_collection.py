"""
Ingredient Collection Module

This module provides the concrete collection implementation for ingredients,
handling the GROUPED data structure (categories with options).

Classes:
    IngredientCollection: Collection for managing ingredient entities

Author: Rafael Correa
Date: November 15, 2025
"""

from typing import Dict, List, Optional
from models.collections.base_collection import BaseCollection
from models.core.base_entity import Entity


class IngredientCollection(BaseCollection):
    """
    Collection for managing ingredient entities.
    
    Handles the GROUPED data structure where ingredients are organized by
    categories (Pan, Salchicha, Toppings, Salsa, Acompañante), each containing
    a list of options.
    
    Data Structure (GROUPED):
        [
            {
                "categoria": "pan",
                "opciones": [
                    {"id": "...", "nombre": "simple", "tipo": "blanco", ...},
                    {"id": "...", "nombre": "integral", "tipo": "trigo", ...}
                ]
            },
            {
                "categoria": "salchicha",
                "opciones": [...]
            }
        ]
    
    The collection converts this structure to/from a flat {id: Entity} dict
    for easy CRUD operations.
    
    Attributes:
        _entity_classes: Dict mapping category names to their entity classes
                        (e.g., {'Pan': PanClass, 'Salchicha': SalchichaClass})
    """
    
    def __init__(self, data_source):
        """
        Initialize the ingredient collection.
        
        Args:
            data_source: DataSourceClient instance for persistence
        """
        # Store entity classes (will be populated in _load)
        self._entity_classes: Dict[str, type] = {}
        
        # Call parent constructor (which calls _load)
        super().__init__(data_source, 'ingredientes')
    
    # ────────────────────────────────────────────────────────────
    # Abstract Methods Implementation
    # ────────────────────────────────────────────────────────────
    
    def _load(self) -> None:
        """
        Load ingredients from data source and populate self._items.
        
        Process:
        1. Get raw data from data source (GROUPED structure)
        2. Create entity classes dynamically using schemas inferred from data
        3. Convert GROUPED structure to flat {id: Entity} dict
        4. Store entity classes for later use in _prepare_for_save
        """
        # Get raw data (GROUPED structure with IDs and normalized keys)
        raw_data = self._data_source.get(self._source_name)
        
        if not raw_data:
            # No data to load (empty collection)
            return
        
        # Create entity classes dynamically from data
        from models.entities.ingredients import create_ingredient_entities
        self._entity_classes = create_ingredient_entities(raw_data)
        
        # Convert GROUPED structure to flat {id: Entity}
        for category_data in raw_data:
            categoria = category_data.get('categoria', '')
            opciones = category_data.get('opciones', [])
            
            # Capitalize category name to match class name (pan -> Pan)
            entity_type = categoria.capitalize()
            
            # Get the corresponding entity class
            EntityClass = self._entity_classes.get(entity_type)
            
            if EntityClass is None:
                # Skip unknown categories (shouldn't happen with dynamic creation)
                continue
            
            # Create entity instances from opciones
            for item_data in opciones:
                # Remove entity_type from data if present (will be added via parameter)
                # This handles the case where data was previously saved with entity_type
                clean_data = {k: v for k, v in item_data.items() if k != 'entity_type'}
                
                # Create entity instance
                # The entity_type is added to distinguish between different ingredient types
                entity = EntityClass(**clean_data, entity_type=entity_type)
                
                # Add to internal storage
                self._items[entity.id] = entity
    
    def _prepare_for_save(self) -> List[Dict]:
        """
        Convert internal {id: Entity} structure to GROUPED format for saving.
        
        Process:
        1. Group entities by their entity_type (categoria)
        2. Convert each entity to dict using to_dict()
        3. Build GROUPED structure: [{categoria: ..., opciones: [...]}, ...]
        
        Returns:
            List of category dicts in GROUPED format
        """
        # Group entities by category
        grouped: Dict[str, List[Dict]] = {}
        
        for entity in self._items.values():
            categoria = entity.entity_type
            
            if categoria not in grouped:
                grouped[categoria] = []
            
            # Convert entity to dict and add to group
            grouped[categoria].append(entity.to_dict())
        
        # Convert grouped dict to GROUPED structure
        result = []
        for categoria, items in grouped.items():
            result.append({
                'categoria': categoria.lower(),  # Normalize to lowercase
                'opciones': items
            })
        
        return result
    
    # ────────────────────────────────────────────────────────────
    # Domain-Specific Methods
    # ────────────────────────────────────────────────────────────
    
    def get_by_category(self, categoria: str) -> List[Entity]:
        """
        Get all ingredients of a specific category.
        
        Args:
            categoria: Category name (e.g., 'Pan', 'Salchicha', 'Toppings')
                      Case-insensitive, will be capitalized automatically
        
        Returns:
            List of entities in that category
            
        Example:
            panes = collection.get_by_category('Pan')
            salsas = collection.get_by_category('salsa')  # Auto-capitalized
        """
        # Capitalize to match entity_type format
        entity_type = categoria.capitalize()
        
        # Use base class find method
        return self.find(entity_type=entity_type)
    
    def get_by_name(self, nombre: str, categoria: Optional[str] = None) -> Optional[Entity]:
        """
        Get an ingredient by name, optionally filtering by category.
        
        Args:
            nombre: Name of the ingredient
            categoria: Optional category to filter (e.g., 'Pan')
                      If None, searches across all categories
        
        Returns:
            First matching entity, or None if not found
            
        Example:
            pan = collection.get_by_name('simple', 'Pan')
            salsa = collection.get_by_name('mostaza')  # Search all categories
        """
        criteria = {'nombre': nombre}
        
        if categoria:
            criteria['entity_type'] = categoria.capitalize()
        
        results = self.find(**criteria)
        
        return results[0] if results else None
    
    def exists_in_category(self, nombre: str, categoria: str) -> bool:
        """
        Check if an ingredient with given name exists in a specific category.
        
        This is useful for validating uniqueness before adding new ingredients,
        as ingredient names must be unique within their category.
        
        Args:
            nombre: Name to check
            categoria: Category to check in (e.g., 'Pan')
        
        Returns:
            True if ingredient exists in that category, False otherwise
            
        Example:
            if collection.exists_in_category('simple', 'Pan'):
                print("Pan 'simple' already exists")
        """
        result = self.get_by_name(nombre, categoria)
        return result is not None
    
    def get_categories(self) -> List[str]:
        """
        Get list of all categories present in the collection.
        
        Returns:
            List of unique category names (capitalized)
            
        Example:
            categories = collection.get_categories()
            # ['Pan', 'Salchicha', 'Toppings', 'Salsa', 'Acompañante']
        """
        categories = set()
        
        for entity in self._items.values():
            categories.add(entity.entity_type)
        
        return sorted(list(categories))
    
    def count_by_category(self, categoria: str) -> int:
        """
        Count how many ingredients exist in a specific category.
        
        Args:
            categoria: Category name (e.g., 'Pan')
        
        Returns:
            Number of ingredients in that category
            
        Example:
            num_panes = collection.count_by_category('Pan')
            print(f"Hay {num_panes} tipos de pan")
        """
        return len(self.get_by_category(categoria))
    
    def get_category_stats(self) -> Dict[str, int]:
        """
        Get statistics of how many ingredients exist per category.
        
        Returns:
            Dict mapping category names to counts
            
        Example:
            stats = collection.get_category_stats()
            # {'Pan': 2, 'Salchicha': 3, 'Toppings': 5, ...}
            
            for categoria, count in stats.items():
                print(f"{categoria}: {count}")
        """
        stats = {}
        
        for categoria in self.get_categories():
            stats[categoria] = self.count_by_category(categoria)
        
        return stats
    
    def delete_category(self, categoria: str) -> int:
        """
        Delete all ingredients in a specific category.
        
        Args:
            categoria: Category name (e.g., 'Pan')
        
        Returns:
            Number of ingredients deleted
            
        Example:
            deleted = collection.delete_category('Toppings')
            print(f"Eliminados {deleted} toppings")
        """
        entity_type = categoria.capitalize()
        return self.delete_where(entity_type=entity_type)
    
    # ────────────────────────────────────────────────────────────
    # Validation Helpers
    # ────────────────────────────────────────────────────────────
    
    def validate_unique_name(self, nombre: str, categoria: str, 
                           exclude_id: Optional[str] = None) -> None:
        """
        Validate that an ingredient name is unique within its category.
        
        This is typically called before adding or updating an ingredient
        to ensure name uniqueness constraints.
        
        Args:
            nombre: Name to validate
            categoria: Category to check in
            exclude_id: Optional ID to exclude from check (for updates)
        
        Raises:
            ValueError: If name already exists in that category
            
        Example:
            # Before adding
            collection.validate_unique_name('simple', 'Pan')
            
            # Before updating (exclude current entity)
            collection.validate_unique_name('simple', 'Pan', exclude_id=pan.id)
        """
        existing = self.get_by_name(nombre, categoria)
        
        if existing and existing.id != exclude_id:
            raise ValueError(
                f"Ya existe un {categoria} llamado '{nombre}'"
            )
    
    def __repr__(self) -> str:
        """
        Get a detailed string representation of the collection.
        
        Returns:
            String showing collection stats and dirty state
        """
        dirty_marker = " (*)" if self._dirty else ""
        stats = self.get_category_stats()
        stats_str = ", ".join(f"{k}={v}" for k, v in stats.items())
        
        return (
            f"IngredientCollection(total={len(self._items)}, "
            f"categories=[{stats_str}]{dirty_marker})"
        )
