"""
Main menu definition.

This is the entry point of the CLI application.
Provides access to all main modules of the system.

Author: Rafael Correa
Date: November 16, 2025
"""

from cli.core import MenuDefinition, MenuOption


def create_main_menu() -> MenuDefinition:
    """
    Creates the main menu definition.
    
    This is the entry point of the application, providing access to:
    - Ingredient Management
    - Menu Management (Hot Dogs)
    - Sales Management (Ventas)
    
    Returns:
        MenuDefinition for the main menu
    """
    return MenuDefinition(
        id='main',
        title='🌭 HOT DOG CCS - SISTEMA DE GESTIÓN',
        description='Sistema de administración para cadena de hot dogs en Caracas',
        options=[
            # ──────────────────────────────────────────────────────
            # Module 1: Ingredient Management
            # ──────────────────────────────────────────────────────
            MenuOption(
                key='1',
                label='📦 Gestión de Ingredientes',
                navigate_to='ingredients'
            ),
            
            # ──────────────────────────────────────────────────────
            # Module 2: Menu Management (Hot Dogs)
            # ──────────────────────────────────────────────────────
            MenuOption(
                key='2',
                label='🌭 Gestión del Menú',
                navigate_to='menu'
            ),
            
            # ──────────────────────────────────────────────────────
            # Module 3: Sales Management
            # ──────────────────────────────────────────────────────
            MenuOption(
                key='3',
                label='💰 Gestión de Ventas',
                navigate_to='ventas'
            ),
            
            # ──────────────────────────────────────────────────────
            # Module 4 (Bonus): Statistics and Reports
            # ──────────────────────────────────────────────────────
            MenuOption(
                key='4',
                label='📊 Reportes y Estadísticas',
                navigate_to='reportes'
            ),
            
            # ──────────────────────────────────────────────────────
            # Debug Menu
            # ──────────────────────────────────────────────────────
            MenuOption(
                key='9',
                label='🔧 Debug / Diagnostics',
                navigate_to='debug'
            ),
        ],
        parent_menu=None,  # No parent - this is the root
        auto_add_back=False,  # No back option (root menu)
        auto_add_exit=True,  # Router adds exit option automatically
        clear_screen=True
    )
