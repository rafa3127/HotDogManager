"""
Key Normalization Adapter for external data sources.

Wraps an ExternalSourceClient and normalizes all keys in the fetched data:
- Converts to lowercase
- Removes accents from vowels (á→a, é→e, í→i, ó→o, ú→u)
- Replaces ñ with n

This ensures consistent key naming across the entire application,
regardless of the original data source format.

Author: Rafael Correa
Date: November 14, 2025
"""

import unicodedata
from typing import Any, Dict, List
from clients.external_sources.external_source_client import ExternalSourceClient


def normalize_key(key: str) -> str:
    """
    Normalize a dictionary key to lowercase without accents or ñ.
    
    Transformations:
    - 'Categoría' → 'categoria'
    - 'Tamaño' → 'tamano'
    - 'Año' → 'ano'
    - 'NOMBRE' → 'nombre'
    
    Args:
        key: Original key string
    
    Returns:
        Normalized key
    
    Examples:
        >>> normalize_key('Categoría')
        'categoria'
        >>> normalize_key('Tamaño')
        'tamano'
        >>> normalize_key('Año')
        'ano'
    """
    # Replace ñ and Ñ explicitly (not handled by NFD decomposition)
    normalized = key.replace('ñ', 'n').replace('Ñ', 'n')
    
    # Decompose unicode characters (á → a + combining acute accent)
    normalized = unicodedata.normalize('NFD', normalized)
    
    # Remove combining characters (accents)
    normalized = ''.join(
        char for char in normalized 
        if unicodedata.category(char) != 'Mn'
    )
    
    # Convert to lowercase
    return normalized.lower()


def normalize_keys_recursive(data: Any) -> Any:
    """
    Recursively normalize all keys in nested dictionaries and lists.
    
    Handles:
    - Dictionaries: Normalizes all keys
    - Lists: Processes each item recursively
    - Primitives: Returns as-is
    
    Args:
        data: Data structure to normalize (dict, list, or primitive)
    
    Returns:
        Data with all keys normalized
    
    Examples:
        >>> normalize_keys_recursive({'Nombre': 'Juan', 'Año': 2024})
        {'nombre': 'Juan', 'ano': 2024}
        
        >>> normalize_keys_recursive([{'Tamaño': 6}, {'Tamaño': 9}])
        [{'tamano': 6}, {'tamano': 9}]
    """
    if isinstance(data, dict):
        # Normalize all keys in the dictionary
        return {
            normalize_key(key): normalize_keys_recursive(value)
            for key, value in data.items()
        }
    elif isinstance(data, list):
        # Process each item in the list
        return [normalize_keys_recursive(item) for item in data]
    else:
        # Primitive value (str, int, float, bool, None)
        return data


class KeyNormalizationAdapter(ExternalSourceClient):
    """
    Adapter that normalizes all keys in fetched data.
    
    This adapter:
    1. Delegates fetching to the wrapped external source
    2. Recursively normalizes all dictionary keys
    3. Returns data with consistent key naming
    
    Can be chained with other adapters:
        github = GitHubClient(...)
        with_ids = IDAdapter(github, processor)
        normalized = KeyNormalizationAdapter(with_ids)
    
    Example:
        >>> github = GitHubClient(owner='user', repo='data')
        >>> with_ids = IDAdapter(github, process_grouped_structure_ids)
        >>> normalized = KeyNormalizationAdapter(with_ids)
        >>> data = normalized.fetch_data('ingredientes.json')
        >>> # All keys are now lowercase without accents
    """
    
    def __init__(self, external_source: ExternalSourceClient):
        """
        Initialize the adapter.
        
        Args:
            external_source: The underlying external source (can be another adapter)
        
        Example:
            >>> # Chain with IDAdapter
            >>> github = GitHubClient(...)
            >>> with_ids = IDAdapter(github, processor)
            >>> adapter = KeyNormalizationAdapter(with_ids)
        """
        self.external_source = external_source
    
    def fetch_data(self, identifier: str, **kwargs) -> Any:
        """
        Fetch data and normalize all keys.
        
        This method:
        1. Delegates to the wrapped external source to fetch data
        2. Recursively normalizes all dictionary keys
        3. Returns data with consistent naming
        
        Args:
            identifier: Data identifier (e.g., 'ingredientes.json')
            **kwargs: Additional arguments passed to external source
        
        Returns:
            Data with all keys normalized
        
        Raises:
            Any exceptions from the underlying external source
        
        Example:
            >>> data = adapter.fetch_data('ingredientes.json')
            >>> # Keys like 'Categoría' are now 'categoria'
        """
        # Fetch data from external source (may already have IDs)
        raw_data = self.external_source.fetch_data(identifier, **kwargs)
        
        # Normalize all keys recursively
        normalized_data = normalize_keys_recursive(raw_data)
        
        # Optional: Log normalization
        print(f"🔤 Normalized keys in {identifier}")
        
        return normalized_data
