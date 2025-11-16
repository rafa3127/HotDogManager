"""
External data sources module.

Author: Rafael Correa
Date: November 14, 2025
"""

from .external_source_client import ExternalSourceClient
from .github_client import GitHubClient

__all__ = [
    'ExternalSourceClient',
    'GitHubClient',
]
