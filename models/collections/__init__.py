"""
Collections Module

This module provides collection classes for managing groups of entities
with CRUD operations and deferred persistence.

Collections implement the Repository Pattern, providing an abstraction layer
between the domain logic and data persistence. Each collection corresponds to
a data source and handles the conversion between the source's data structure
(GROUPED, FLAT, etc.) and the application's entity objects.

Classes:
    BaseCollection: Abstract base class for all collections
    IngredientCollection: Collection for ingredient entities (GROUPED structure)
    HotDogCollection: Collection for hot dog menu entities (FLAT structure)

Usage:
    from models.collections import IngredientCollection, HotDogCollection
    
    # Initialize collections
    ingredientes = IngredientCollection(data_source)
    menu = HotDogCollection(data_source)
    
    # Use CRUD operations
    panes = ingredientes.get_by_category('Pan')
    hotdog = menu.get_by_name('simple')
    
    # Persist changes
    if ingredientes.is_dirty:
        ingredientes.flush()

Author: Rafael Correa
Date: November 15, 2025
"""

from models.collections.base_collection import BaseCollection
from models.collections.ingredient_collection import IngredientCollection
from models.collections.hotdog_collection import HotDogCollection
from models.collections.venta_collection import VentaCollection

__all__ = [
    'BaseCollection',
    'IngredientCollection',
    'HotDogCollection',
    'VentaCollection',
]
