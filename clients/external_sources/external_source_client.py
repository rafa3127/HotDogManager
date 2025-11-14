# clients/external_sources/external_source_client.py

"""
Abstract base class for external data source clients.

Author: Rafael Correa
Date: November 12, 2025
Updated: November 14, 2025 - Added ID contract documentation
"""

from abc import ABC, abstractmethod
from typing import Any


class ExternalSourceClient(ABC):
    """
    Abstract base class that defines the interface for external data sources.
    
    All external source clients (GitHub, MongoDB, REST APIs, etc.) must inherit
    from this class and implement the fetch_data method.
    
    CONTRACT - Data Format:
    ----------------------
    All implementations MUST ensure that returned data includes unique IDs.
    
    - Each data item must have an 'id' field containing a unique identifier
    - IDs should be stable (same item = same ID across fetches)
    - ID format: UUID string (e.g., 'a1b2c3d4-e5f6-7890-abcd-ef1234567890')
    
    For external sources that don't natively provide IDs:
    - Use IDAdapter to wrap the source
    - IDAdapter will handle ID generation automatically
    
    Example:
        >>> # Raw source without IDs
        >>> github = GitHubClient(owner='user', repo='data')
        >>> 
        >>> # Wrap with adapter to ensure IDs
        >>> from clients.adapters import IDAdapter
        >>> from clients.id_processors import process_grouped_structure_ids
        >>> adapted = IDAdapter(github, process_grouped_structure_ids)
        >>> 
        >>> # Now guaranteed to have IDs
        >>> data = adapted.fetch_data('ingredientes.json')
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
            MUST include 'id' field in each data item
        
        Raises:
            Exception: Implementation-specific exceptions for fetch failures
        """
        pass