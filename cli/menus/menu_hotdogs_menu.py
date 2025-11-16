"""
Menu definition for Hot Dog menu management.

Author: Rafael Correa
Date: November 16, 2025
"""

from cli.core import MenuDefinition, MenuOption
from cli.actions import (
    action_list_hotdogs,
    action_check_hotdog_availability,
    action_add_hotdog,
    action_delete_hotdog,
)


def create_menu_hotdogs_menu() -> MenuDefinition:
    """
    Creates the menu for hot dog management.
    
    Returns:
        MenuDefinition for hot dog management
    """
    return MenuDefinition(
        id='menu',
        title='🌭 GESTIÓN DEL MENÚ',
        description='Administra los hot dogs del menú',
        options=[
            MenuOption(
                key='1',
                label='Ver lista de hot dogs',
                action=action_list_hotdogs
            ),
            MenuOption(
                key='2',
                label='Verificar disponibilidad de hot dog',
                action=action_check_hotdog_availability
            ),
            MenuOption(
                key='3',
                label='Agregar hot dog',
                action=action_add_hotdog
            ),
            MenuOption(
                key='4',
                label='Eliminar hot dog',
                action=action_delete_hotdog,
                requires_confirm=False
            ),
        ],
        parent_menu='main',
        auto_add_back=True,
        auto_add_exit=True,
        clear_screen=True
    )
