"""
Ingredients management menu.

Provides access to all ingredient-related operations:
- Listing by category and type
- Viewing inventory
- Adding/deleting ingredients
- Updating stock

Author: Rafael Correa
Date: November 16, 2025
"""

from cli.core import MenuDefinition, MenuOption
from cli.actions import (
    action_list_by_category,
    action_list_by_type,
    action_view_inventory,
    action_update_stock,
    action_add_ingredient,
    action_delete_ingredient,
)


def create_ingredients_menu() -> MenuDefinition:
    """
    Creates the ingredients management menu.
    
    Provides access to:
    - Listing ingredients (by category, by type)
    - Viewing full inventory
    - Adding new ingredients
    - Deleting ingredients (with validation)
    - Updating stock levels
    
    Returns:
        MenuDefinition for ingredients menu
    """
    return MenuDefinition(
        id='ingredients',
        title='📦 GESTIÓN DE INGREDIENTES',
        description='Administración del catálogo e inventario de ingredientes',
        options=[
            # ──────────────────────────────────────────────────────
            # Listing Options (Requirements 1 & 2)
            # ──────────────────────────────────────────────────────
            MenuOption(
                key='1',
                label='📋 Listar por Categoría',
                action=action_list_by_category
            ),
            
            MenuOption(
                key='2',
                label='🔍 Listar por Tipo',
                action=action_list_by_type
            ),
            
            # ──────────────────────────────────────────────────────
            # Inventory Options
            # ──────────────────────────────────────────────────────
            MenuOption(
                key='3',
                label='📊 Ver Inventario Completo',
                action=action_view_inventory
            ),
            
            MenuOption(
                key='4',
                label='📝 Actualizar Stock',
                action=action_update_stock
            ),
            
            # ──────────────────────────────────────────────────────
            # Add/Delete Options (Requirements 3 & 4)
            # ──────────────────────────────────────────────────────
            MenuOption(
                key='5',
                label='➕ Agregar Ingrediente',
                action=action_add_ingredient
            ),
            
            MenuOption(
                key='6',
                label='🗑️  Eliminar Ingrediente',
                action=action_delete_ingredient,
                requires_confirm=False  # Action handles confirmation internally
            ),
        ],
        parent_menu='main',
        auto_add_back=True,  # Auto-add back to main
        auto_add_exit=True,
        clear_screen=True
    )
