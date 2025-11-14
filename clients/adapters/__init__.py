"""
Adapters for external data sources.

Adapters wrap external sources to add additional functionality
while maintaining the ExternalSourceClient interface.
"""

from clients.adapters.id_adapter import IDAdapter

__all__ = ['IDAdapter']
