"""
Adapters for external data sources.

Adapters wrap ExternalSourceClients to add functionality like:
- Adding stable IDs to data
- Normalizing dictionary keys
- Transforming data formats
- Validating data schemas

Author: Rafael Correa
Date: November 14, 2025
"""

from .id_adapter import IDAdapter
from .key_normalization_adapter import KeyNormalizationAdapter

__all__ = ['IDAdapter', 'KeyNormalizationAdapter']
