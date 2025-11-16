"""
Models package.

Provides functions to create entity classes dynamically based on data schemas.

Author: Rafael Correa
Date: November 13, 2025
"""

from models.entities.ingredients import create_ingredient_entities
from models.entities.hotdogs import create_hotdog_entities

__all__ = [
    'create_ingredient_entities',
    'create_hotdog_entities'
]