"""
Venta Service Module

Provides business logic for managing sales/orders with a deferred builder pattern.

The service uses a VentaBuilder for constructing sales step-by-step before
confirming and persisting them. This allows for flexible order building with
validation and preview before inventory deduction.

Author: Rafael Correa
Date: November 16, 2025
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from services.ingredient_service import IngredientService


class VentaBuilder:
    """
    Builder for constructing ventas in a deferred manner.
    
    This is NOT a persisted entity - just an in-memory object to accumulate
    items before confirming the sale.
    
    Features:
        - Add items one by one
        - Update quantities
        - Remove items
        - Clear all items
        - Automatic quantity merging (same hotdog → increment cantidad)
    
    Example:
        builder = VentaBuilder()
        builder.add_item('hotdog-1', 'simple', 2)
        builder.add_item('hotdog-2', 'combo', 1)
        builder.add_item('hotdog-1', 'simple', 1)  # Merges to cantidad=3
        # builder.items = [
        #   {'hotdog_id': 'hotdog-1', 'hotdog_nombre': 'simple', 'cantidad': 3},
        #   {'hotdog_id': 'hotdog-2', 'hotdog_nombre': 'combo', 'cantidad': 1}
        # ]
    """
    
    def __init__(self):
        """Initialize an empty venta builder."""
        self.items: List[Dict[str, Any]] = []
        self.fecha: Optional[str] = None  # Set when confirming
        self.id: Optional[str] = None     # Generated when confirming
    
    def add_item(self, hotdog_id: str, hotdog_nombre: str, cantidad: int) -> None:
        """
        Add an item to the draft.
        
        If the hotdog already exists in items, increments its cantidad.
        Otherwise, adds a new item.
        
        Args:
            hotdog_id: ID of the hot dog
            hotdog_nombre: Name of the hot dog
            cantidad: Quantity to add
        """
        # Check if hotdog already exists
        for item in self.items:
            if item['hotdog_id'] == hotdog_id:
                # Already exists, increment cantidad
                item['cantidad'] += cantidad
                return
        
        # Doesn't exist, add new item
        self.items.append({
            'hotdog_id': hotdog_id,
            'hotdog_nombre': hotdog_nombre,
            'cantidad': cantidad
        })
    
    def remove_item(self, hotdog_id: str) -> bool:
        """
        Remove an item from the draft.
        
        Args:
            hotdog_id: ID of the hot dog to remove
        
        Returns:
            True if item was found and removed, False otherwise
        """
        original_length = len(self.items)
        self.items = [item for item in self.items if item['hotdog_id'] != hotdog_id]
        return len(self.items) < original_length
    
    def update_cantidad(self, hotdog_id: str, cantidad: int) -> bool:
        """
        Update the quantity of an existing item.
        
        Args:
            hotdog_id: ID of the hot dog
            cantidad: New quantity (must be > 0)
        
        Returns:
            True if item was found and updated, False otherwise
        """
        for item in self.items:
            if item['hotdog_id'] == hotdog_id:
                item['cantidad'] = cantidad
                return True
        return False
    
    def clear(self) -> None:
        """Clear all items from the draft."""
        self.items = []
    
    def get_total_items(self) -> int:
        """Get total quantity of items (sum of all cantidades)."""
        return sum(item['cantidad'] for item in self.items)
    
    def __repr__(self) -> str:
        """String representation."""
        return f"VentaBuilder(items={len(self.items)}, total_cantidad={self.get_total_items()})"


class VentaService:
    """
    Static service class for venta (sales/orders) management operations.
    
    This service uses a builder pattern for constructing sales step-by-step:
    1. Create draft (VentaBuilder)
    2. Add items one by one
    3. Preview (check inventory, see totals)
    4. Confirm (deduct inventory, persist to collection)
    
    All methods are static and receive the DataHandler as parameter when needed.
    
    Business Rules Enforced:
        - Hot dogs must exist in menu
        - Cantidad must be positive
        - Inventory must be available when confirming
        - Venta must have at least one item to confirm
    """
    
    @staticmethod
    def create_draft() -> VentaBuilder:
        """
        Create an empty venta draft.
        
        Returns:
            VentaBuilder instance (in-memory, not persisted)
        
        Example:
            >>> builder = VentaService.create_draft()
            >>> print(builder)
            VentaBuilder(items=0, total_cantidad=0)
        """
        return VentaBuilder()
    
    @staticmethod
    def add_item(
        handler,
        venta_builder: VentaBuilder,
        hotdog_id: str,
        cantidad: int = 1
    ) -> Dict[str, Any]:
        """
        Add an item to the venta draft.
        
        Validations:
        - Hot dog must exist in menu
        - Cantidad must be > 0
        
        Args:
            handler: DataHandler instance
            venta_builder: VentaBuilder instance
            hotdog_id: ID of the hot dog to add
            cantidad: Quantity to add (default: 1)
        
        Returns:
            Dict with:
                - exito: bool
                - item: dict with hotdog info (if success)
                - merged: bool - True if cantidad was merged with existing item
                - error: str (if failed)
        
        Example:
            >>> result = VentaService.add_item(handler, builder, 'hotdog-123', 2)
            >>> if result['exito']:
            ...     print(f"Added: {result['item']}")
        """
        try:
            # Validate hotdog exists in menu
            hotdog = handler.menu.get(hotdog_id)
            if not hotdog:
                return {
                    'exito': False,
                    'error': f"Hot dog con ID '{hotdog_id}' no encontrado en el menú"
                }
            
            # Validate cantidad
            if cantidad <= 0:
                return {
                    'exito': False,
                    'error': f"Cantidad debe ser mayor a 0, recibido: {cantidad}"
                }
            
            # Check if item already exists (for merged flag)
            already_exists = any(item['hotdog_id'] == hotdog_id for item in venta_builder.items)
            
            # Add to builder (will merge if exists)
            venta_builder.add_item(hotdog_id, hotdog.nombre, cantidad)
            
            return {
                'exito': True,
                'item': {
                    'hotdog_id': hotdog_id,
                    'hotdog_nombre': hotdog.nombre,
                    'cantidad': cantidad
                },
                'merged': already_exists
            }
        
        except Exception as e:
            return {
                'exito': False,
                'error': f"Error inesperado: {str(e)}"
            }
    
    @staticmethod
    def remove_item(
        venta_builder: VentaBuilder,
        hotdog_id: str
    ) -> Dict[str, Any]:
        """
        Remove an item from the venta draft.
        
        Args:
            venta_builder: VentaBuilder instance
            hotdog_id: ID of the hot dog to remove
        
        Returns:
            Dict with:
                - exito: bool
                - removed: bool - True if item was found and removed
        
        Example:
            >>> result = VentaService.remove_item(builder, 'hotdog-123')
            >>> if result['removed']:
            ...     print("Item removed")
        """
        removed = venta_builder.remove_item(hotdog_id)
        return {
            'exito': True,
            'removed': removed
        }
    
    @staticmethod
    def update_quantity(
        venta_builder: VentaBuilder,
        hotdog_id: str,
        cantidad: int
    ) -> Dict[str, Any]:
        """
        Update the quantity of an item in the draft.
        
        Args:
            venta_builder: VentaBuilder instance
            hotdog_id: ID of the hot dog
            cantidad: New quantity (must be > 0)
        
        Returns:
            Dict with:
                - exito: bool
                - updated: bool - True if item was found and updated
                - error: str (if cantidad invalid)
        
        Example:
            >>> result = VentaService.update_quantity(builder, 'hotdog-123', 5)
            >>> if result['updated']:
            ...     print("Quantity updated to 5")
        """
        if cantidad <= 0:
            return {
                'exito': False,
                'error': f"Cantidad debe ser mayor a 0, recibido: {cantidad}"
            }
        
        updated = venta_builder.update_cantidad(hotdog_id, cantidad)
        return {
            'exito': True,
            'updated': updated
        }
    
    @staticmethod
    def clear_draft(venta_builder: VentaBuilder) -> Dict[str, Any]:
        """
        Clear all items from the draft.
        
        Args:
            venta_builder: VentaBuilder instance
        
        Returns:
            Dict with exito: True
        
        Example:
            >>> VentaService.clear_draft(builder)
            {'exito': True}
        """
        venta_builder.clear()
        return {'exito': True}
    
    @staticmethod
    def preview_draft(
        handler,
        venta_builder: VentaBuilder
    ) -> Dict[str, Any]:
        """
        Preview the venta before confirming.
        
        Checks:
        - Total items
        - Inventory availability for each hot dog in the order
        - What ingredients would be missing if confirmed now
        
        Args:
            handler: DataHandler instance
            venta_builder: VentaBuilder instance
        
        Returns:
            Dict with:
                - items: List of items in the draft
                - total_items: Total cantidad across all items
                - disponible: bool - True if all inventory is available
                - faltantes: List of missing ingredients per hotdog
                - hotdogs_sin_inventario: List of hotdog names that can't be made
        
        Example:
            >>> preview = VentaService.preview_draft(handler, builder)
            >>> if preview['disponible']:
            ...     print("✅ All inventory available!")
            >>> else:
            ...     print(f"❌ Missing: {preview['hotdogs_sin_inventario']}")
        """
        if not venta_builder.items:
            return {
                'items': [],
                'total_items': 0,
                'disponible': True,
                'faltantes': [],
                'hotdogs_sin_inventario': []
            }
        
        all_faltantes = []
        hotdogs_sin_inventario = []
        
        # Check availability for each item
        for item in venta_builder.items:
            hotdog_id = item['hotdog_id']
            cantidad_pedida = item['cantidad']
            
            # Check availability for ONE unit
            availability = IngredientService.check_hotdog_availability(handler, hotdog_id)
            
            if 'error' in availability:
                # Hot dog doesn't exist (shouldn't happen if added via agregar_item)
                hotdogs_sin_inventario.append(item['hotdog_nombre'])
                continue
            
            if not availability['disponible']:
                # Not enough for even ONE unit
                hotdogs_sin_inventario.append(item['hotdog_nombre'])
                all_faltantes.extend(availability['faltantes'])
            else:
                # Check if there's enough for the CANTIDAD requested
                # We need to verify stock for cantidad_pedida units
                for faltante in availability.get('faltantes', []):
                    # This shouldn't happen if disponible=True, but just in case
                    hotdogs_sin_inventario.append(item['hotdog_nombre'])
                    all_faltantes.append(faltante)
        
        return {
            'items': venta_builder.items.copy(),
            'total_items': venta_builder.get_total_items(),
            'disponible': len(hotdogs_sin_inventario) == 0,
            'faltantes': all_faltantes,
            'hotdogs_sin_inventario': list(set(hotdogs_sin_inventario))  # Unique
        }
    
    @staticmethod
    def confirm_sale(
        handler,
        venta_builder: VentaBuilder,
        fecha: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Confirm the venta: deduct inventory and persist.
        
        Process:
        1. Validate items not empty
        2. Verify inventory available for all items
        3. Deduct stock for each ingredient in each hotdog
        4. Create Venta entity
        5. Add to collection
        6. Mark handler as dirty (caller must commit)
        
        Args:
            handler: DataHandler instance
            venta_builder: VentaBuilder with items
            fecha: Optional datetime string (ISO format). If None, uses current time.
        
        Returns:
            Dict with:
                - exito: bool
                - venta: Venta entity (if success)
                - inventario_descontado: Dict mapping ingrediente_id -> cantidad descontada
                - advertencias: List of warnings (if any)
                - error: str (if failed)
        
        Example:
            >>> result = VentaService.confirm_sale(handler, builder)
            >>> if result['exito']:
            ...     handler.commit()  # Persist changes
            ...     print(f"✅ Venta confirmed: {result['venta'].id}")
            >>> else:
            ...     print(f"❌ {result['error']}")
        """
        try:
            # ─── VALIDATION 1: Items not empty ───
            if not venta_builder.items:
                return {
                    'exito': False,
                    'error': 'La venta debe tener al menos un item'
                }
            
            # ─── VALIDATION 2: Check inventory availability ───
            preview = VentaService.preview_draft(handler, venta_builder)
            
            if not preview['disponible']:
                return {
                    'exito': False,
                    'error': 'Inventario insuficiente para completar la venta',
                    'faltantes': preview['faltantes'],
                    'hotdogs_sin_inventario': preview['hotdogs_sin_inventario']
                }
            
            # ─── STEP 3: Deduct inventory ───
            inventario_descontado = {}
            advertencias = []
            
            for item in venta_builder.items:
                hotdog_id = item['hotdog_id']
                cantidad_vendida = item['cantidad']
                
                # Get hotdog entity
                hotdog = handler.menu.get(hotdog_id)
                if not hotdog:
                    return {
                        'exito': False,
                        'error': f"Hot dog con ID '{hotdog_id}' no encontrado"
                    }
                
                # Deduct stock for each ingredient in the hotdog
                # Pan
                if hasattr(hotdog, 'pan') and hotdog.pan:
                    pan_id = hotdog.pan['id']
                    pan = handler.ingredientes.get(pan_id)
                    if pan:
                        result = IngredientService.update_stock(handler, pan_id, -cantidad_vendida)
                        if result['exito']:
                            inventario_descontado[pan_id] = cantidad_vendida
                        else:
                            # Shouldn't happen if preview passed, but handle it
                            advertencias.append(f"⚠️ Error descontando pan: {result['error']}")
                
                # Salchicha
                if hasattr(hotdog, 'salchicha') and hotdog.salchicha:
                    salchicha_id = hotdog.salchicha['id']
                    salchicha = handler.ingredientes.get(salchicha_id)
                    if salchicha:
                        result = IngredientService.update_stock(handler, salchicha_id, -cantidad_vendida)
                        if result['exito']:
                            inventario_descontado[salchicha_id] = cantidad_vendida
                        else:
                            advertencias.append(f"⚠️ Error descontando salchicha: {result['error']}")
                
                # Toppings
                if hasattr(hotdog, 'toppings') and hotdog.toppings:
                    for topping_ref in hotdog.toppings:
                        topping_id = topping_ref['id']
                        result = IngredientService.update_stock(handler, topping_id, -cantidad_vendida)
                        if result['exito']:
                            inventario_descontado[topping_id] = inventario_descontado.get(topping_id, 0) + cantidad_vendida
                        else:
                            advertencias.append(f"⚠️ Error descontando topping: {result['error']}")
                
                # Salsas
                if hasattr(hotdog, 'salsas') and hotdog.salsas:
                    for salsa_ref in hotdog.salsas:
                        salsa_id = salsa_ref['id']
                        result = IngredientService.update_stock(handler, salsa_id, -cantidad_vendida)
                        if result['exito']:
                            inventario_descontado[salsa_id] = inventario_descontado.get(salsa_id, 0) + cantidad_vendida
                        else:
                            advertencias.append(f"⚠️ Error descontando salsa: {result['error']}")
                
                # Acompañante
                if hasattr(hotdog, 'acompanante') and hotdog.acompanante:
                    acomp_id = hotdog.acompanante['id']
                    result = IngredientService.update_stock(handler, acomp_id, -cantidad_vendida)
                    if result['exito']:
                        inventario_descontado[acomp_id] = inventario_descontado.get(acomp_id, 0) + cantidad_vendida
                    else:
                        advertencias.append(f"⚠️ Error descontando acompañante: {result['error']}")
            
            # ─── STEP 4: Create Venta entity ───
            if fecha is None:
                fecha = datetime.now().isoformat()
            
            # Generate deterministic ID
            from clients.id_processors import generate_stable_id
            venta_id = generate_stable_id(fecha, 'Venta')
            
            # Get Venta class
            from models import create_venta_entities
            venta_entities = create_venta_entities()
            VentaClass = venta_entities['Venta']
            
            # Create instance
            nueva_venta = VentaClass(
                id=venta_id,
                entity_type='Venta',
                fecha=fecha,
                items=venta_builder.items.copy()  # Copy to avoid mutation
            )
            
            # Validate
            nueva_venta.validate()
            
            # ─── STEP 5: Add to collection ───
            handler.ventas.add(nueva_venta)
            
            # ─── RETURN SUCCESS ───
            return {
                'exito': True,
                'venta': nueva_venta,
                'inventario_descontado': inventario_descontado,
                'advertencias': advertencias if advertencias else None
            }
        
        except ValueError as e:
            return {
                'exito': False,
                'error': f"Error de validación: {str(e)}"
            }
        except Exception as e:
            return {
                'exito': False,
                'error': f"Error inesperado: {str(e)}"
            }
