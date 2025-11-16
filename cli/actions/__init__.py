"""
Actions package.

Exports all action functions for the CLI.

Author: Rafael Correa
Date: November 16, 2025
"""

from .ingredientes_actions import (
    action_list_by_category,
    action_list_by_type,
    action_view_inventory,
    action_update_stock,
    action_add_ingredient,
    action_delete_ingredient,
)

__all__ = [
    # Ingredientes
    'action_list_by_category',
    'action_list_by_type',
    'action_view_inventory',
    'action_update_stock',
    'action_add_ingredient',
    'action_delete_ingredient',
]
