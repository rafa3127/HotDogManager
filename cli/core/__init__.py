"""
Core components for the CLI system.

This module provides the foundational building blocks for creating
interactive command-line interfaces with routing, menus, and actions.

Author: Rafael Correa
Date: November 16, 2025
"""

from .colors import Colors
from .action_result import ActionResult
from .menu_definition import MenuDefinition, MenuOption
from .views import Views
from .router import MenuRouter

__all__ = [
    'Colors',
    'ActionResult',
    'MenuDefinition',
    'MenuOption',
    'Views',
    'MenuRouter',
]
