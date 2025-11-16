"""
Clients module - External data sources and adapters.

Author: Rafael Correa
Date: November 16, 2025
"""

from .data_source_client import DataSourceClient
from .external_sources import GitHubClient

__all__ = [
    'DataSourceClient',
    'GitHubClient',
]
