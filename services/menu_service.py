"""
Menu Service Module

Provides business logic for managing the hot dog menu, including operations
for listing, adding, and deleting menu items with appropriate validations.

Author: Rafael Correa
Date: November 16, 2025
"""

from typing import Dict, Any, List, Optional
from services.ingredient_service import IngredientService


class MenuService:
    """
    Static service class for menu management operations.
    
    This service orchestrates operations on the hot dog menu, delegating to
    the DataHandler and collections while implementing business rules and
    validations specific to menu management.
    
    All methods are static and receive the DataHandler as the first parameter.
    
    Business Rules Enforced:
        - Hot dog names must be unique
        - All ingredients must exist in the ingredient catalog
        - Pan and salchicha sizes should match (warning if not)
        - Inventory warnings when adding hot dogs with low/no stock
        - Deletion warnings when removing hot dogs with available inventory
    """
    
    @staticmethod
    def list_all(handler) -> List[Any]:
        """
        List all hot dogs in the menu.
        
        Args:
            handler: DataHandler instance
        
        Returns:
            List of HotDog entities
            
        Example:
            hotdogs = MenuService.list_all(handler)
            for hd in hotdogs:
                print(f"{hd.nombre}: {hd.pan['nombre']} + {hd.salchicha['nombre']}")
        """
        return handler.menu.get_all()
    
    @staticmethod
    def get_by_name(handler, nombre: str) -> Optional[Any]:
        """
        Get a specific hot dog by name.
        
        Args:
            handler: DataHandler instance
            nombre: Name of the hot dog
        
        Returns:
            HotDog entity if found, None otherwise
            
        Example:
            hotdog = MenuService.get_by_name(handler, 'simple')
            if hotdog:
                print(f"Encontrado: {hotdog.nombre}")
        """
        return handler.menu.get_by_name(nombre)
    
    @staticmethod
    def get_combos(handler) -> List[Any]:
        """
        Get all combo hot dogs (with acompañante).
        
        Args:
            handler: DataHandler instance
        
        Returns:
            List of HotDog entities that are combos
        """
        return handler.menu.get_combos()
    
    @staticmethod
    def get_simple_hotdogs(handler) -> List[Any]:
        """
        Get all simple hot dogs (no extras).
        
        Args:
            handler: DataHandler instance
        
        Returns:
            List of simple HotDog entities
        """
        return handler.menu.get_simple_hotdogs()

    
    @staticmethod
    def check_availability(handler, hotdog_id: str) -> Dict[str, Any]:
        """
        Check if there's enough inventory to make a specific hot dog.
        
        Delegates to IngredientService.check_hotdog_availability() which
        verifies inventory for all ingredients in the hot dog.
        
        Args:
            handler: DataHandler instance
            hotdog_id: ID of the hot dog to check
        
        Returns:
            Dict with:
                - disponible: bool
                - faltantes: list of dicts with missing ingredients (if any)
                - error: str (if hotdog not found)
        
        Example:
            result = MenuService.check_availability(handler, hotdog_id)
            if result['disponible']:
                print("✅ Hay inventario suficiente")
            else:
                print(f"❌ Faltan: {result['faltantes']}")
        """
        return IngredientService.check_hotdog_availability(handler, hotdog_id)
    
    @staticmethod
    def add_hotdog(
        handler,
        nombre: str,
        pan_id: str,
        salchicha_id: str,
        topping_ids: Optional[List[str]] = None,
        salsa_ids: Optional[List[str]] = None,
        acompanante_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a new hot dog to the menu with full validation.
        
        Business Rules:
            1. Name must be unique
            2. All ingredients must exist (by ID)
            3. Pan and salchicha sizes should match (warning if not)
            4. Low/no inventory triggers warning (but doesn't block)
        
        Args:
            handler: DataHandler instance
            nombre: Name for the new hot dog
            pan_id: ID of the pan ingredient
            salchicha_id: ID of the salchicha ingredient
            topping_ids: Optional list of topping IDs
            salsa_ids: Optional list of salsa IDs
            acompanante_id: Optional acompañante ID
        
        Returns:
            Dict with:
                - exito: bool
                - hotdog: created HotDog entity (if success)
                - advertencias: list of warning messages (if any)
                - error: str (if failed)
        
        Example:
            result = MenuService.add_hotdog(
                handler,
                nombre='super perro',
                pan_id='pan_id_123',
                salchicha_id='salchicha_id_456',
                topping_ids=['topping_id_789'],
                salsa_ids=['salsa_id_012'],
                acompanante_id='acomp_id_345'
            )
            
            if result['exito']:
                print(f"✅ Hot dog '{result['hotdog'].nombre}' creado")
                if result.get('advertencias'):
                    for adv in result['advertencias']:
                        print(f"⚠️  {adv}")
            else:
                print(f"❌ {result['error']}")
        """
        topping_ids = topping_ids or []
        salsa_ids = salsa_ids or []
        advertencias = []
        
        try:
            # ─── VALIDACIÓN 1: Nombre único ───
            handler.menu.validate_unique_name(nombre)
            
            # ─── VALIDACIÓN 2: Todos los ingredientes existen ───
            # Obtener ingredientes por ID
            pan = handler.ingredientes.get(pan_id)
            if not pan:
                return {'exito': False, 'error': f"Pan con ID '{pan_id}' no encontrado"}
            
            salchicha = handler.ingredientes.get(salchicha_id)
            if not salchicha:
                return {'exito': False, 'error': f"Salchicha con ID '{salchicha_id}' no encontrada"}
            
            # Validar toppings
            toppings = []
            for topping_id in topping_ids:
                topping = handler.ingredientes.get(topping_id)
                if not topping:
                    return {'exito': False, 'error': f"Topping con ID '{topping_id}' no encontrado"}
                toppings.append(topping)
            
            # Validar salsas
            salsas = []
            for salsa_id in salsa_ids:
                salsa = handler.ingredientes.get(salsa_id)
                if not salsa:
                    return {'exito': False, 'error': f"Salsa con ID '{salsa_id}' no encontrada"}
                salsas.append(salsa)
            
            # Validar acompañante (opcional)
            acompanante = None
            if acompanante_id:
                acompanante = handler.ingredientes.get(acompanante_id)
                if not acompanante:
                    return {'exito': False, 'error': f"Acompañante con ID '{acompanante_id}' no encontrado"}
            
            # ─── VALIDACIÓN 3: Tamaños coincidentes (advertencia) ───
            # Usa el método matches_size() del plugin de Salchicha
            if not salchicha.matches_size(pan):
                advertencias.append(
                    f"⚠️  Advertencia: El pan ({pan.tamano} {pan.unidad}) y la salchicha "
                    f"({salchicha.tamano} {salchicha.unidad}) tienen tamaños diferentes"
                )
            
            # ─── VALIDACIÓN 4: Inventario disponible (advertencia) ───
            # Verificar stock de cada ingrediente
            stock_warnings = []
            
            if pan.stock <= 0:
                stock_warnings.append(f"Pan '{pan.nombre}' (sin stock)")
            elif pan.stock < 10:
                stock_warnings.append(f"Pan '{pan.nombre}' (stock bajo: {pan.stock})")
            
            if salchicha.stock <= 0:
                stock_warnings.append(f"Salchicha '{salchicha.nombre}' (sin stock)")
            elif salchicha.stock < 10:
                stock_warnings.append(f"Salchicha '{salchicha.nombre}' (stock bajo: {salchicha.stock})")
            
            for topping in toppings:
                if topping.stock <= 0:
                    stock_warnings.append(f"Topping '{topping.nombre}' (sin stock)")
                elif topping.stock < 10:
                    stock_warnings.append(f"Topping '{topping.nombre}' (stock bajo: {topping.stock})")
            
            for salsa in salsas:
                if salsa.stock <= 0:
                    stock_warnings.append(f"Salsa '{salsa.nombre}' (sin stock)")
                elif salsa.stock < 10:
                    stock_warnings.append(f"Salsa '{salsa.nombre}' (stock bajo: {salsa.stock})")
            
            if acompanante and acompanante.stock <= 0:
                stock_warnings.append(f"Acompañante '{acompanante.nombre}' (sin stock)")
            elif acompanante and acompanante.stock < 10:
                stock_warnings.append(f"Acompañante '{acompanante.nombre}' (stock bajo: {acompanante.stock})")
            
            if stock_warnings:
                advertencias.append(
                    f"⚠️  Advertencia de inventario: {', '.join(stock_warnings)}"
                )
            
            # ─── CREAR HOT DOG ───
            # Construir referencias estructuradas {id, nombre}
            pan_ref = {'id': pan.id, 'nombre': pan.nombre}
            salchicha_ref = {'id': salchicha.id, 'nombre': salchicha.nombre}
            
            toppings_ref = [{'id': t.id, 'nombre': t.nombre} for t in toppings]
            salsas_ref = [{'id': s.id, 'nombre': s.nombre} for s in salsas]
            
            acompanante_ref = None
            if acompanante:
                acompanante_ref = {'id': acompanante.id, 'nombre': acompanante.nombre}
            
            # Generar ID determinístico para el hot dog
            from clients.id_processors import generate_stable_id
            hotdog_id = generate_stable_id(nombre, 'HotDog')
            
            # Obtener clase HotDog
            hotdog_class = handler.menu._hotdog_class
            
            # Crear instancia
            nuevo_hotdog = hotdog_class(
                id=hotdog_id,
                entity_type='HotDog',
                nombre=nombre,
                pan=pan_ref,
                salchicha=salchicha_ref,
                toppings=toppings_ref,
                salsas=salsas_ref,
                acompanante=acompanante_ref
            )
            
            # Agregar a collection (esto valida automáticamente con plugins)
            handler.menu.add(nuevo_hotdog)
            
            return {
                'exito': True,
                'hotdog': nuevo_hotdog,
                'advertencias': advertencias if advertencias else None
            }
        
        except ValueError as e:
            return {'exito': False, 'error': str(e)}
        except Exception as e:
            return {'exito': False, 'error': f"Error inesperado: {str(e)}"}
    
    @staticmethod
    def delete_hotdog(
        handler,
        hotdog_id: str,
        confirmar_con_inventario: bool = False
    ) -> Dict[str, Any]:
        """
        Delete a hot dog from the menu with inventory validation.
        
        Business Rule:
            Only hot dogs WITHOUT sufficient inventory should be deleted freely.
            If there IS inventory, require confirmation (two-step pattern).
        
        Args:
            handler: DataHandler instance
            hotdog_id: ID of the hot dog to delete
            confirmar_con_inventario: If True, delete even with inventory
        
        Returns:
            Dict with:
                - exito: bool
                - hotdog_eliminado: deleted HotDog entity (if success)
                - requiere_confirmacion: bool (if confirmation needed)
                - advertencia: str (if confirmation needed)
                - error: str (if failed)
        
        Example:
            # First attempt
            result = MenuService.delete_hotdog(handler, hotdog_id)
            if result.get('requiere_confirmacion'):
                print(f"⚠️  {result['advertencia']}")
                # User confirms...
                result = MenuService.delete_hotdog(handler, hotdog_id, True)
            
            if result['exito']:
                print(f"✅ Hot dog '{result['hotdog_eliminado'].nombre}' eliminado")
        """
        try:
            # ─── VERIFICAR EXISTENCIA ───
            hotdog = handler.menu.get(hotdog_id)
            if not hotdog:
                return {'exito': False, 'error': f"Hot dog con ID '{hotdog_id}' no encontrado"}
            
            # ─── VERIFICAR DISPONIBILIDAD DE INVENTARIO ───
            availability = IngredientService.check_hotdog_availability(handler, hotdog_id)
            
            # Si hay error en la verificación (ej: hotdog no existe), retornar error
            if 'error' in availability:
                return {'exito': False, 'error': availability['error']}
            
            tiene_inventario = availability['disponible']
            
            # ─── PATRÓN DE CONFIRMACIÓN ───
            if tiene_inventario and not confirmar_con_inventario:
                return {
                    'exito': False,
                    'requiere_confirmacion': True,
                    'advertencia': (
                        f"⚠️  El hot dog '{hotdog.nombre}' tiene inventario suficiente para ser vendido. "
                        f"¿Está seguro que desea eliminarlo del menú?"
                    ),
                    'hotdog': hotdog
                }
            
            # ─── ELIMINAR ───
            handler.menu.delete(hotdog_id)
            
            return {
                'exito': True,
                'hotdog_eliminado': hotdog
            }
        
        except ValueError as e:
            return {'exito': False, 'error': str(e)}
        except Exception as e:
            return {'exito': False, 'error': f"Error inesperado: {str(e)}"}
    
    @staticmethod
    def get_stats(handler) -> Dict[str, Any]:
        """
        Get menu statistics.
        
        Args:
            handler: DataHandler instance
        
        Returns:
            Dict with various statistics
            
        Example:
            stats = MenuService.get_stats(handler)
            print(f"Total de hot dogs: {stats['total']}")
            print(f"Combos: {stats['combos']}")
            print(f"Simples: {stats['simples']}")
        """
        return handler.menu.get_stats()
