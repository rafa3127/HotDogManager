"""
Venta Collection Module

Provides VentaCollection for managing sales/orders with FLAT structure.

The VentaCollection handles sales records stored as a flat list of Venta entities.
Each venta contains an array of items (hot dogs ordered).

Author: Rafael Correa
Date: November 16, 2025
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from models.collections.base_collection import BaseCollection
from models import create_venta_entities


class VentaCollection(BaseCollection):
    """
    Collection for managing Venta (sales/orders) entities.
    
    Structure: FLAT - List of Venta objects
    
    Each Venta has:
        - id: Unique identifier
        - fecha: ISO datetime string
        - items: List of dicts with {hotdog_id, hotdog_nombre, cantidad}
    
    Example data structure:
        [
            {
                "id": "venta-001",
                "fecha": "2024-11-16T14:30:00",
                "items": [
                    {
                        "hotdog_id": "hotdog-simple",
                        "hotdog_nombre": "simple",
                        "cantidad": 2
                    }
                ]
            }
        ]
    """
    
    def __init__(self, data_source):
        """
        Initialize VentaCollection.
        
        Args:
            data_source: DataSourceClient instance for persistence
        """
        # Create Venta entity class
        venta_entities = create_venta_entities()
        self._venta_class = venta_entities['Venta']
        
        super().__init__(
            data_source=data_source,
            source_name='ventas'
        )
    
    # ════════════════════════════════════════════════════════════════════
    # ABSTRACT METHODS IMPLEMENTATION
    # ════════════════════════════════════════════════════════════════════
    
    def _load(self):
        """Load ventas from FLAT structure into internal dict."""
        raw_data = self._data_source.get(self._source_name)
        
        if not raw_data:
            # No ventas yet, start with empty collection
            return
        
        for venta_data in raw_data:
            # Filter out entity_type if present (from previous saves)
            clean_data = {k: v for k, v in venta_data.items() if k != 'entity_type'}
            
            # Create Venta entity
            venta = self._venta_class(**clean_data, entity_type='Venta')
            
            # Store in internal dict
            self._items[venta.id] = venta
    
    def _prepare_for_save(self) -> List[Dict]:
        """Prepare ventas for saving as FLAT list."""
        # Simply convert all entities to dicts
        return [venta.to_dict() for venta in self._items.values()]
    
    # ════════════════════════════════════════════════════════════════════
    # DOMAIN-SPECIFIC QUERY METHODS
    # ════════════════════════════════════════════════════════════════════
    
    def get_by_date(self, fecha: str) -> List[Any]:
        """
        Get all ventas for a specific date.
        
        Args:
            fecha: Date string (can be just date part: '2024-11-16')
        
        Returns:
            List of Venta entities matching the date
        
        Example:
            >>> ventas = collection.get_by_date('2024-11-16')
            >>> print(f"Found {len(ventas)} ventas on that date")
        """
        return [
            venta for venta in self._items.values()
            if hasattr(venta, 'fecha') and venta.fecha.startswith(fecha)
        ]
    
    def get_by_date_range(self, fecha_inicio: str, fecha_fin: str) -> List[Any]:
        """
        Get ventas within a date range (inclusive).
        
        Args:
            fecha_inicio: Start date (ISO format)
            fecha_fin: End date (ISO format)
        
        Returns:
            List of Venta entities in the range
        
        Example:
            >>> ventas = collection.get_by_date_range('2024-11-01', '2024-11-30')
            >>> print(f"November had {len(ventas)} ventas")
        """
        return [
            venta for venta in self._items.values()
            if hasattr(venta, 'fecha') and fecha_inicio <= venta.fecha <= fecha_fin
        ]
    
    def get_by_hotdog(self, hotdog_id: str) -> List[Any]:
        """
        Get all ventas that include a specific hot dog.
        
        Args:
            hotdog_id: ID of the hot dog to search for
        
        Returns:
            List of Venta entities containing that hot dog
        
        Example:
            >>> ventas = collection.get_by_hotdog('hotdog-simple')
            >>> print(f"Hot dog 'simple' appears in {len(ventas)} ventas")
        """
        matching_ventas = []
        
        for venta in self._items.values():
            if hasattr(venta, 'items'):
                for item in venta.items:
                    if item.get('hotdog_id') == hotdog_id:
                        matching_ventas.append(venta)
                        break  # Don't add same venta multiple times
        
        return matching_ventas
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about ventas.
        
        Returns:
            Dict with statistics:
                - total: Total number of ventas
                - total_items: Total items sold across all ventas
                - promedio_items_por_venta: Average items per venta
        
        Example:
            >>> stats = collection.get_stats()
            >>> print(f"Total ventas: {stats['total']}")
            >>> print(f"Avg items per venta: {stats['promedio_items_por_venta']:.2f}")
        """
        total_ventas = len(self._items)
        
        if total_ventas == 0:
            return {
                'total': 0,
                'total_items': 0,
                'promedio_items_por_venta': 0.0
            }
        
        total_items = 0
        for venta in self._items.values():
            if hasattr(venta, 'items'):
                total_items += len(venta.items)
        
        return {
            'total': total_ventas,
            'total_items': total_items,
            'promedio_items_por_venta': total_items / total_ventas if total_ventas > 0 else 0.0
        }
    
    
    def __repr__(self) -> str:
        """String representation showing total ventas and dirty status."""
        dirty_marker = " (*)" if self._dirty else ""
        return f"VentaCollection(total={len(self._items)}{dirty_marker})"
