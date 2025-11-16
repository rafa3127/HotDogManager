"""
Data source client that manages fetching from external sources with local file fallback.

Author: Rafael Correa
Date: November 12, 2025
"""

import json
import os
from typing import Any, Dict
from clients.external_sources.external_source_client import ExternalSourceClient


class DataSourceClient:
    """
    Manages data retrieval from external sources with local file cache/fallback.
    All files are stored as {name}.json in the data directory.
    
    Each data source can have its own external client (GitHub, Mongo, BigQuery, etc.).
    
    TODO: Refactor to accept Collection objects instead of dict when Collections are implemented.
          Collections will encapsulate their name, external source, and other metadata.
    """
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the data source client.
        
        Args:
            data_dir: Directory for local JSON files (default: "data")
        """
        self.data_dir = data_dir
        self._data_store = {}  # In-memory storage: {name: data}
        self._external_sources = {}  # Maps source name to its external client
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
    
    def initialize(
        self, 
        sources: Dict[str, ExternalSourceClient], # Will be a collection's list later
        force_external: bool = False
    ) -> None:
        """
        Initialize data sources. Tries local first, falls back to external source.
        
        Args:
            sources: Dict mapping source names to their external clients
                    e.g., {'ingredientes': github_client, 'ventas': mongo_client}
            force_external: If True, ignores local files and fetches from external sources
        """
        for name, external_client in sources.items():
            # Store the external client for this source
            self._external_sources[name] = external_client
            
            try:
                if force_external:
                    # Force fetch from external source
                    data = self._fetch_from_external(name)
                else:
                    # Try local first
                    try:
                        data = self._load_local(name)
                    except FileNotFoundError:
                        # Local doesn't exist, fetch from external source
                        print(f"⚠️  No local file for {name}, fetching from external source...")
                        data = self._fetch_from_external(name)
                
                # Store in memory
                self._data_store[name] = data
                print(f"✅ Initialized {name}")
                
            except Exception as e:
                print(f"❌ Failed to initialize {name}: {e}")
                raise
    
    def get(self, name: str) -> Any:
        """
        Get data by name from in-memory store.
        
        Args:
            name: Data identifier (e.g., 'ingredientes', 'menu')
        
        Returns:
            The data (list or dict)
        
        Raises:
            KeyError: If the data source wasn't initialized
        """
        if name not in self._data_store:
            raise KeyError(f"Data source '{name}' not initialized. Call initialize() first.")
        
        return self._data_store[name]
    
    def save(self, name: str, data: Any) -> None:
        """
        Save data to in-memory store and persist to local file.
        
        Args:
            name: Data identifier (e.g., 'ingredientes', 'menu')
            data: Data to save (must be JSON serializable)
        """
        # Update in-memory
        self._data_store[name] = data
        
        # Persist to file
        self._save_local(name, data)
    
    def _fetch_from_external(self, name: str) -> Any:
        """
        Fetch data from external source and save locally.
        
        Args:
            name: Data source name
        
        Returns:
            The fetched data
        
        Raises:
            KeyError: If external source for this name wasn't registered
        """
        if name not in self._external_sources:
            raise KeyError(f"No external source registered for '{name}'")
        
        external_client = self._external_sources[name]
        filename = f"{name}.json"
        data = external_client.fetch_data(filename)
        self._save_local(name, data)
        return data
    
    def _load_local(self, name: str) -> Any:
        """Load data from local JSON file."""
        filepath = os.path.join(self.data_dir, f"{name}.json")
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Local file not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_local(self, name: str, data: Any) -> None:
        """Save data to local JSON file."""
        filepath = os.path.join(self.data_dir, f"{name}.json")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)