"""
Menu definitions package.

Exports all menu creation functions for the CLI.

Author: Rafael Correa
Date: November 16, 2025
"""

from .main_menu import create_main_menu
from .not_found_menu import create_not_found_menu

__all__ = [
    'create_main_menu',
    'create_not_found_menu',
]
