# clients/external_sources/external_source_client.py
"""
Abstract base class for external data source clients.

Author: Rafael Correa
Date: November 12, 2025
"""

from abc import ABC, abstractmethod
from typing import Any


class ExternalSourceClient(ABC):
    """
    Abstract base class that defines the interface for external data sources.
    
    All external source clients (GitHub, MongoDB, REST APIs, etc.) must inherit
    from this class and implement the fetch_data method.
    """
    
    @abstractmethod
    def fetch_data(self, identifier: str, **kwargs) -> Any:
        """
        Fetch data from the external source.
        
        Args:
            identifier: Primary identifier for the data (e.g., file path, collection name, endpoint)
            **kwargs: Additional configuration parameters specific to the implementation
        
        Returns:
            The fetched data (typically dict or list that can be JSON serialized)
        
        Raises:
            Exception: Implementation-specific exceptions for fetch failures
        """
        pass