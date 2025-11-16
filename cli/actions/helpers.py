"""
Helper functions for CLI actions.

Utilities for common tasks like category normalization,
formatting, and conversions.

Author: Rafael Correa
Date: November 16, 2025
"""

from typing import Dict, List


# ──────────────────────────────────────────────────────
# CATEGORY NORMALIZATION
# ──────────────────────────────────────────────────────

CATEGORY_DISPLAY_NAMES: Dict[str, str] = {
    'pan': 'Pan',
    'salchicha': 'Salchicha',
    'acompañante': 'Acompañante',
    'acompanante': 'Acompañante',
    'salsa': 'Salsa',
    'toppings': 'Toppings'
}

# Mapping from display names to entity class names
CATEGORY_TO_CLASS: Dict[str, str] = {
    'Pan': 'Pan',
    'Salchicha': 'Salchicha',
    'Acompañante': 'Acompanante',  
    'Salsa': 'Salsa',
    'Toppings': 'Toppings'
}


def get_display_categories(handler) -> List[str]:
    """
    Get list of categories with display names.
    
    Returns categories from handler but with proper display names
    (including special characters like ñ).
    
    Args:
        handler: DataHandler instance
        
    Returns:
        List of category display names
    """
    raw_categories = handler.ingredientes.get_categories()
    
    # Convert to display names
    display_categories = []
    for cat in raw_categories:
        # Try to get display name, fallback to original
        display_name = CATEGORY_DISPLAY_NAMES.get(cat.lower(), cat)
        if display_name not in display_categories:
            display_categories.append(display_name)
    
    return sorted(display_categories)


def normalize_category_input(user_input: str) -> str:
    """
    Normalize user input for category to class name.
    
    Handles:
    - Case insensitivity
    - With/without accents (ñ)
    - Proper capitalization
    
    Args:
        user_input: Raw input from user
        
    Returns:
        Normalized category name for use with handler/service
        
    Examples:
        >>> normalize_category_input('acompañante')
        'Acompanante'
        >>> normalize_category_input('ACOMPAÑANTE')
        'Acompanante'
        >>> normalize_category_input('acompanante')
        'Acompanante'
    """
    # Normalize to lowercase
    normalized = user_input.lower().strip()
    
    # Map to display name first
    display_name = CATEGORY_DISPLAY_NAMES.get(normalized, user_input.capitalize())
    
    # Map display name to class name (handles ñ → n)
    class_name = CATEGORY_TO_CLASS.get(display_name, display_name)
    
    return class_name


def get_category_class_name(display_name: str) -> str:
    """
    Get entity class name from display name.
    
    Args:
        display_name: Display name (e.g., 'Acompañante')
        
    Returns:
        Class name (e.g., 'Acompanante')
    """
    return CATEGORY_TO_CLASS.get(display_name, display_name)


# ──────────────────────────────────────────────────────
# CATEGORY REQUIREMENTS
# ──────────────────────────────────────────────────────

def get_required_fields_for_category(categoria_class: str) -> List[str]:
    """
    Get list of required fields for a category.
    
    Args:
        categoria_class: Class name (e.g., 'Pan', 'Acompanante')
        
    Returns:
        List of required field names beyond 'tipo' and 'stock'
        
    Examples:
        >>> get_required_fields_for_category('Pan')
        ['tamano', 'unidad']
        >>> get_required_fields_for_category('Salsa')
        ['base', 'color']
    """
    # Categories that need size fields
    if categoria_class in ['Pan', 'Salchicha', 'Acompanante']:
        return ['tamano', 'unidad']
    
    # Salsa has different fields
    if categoria_class == 'Salsa':
        return ['base', 'color']
    
    # Toppings has presentacion
    if categoria_class == 'Toppings':
        return ['presentacion']
    
    return []
