"""
HotDog Collection Module

This module provides the concrete collection implementation for hot dogs,
handling the FLAT data structure (simple list of items).

Classes:
    HotDogCollection: Collection for managing hot dog menu entities
Author: Rafael Correa
Date: November 15, 2025
"""

from typing import Optional, List
from models.collections.base_collection import BaseCollection
from models.core.base_entity import Entity


class HotDogCollection(BaseCollection):
    """
    Collection for managing hot dog menu entities.
    
    Handles the FLAT data structure where hot dogs are stored as a simple
    list of items, without any grouping or categorization.
    
    Data Structure (FLAT):
        [
            {
                "id": "...",
                "nombre": "simple",
                "pan": "simple",
                "salchicha": "weiner",
                "toppings": [],
                "salsas": [],
                "acompanante": null
            },
            {
                "id": "...",
                "nombre": "inglés",
                "pan": "integral",
                "salchicha": "breakfast",
                "toppings": ["cebolla"],
                "salsas": ["relish"],
                "acompanante": "Papas"
            }
        ]
    
    The collection converts this structure to/from a flat {id: Entity} dict
    for easy CRUD operations.
    
    Attributes:
        _hotdog_class: The HotDog entity class used to create instances
    """
    
    def __init__(self, data_source):
        """
        Initialize the hot dog collection.
        
        Args:
            data_source: DataSourceClient instance for persistence
        """
        # Store HotDog class (will be populated in _load)
        self._hotdog_class = None
        
        # Call parent constructor (which calls _load)
        super().__init__(data_source, 'menu')
    
    # ────────────────────────────────────────────────────────────
    # Abstract Methods Implementation
    # ────────────────────────────────────────────────────────────
    
    def _load(self) -> None:
        """
        Load hot dogs from data source and populate self._items.
        
        Process:
        1. Get raw data from data source (FLAT structure)
        2. Create HotDog entity class dynamically using schema inferred from data
        3. Convert FLAT list to {id: Entity} dict
        4. Store HotDog class for later use
        """
        # Get raw data (FLAT structure with IDs and normalized keys)
        raw_data = self._data_source.get(self._source_name)
        
        if not raw_data:
            # No data to load (empty collection)
            return
        
        # Create HotDog entity class dynamically from data
        from models.entities.hotdogs import create_hotdog_entities
        hotdog_classes = create_hotdog_entities(raw_data)
        self._hotdog_class = hotdog_classes['HotDog']
        
        # Convert FLAT list to {id: Entity} dict
        for item_data in raw_data:
            # Remove entity_type from data if present (will be added via parameter)
            # This handles the case where data was previously saved with entity_type
            clean_data = {k: v for k, v in item_data.items() if k != 'entity_type'}
            
            # Create HotDog instance
            entity = self._hotdog_class(**clean_data, entity_type='HotDog')
            
            # Add to internal storage
            self._items[entity.id] = entity
    
    def _prepare_for_save(self) -> List[dict]:
        """
        Convert internal {id: Entity} structure to FLAT list for saving.
        
        Process:
        1. Convert each entity to dict using to_dict()
        2. Return as simple list (FLAT structure)
        
        Returns:
            List of hot dog dicts in FLAT format
        """
        # Convert each entity to dict and return as list
        return [entity.to_dict() for entity in self._items.values()]
    
    # ────────────────────────────────────────────────────────────
    # Domain-Specific Methods
    # ────────────────────────────────────────────────────────────
    
    def get_by_name(self, nombre: str) -> Optional[Entity]:
        """
        Get a hot dog by its name.
        
        Hot dog names should be unique, so this returns the first match
        or None if not found.
        
        Args:
            nombre: Name of the hot dog (e.g., 'simple', 'inglés')
        
        Returns:
            HotDog entity if found, None otherwise
            
        Example:
            hotdog = collection.get_by_name('simple')
            if hotdog:
                print(f"Pan: {hotdog.pan}, Salchicha: {hotdog.salchicha}")
        """
        results = self.find(nombre=nombre)
        return results[0] if results else None
    
    def exists_by_name(self, nombre: str) -> bool:
        """
        Check if a hot dog with given name exists.
        
        Args:
            nombre: Name to check
        
        Returns:
            True if hot dog exists, False otherwise
            
        Example:
            if collection.exists_by_name('simple'):
                print("Hot dog 'simple' already exists")
        """
        return self.get_by_name(nombre) is not None
    
    def get_with_topping(self, topping: str) -> List[Entity]:
        """
        Get all hot dogs that include a specific topping.
        
        Args:
            topping: Name of the topping (e.g., 'cebolla', 'queso')
        
        Returns:
            List of hot dogs that contain this topping
            
        Example:
            hotdogs = collection.get_with_topping('cebolla')
            print(f"{len(hotdogs)} hot dogs incluyen cebolla")
        """
        results = []
        
        for hotdog in self._items.values():
            # Check if hotdog has toppings attribute and topping is in list
            if hasattr(hotdog, 'toppings') and topping in hotdog.toppings:
                results.append(hotdog)
        
        return results
    
    def get_with_salsa(self, salsa: str) -> List[Entity]:
        """
        Get all hot dogs that include a specific salsa.
        
        Args:
            salsa: Name of the salsa (e.g., 'mostaza', 'ketchup')
        
        Returns:
            List of hot dogs that contain this salsa
            
        Example:
            hotdogs = collection.get_with_salsa('mostaza')
            print(f"{len(hotdogs)} hot dogs incluyen mostaza")
        """
        results = []
        
        for hotdog in self._items.values():
            # Check if hotdog has salsas attribute and salsa is in list
            if hasattr(hotdog, 'salsas') and salsa in hotdog.salsas:
                results.append(hotdog)
        
        return results
    
    def get_combos(self) -> List[Entity]:
        """
        Get all hot dogs that are combos (have acompañante).
        
        Returns:
            List of hot dogs that include an acompañante
            
        Example:
            combos = collection.get_combos()
            print(f"Hay {len(combos)} combos disponibles")
        """
        results = []
        
        for hotdog in self._items.values():
            # Check if hotdog has acompañante and it's not None/empty
            if hasattr(hotdog, 'acompanante') and hotdog.acompanante:
                results.append(hotdog)
        
        return results
    
    def get_simple_hotdogs(self) -> List[Entity]:
        """
        Get all simple hot dogs (no toppings, no salsas, no acompañante).
        
        Returns:
            List of simple hot dogs
            
        Example:
            simple = collection.get_simple_hotdogs()
            print(f"Hay {len(simple)} hot dogs simples")
        """
        results = []
        
        for hotdog in self._items.values():
            is_simple = True
            
            # Check toppings
            if hasattr(hotdog, 'toppings') and hotdog.toppings:
                is_simple = False
            
            # Check salsas
            if hasattr(hotdog, 'salsas') and hotdog.salsas:
                is_simple = False
            
            # Check acompañante
            if hasattr(hotdog, 'acompanante') and hotdog.acompanante:
                is_simple = False
            
            if is_simple:
                results.append(hotdog)
        
        return results
    
    def get_by_pan_type(self, pan: str) -> List[Entity]:
        """
        Get all hot dogs that use a specific type of pan.
        
        Args:
            pan: Name of the pan type (e.g., 'simple', 'integral')
        
        Returns:
            List of hot dogs using this pan
            
        Example:
            hotdogs = collection.get_by_pan_type('integral')
            print(f"{len(hotdogs)} hot dogs usan pan integral")
        """
        return self.find(pan=pan)
    
    def get_by_salchicha_type(self, salchicha: str) -> List[Entity]:
        """
        Get all hot dogs that use a specific type of salchicha.
        
        Args:
            salchicha: Name of the salchicha type (e.g., 'weiner', 'breakfast')
        
        Returns:
            List of hot dogs using this salchicha
            
        Example:
            hotdogs = collection.get_by_salchicha_type('weiner')
            print(f"{len(hotdogs)} hot dogs usan salchicha weiner")
        """
        return self.find(salchicha=salchicha)
    
    # ────────────────────────────────────────────────────────────
    # Validation Helpers
    # ────────────────────────────────────────────────────────────
    
    def validate_unique_name(self, nombre: str, exclude_id: Optional[str] = None) -> None:
        """
        Validate that a hot dog name is unique.
        
        This is typically called before adding or updating a hot dog
        to ensure name uniqueness constraints.
        
        Args:
            nombre: Name to validate
            exclude_id: Optional ID to exclude from check (for updates)
        
        Raises:
            ValueError: If name already exists
            
        Example:
            # Before adding
            collection.validate_unique_name('super perro')
            
            # Before updating (exclude current entity)
            collection.validate_unique_name('simple', exclude_id=hotdog.id)
        """
        existing = self.get_by_name(nombre)
        
        if existing and existing.id != exclude_id:
            raise ValueError(
                f"Ya existe un hot dog llamado '{nombre}'"
            )
    
    def validate_ingredients_exist(self, pan: str, salchicha: str, 
                                   toppings: List[str], salsas: List[str],
                                   acompanante: Optional[str],
                                   ingredient_collection) -> None:
        """
        Validate that all ingredients referenced in a hot dog exist.
        
        This ensures referential integrity between hot dogs and ingredients.
        
        Args:
            pan: Pan name
            salchicha: Salchicha name
            toppings: List of topping names
            salsas: List of salsa names
            acompanante: Acompañante name (optional)
            ingredient_collection: IngredientCollection to check against
        
        Raises:
            ValueError: If any ingredient doesn't exist
            
        Example:
            collection.validate_ingredients_exist(
                pan='simple',
                salchicha='weiner',
                toppings=['cebolla'],
                salsas=['mostaza'],
                acompanante='Papas',
                ingredient_collection=ingredientes
            )
        """
        # Validate pan
        if not ingredient_collection.exists_in_category(pan, 'Pan'):
            raise ValueError(f"Pan '{pan}' no existe en ingredientes")
        
        # Validate salchicha
        if not ingredient_collection.exists_in_category(salchicha, 'Salchicha'):
            raise ValueError(f"Salchicha '{salchicha}' no existe en ingredientes")
        
        # Validate toppings
        for topping in toppings:
            if not ingredient_collection.exists_in_category(topping, 'Toppings'):
                raise ValueError(f"Topping '{topping}' no existe en ingredientes")
        
        # Validate salsas
        for salsa in salsas:
            if not ingredient_collection.exists_in_category(salsa, 'Salsa'):
                raise ValueError(f"Salsa '{salsa}' no existe en ingredientes")
        
        # Validate acompañante (optional)
        if acompanante:
            if not ingredient_collection.exists_in_category(acompanante, 'Acompañante'):
                raise ValueError(f"Acompañante '{acompanante}' no existe en ingredientes")
    
    # ────────────────────────────────────────────────────────────
    # Statistics
    # ────────────────────────────────────────────────────────────
    
    def get_stats(self) -> dict:
        """
        Get statistics about the hot dog menu.
        
        Returns:
            Dict with various statistics
            
        Example:
            stats = collection.get_stats()
            print(f"Total: {stats['total']}")
            print(f"Combos: {stats['combos']}")
            print(f"Simples: {stats['simples']}")
        """
        return {
            'total': len(self._items),
            'combos': len(self.get_combos()),
            'simples': len(self.get_simple_hotdogs()),
            'con_toppings': sum(1 for hd in self._items.values() 
                               if hasattr(hd, 'toppings') and hd.toppings),
            'con_salsas': sum(1 for hd in self._items.values() 
                             if hasattr(hd, 'salsas') and hd.salsas),
        }
    
    def __repr__(self) -> str:
        """
        Get a detailed string representation of the collection.
        
        Returns:
            String showing collection stats and dirty state
        """
        dirty_marker = " (*)" if self._dirty else ""
        stats = self.get_stats()
        
        return (
            f"HotDogCollection(total={stats['total']}, "
            f"combos={stats['combos']}, simples={stats['simples']}{dirty_marker})"
        )
