"""
Menu definitions package.

Exports all menu creation functions for the CLI.

Author: Rafael Correa
Date: November 16, 2025
"""

from .main_menu import create_main_menu
from .not_found_menu import create_not_found_menu
from .ingredientes_menu import create_ingredients_menu
from .menu_hotdogs_menu import create_menu_hotdogs_menu
from .ventas_menu import create_ventas_menu
from .debug_menu import create_debug_menu

__all__ = [
    'create_main_menu',
    'create_not_found_menu',
    'create_ingredients_menu',
    'create_menu_hotdogs_menu',
    'create_ventas_menu',
    'create_debug_menu',
]
