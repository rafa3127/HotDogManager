"""
GitHub client for downloading files from repositories.

Author: Rafael Correa
Date: November 12, 2025
"""

import requests
from typing import Any
from clients.external_sources.external_source_client import ExternalSourceClient


class GitHubClient(ExternalSourceClient):
    """Client for downloading JSON files from GitHub repositories."""
    
    def __init__(self, owner: str, repo: str, branch: str = "main"):
        """
        Initialize the GitHub client.
        
        Args:
            owner: Repository owner (user or organization)
            repo: Repository name
            branch: Repository branch (default: main)
        """
        self.owner = owner
        self.repo = repo
        self.branch = branch
        self.base_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}"
    
    def fetch_data(self, identifier: str, **kwargs) -> Any:
        """
        Download a JSON file from the repository.
        
        Args:
            identifier: File path in the repository (e.g., "ingredientes.json")
            **kwargs: Additional parameters (timeout, etc.)
        
        Returns:
            The parsed JSON data (dict or list)
        
        Raises:
            requests.RequestException: If there's a network error
            ValueError: If the content is not valid JSON
        """
        timeout = kwargs.get('timeout', 10)
        url = f"{self.base_url}/{identifier}"
        
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()  # Raises exception if status != 200
            return response.json()
        except requests.RequestException as e:
            raise requests.RequestException(f"Error downloading {identifier}: {e}")
        except ValueError as e:
            raise ValueError(f"File {identifier} does not contain valid JSON: {e}")