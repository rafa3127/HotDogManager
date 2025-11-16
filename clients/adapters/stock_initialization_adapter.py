"""
Stock Initialization Adapter

Adds a 'stock' field to all ingredient items with a default initial value.
This adapter is specifically designed for the GROUPED structure (ingredientes.json).

Author: Rafael Correa
Date: November 15, 2025
"""

from typing import Any, Dict, List
from clients.external_sources.external_source_client import ExternalSourceClient


class StockInitializationAdapter(ExternalSourceClient):
    """
    Adapter that adds stock field to all ingredients.
    
    This adapter wraps another ExternalSourceClient and adds a 'stock' field
    to each ingredient option with a configurable initial value.
    
    Designed for GROUPED structure (categories with options).
    """
    
    def __init__(
        self,
        external_source: ExternalSourceClient,
        default_stock: int = 0,
        stock_by_category: Dict[str, int] = None
    ):
        """
        Initialize the Stock Initialization Adapter.
        
        Args:
            external_source: The wrapped external source client
            default_stock: Default stock value for all ingredients (default: 0)
            stock_by_category: Optional dict to set different stock per category
                              e.g., {'pan': 100, 'salchicha': 50}
                              If not provided, uses default_stock for all
        
        Example:
            >>> github = GitHubClient(...)
            >>> with_ids = IDAdapter(github, processor)
            >>> with_stock = StockInitializationAdapter(
            ...     with_ids,
            ...     default_stock=50,
            ...     stock_by_category={'pan': 100, 'salchicha': 75}
            ... )
        """
        self.external_source = external_source
        self.default_stock = default_stock
        self.stock_by_category = stock_by_category or {}
    
    def fetch_data(self, identifier: str, **kwargs) -> Any:
        """
        Fetch data and add stock field to all ingredient options.
        
        Args:
            identifier: Data identifier (e.g., 'ingredientes.json')
            **kwargs: Additional arguments passed to wrapped source
        
        Returns:
            Data with stock field added to each ingredient option
        """
        # Fetch data from wrapped source
        data = self.external_source.fetch_data(identifier, **kwargs)
        
        # Only process if data is a list (GROUPED structure)
        if not isinstance(data, list):
            return data
        
        # Add stock to each ingredient
        return self._add_stock_to_data(data)
    
    def _add_stock_to_data(self, data: List[Dict]) -> List[Dict]:
        """
        Recursively add stock field to all ingredient options.
        
        Args:
            data: List of category dictionaries with opciones
        
        Returns:
            Same data structure with stock field added to each option
        """
        result = []
        
        for category_data in data:
            # Skip if not a dict
            if not isinstance(category_data, dict):
                result.append(category_data)
                continue
            
            # Copy category data
            category_copy = category_data.copy()
            
            # Get categoria (might be normalized or not)
            categoria = category_data.get('categoria') or category_data.get('Categoria', '')
            categoria_lower = categoria.lower()
            
            # Determine stock value for this category
            stock_value = self.stock_by_category.get(
                categoria_lower,
                self.default_stock
            )
            
            # Process opciones if they exist
            if 'opciones' in category_copy:
                opciones_with_stock = []
                
                for option in category_copy['opciones']:
                    if isinstance(option, dict):
                        # Copy option and add stock field
                        option_copy = option.copy()
                        
                        # Only add stock if it doesn't already exist
                        if 'stock' not in option_copy:
                            option_copy['stock'] = stock_value
                        
                        opciones_with_stock.append(option_copy)
                    else:
                        opciones_with_stock.append(option)
                
                category_copy['opciones'] = opciones_with_stock
            
            # Handle 'Opciones' (non-normalized) as well
            elif 'Opciones' in category_copy:
                opciones_with_stock = []
                
                for option in category_copy['Opciones']:
                    if isinstance(option, dict):
                        option_copy = option.copy()
                        
                        if 'stock' not in option_copy:
                            option_copy['stock'] = stock_value
                        
                        opciones_with_stock.append(option_copy)
                    else:
                        opciones_with_stock.append(option)
                
                category_copy['Opciones'] = opciones_with_stock
            
            result.append(category_copy)
        
        return result
