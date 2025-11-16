"""
ID Adapter for external data sources.

Wraps an ExternalSourceClient and ensures all fetched data includes IDs.
This allows external sources to remain simple (pure transport) while
guaranteeing that DataSourceClient always receives data with IDs.

Author: Rafael Correa
Date: November 14, 2025
"""

from typing import Any, Callable, Tuple
from clients.external_sources.external_source_client import ExternalSourceClient


class IDAdapter(ExternalSourceClient):
    """
    Adapter that wraps an external source and adds IDs to fetched data.
    
    This implements the Adapter Pattern to bridge between:
    - External sources that may not have IDs (e.g., GitHub JSON files)
    - DataSourceClient that expects all data to have IDs
    
    The adapter delegates the actual fetching to the wrapped source,
    then applies an ID processor to ensure IDs exist before returning.
    
    Example:
        >>> github = GitHubClient(owner='user', repo='data', branch='main')
        >>> adapted = IDAdapter(github, process_grouped_structure_ids)
        >>> data = adapted.fetch_data('ingredientes.json')
        >>> # data is guaranteed to have IDs
    """
    
    def __init__(
        self,
        external_source: ExternalSourceClient,
        id_processor: Callable[[Any], Tuple[Any, bool]]
    ):
        """
        Initialize the adapter.
        
        Args:
            external_source: The underlying external source (e.g., GitHubClient)
            id_processor: Function that adds IDs to the data structure.
                         Must have signature: (data) -> (processed_data, modified)
                         where modified is True if IDs were added.
        
        Example:
            >>> from clients.id_processors import process_grouped_structure_ids
            >>> github = GitHubClient(...)
            >>> adapter = IDAdapter(github, process_grouped_structure_ids)
        """
        self.external_source = external_source
        self.id_processor = id_processor
    
    def fetch_data(self, identifier: str, **kwargs) -> Any:
        """
        Fetch data from external source and ensure IDs exist.
        
        This method:
        1. Delegates to the wrapped external source to fetch raw data
        2. Applies the ID processor to add missing IDs
        3. Returns data with IDs guaranteed
        
        Args:
            identifier: Data identifier (e.g., 'ingredientes.json')
            **kwargs: Additional arguments passed to external source
        
        Returns:
            Data with IDs included
        
        Raises:
            Any exceptions from the underlying external source or ID processor
        
        Example:
            >>> data = adapter.fetch_data('ingredientes.json')
            >>> # All items in data now have 'id' field
        """
        # Fetch raw data from external source
        raw_data = self.external_source.fetch_data(identifier, **kwargs)
        
        # Apply ID processor
        processed_data, modified = self.id_processor(raw_data)
        
        # Optional: Log if IDs were added (useful for debugging)
        if modified:
            print(f"🆔 Added IDs to {identifier}")
        
        return processed_data