"""
Ingredient Service

Business logic for ingredient management operations.
All methods are static and operate on a DataHandler instance.

Includes both catalog management and inventory management.

Author: Rafael Correa
Date: November 15, 2025
"""

from typing import List, Dict, Any, Optional
from handlers.data_handler import DataHandler


class IngredientService:
    """
    Service class for ingredient-related business logic.
    
    This service provides methods to:
    - List ingredients by category and type
    - Add new ingredients
    - Delete ingredients (with menu validation)
    
    All methods are static and require a DataHandler instance.
    """
    
    @staticmethod
    def list_by_category(handler: DataHandler, categoria: str) -> List[Any]:
        """
        List all ingredients in a specific category.
        
        Args:
            handler: DataHandler instance with loaded data
            categoria: Category name (e.g., 'Pan', 'Salchicha', 'Toppings', 'Salsa', 'Acompañante')
        
        Returns:
            List of ingredient entities in the category
        
        Example:
            >>> panes = IngredientService.list_by_category(handler, 'Pan')
            >>> for pan in panes:
            ...     print(pan.nombre, pan.tipo)
        """
        return handler.ingredientes.get_by_category(categoria)
    
    @staticmethod
    def list_by_type(handler: DataHandler, categoria: str, tipo: str) -> List[Any]:
        """
        List all ingredients in a category filtered by type.
        
        Args:
            handler: DataHandler instance with loaded data
            categoria: Category name (e.g., 'Pan', 'Salchicha')
            tipo: Type value to filter by (e.g., 'blanco', 'integral')
        
        Returns:
            List of ingredient entities matching the category and type
        
        Example:
            >>> panes_blancos = IngredientService.list_by_type(handler, 'Pan', 'blanco')
        """
        # Get all ingredients in category
        ingredients = handler.ingredientes.get_by_category(categoria)
        
        # Filter by type
        return [ing for ing in ingredients if hasattr(ing, 'tipo') and ing.tipo == tipo]
    
    @staticmethod
    def add_ingredient(
        handler: DataHandler,
        categoria: str,
        nombre: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Add a new ingredient to the system.
        
        Args:
            handler: DataHandler instance
            categoria: Category name (e.g., 'Pan', 'Salchicha')
            nombre: Ingredient name (must be unique within category)
            **kwargs: Additional properties (e.g., tipo='blanco', tamano=6, unidad='pulgadas')
        
        Returns:
            Dict with:
                - 'exito': bool indicating success
                - 'ingrediente': Created entity if successful
                - 'error': Error message if failed
        
        Example:
            >>> result = IngredientService.add_ingredient(
            ...     handler,
            ...     'Pan',
            ...     'frances',
            ...     tipo='blanco',
            ...     tamano=8,
            ...     unidad='pulgadas'
            ... )
        """
        try:
            # Validate unique name within category
            handler.ingredientes.validate_unique_name(nombre, categoria)
            
            # Get entity class for this category
            from models.entities.ingredients import create_ingredient_entities
            ingredient_classes = create_ingredient_entities()
            
            entity_type = categoria.capitalize()
            if entity_type not in ingredient_classes:
                return {
                    'exito': False,
                    'error': f"Categoría inválida: {categoria}"
                }
            
            EntityClass = ingredient_classes[entity_type]
            
            # Generate stable ID
            from clients.id_processors import generate_stable_id
            ingredient_id = generate_stable_id(nombre, categoria)
            
            # Create entity
            entity = EntityClass(
                id=ingredient_id,
                entity_type=entity_type,
                nombre=nombre,
                **kwargs
            )
            
            # Validate entity
            entity.validate()
            
            # Add to collection
            handler.ingredientes.add(entity)
            
            return {
                'exito': True,
                'ingrediente': entity
            }
            
        except ValueError as e:
            return {
                'exito': False,
                'error': str(e)
            }
        except Exception as e:
            return {
                'exito': False,
                'error': f"Error inesperado: {str(e)}"
            }
    
    @staticmethod
    def delete_ingredient(
        handler: DataHandler,
        ingrediente_id: str,
        confirmar_eliminar_hotdogs: bool = False
    ) -> Dict[str, Any]:
        """
        Delete an ingredient from the system.
        
        If the ingredient is used in any hot dog from the menu, this method will:
        1. Return the list of affected hot dogs
        2. Require confirmation to proceed
        3. If confirmed, delete both the ingredient and affected hot dogs
        
        Args:
            handler: DataHandler instance
            ingrediente_id: ID of the ingredient to delete
            confirmar_eliminar_hotdogs: If True, confirms deletion of affected hot dogs
        
        Returns:
            Dict with:
                - 'exito': bool indicating if deletion occurred
                - 'ingrediente_eliminado': bool
                - 'hotdogs_afectados': List of hot dog IDs using this ingredient
                - 'hotdogs_eliminados': List of hot dog IDs deleted (if confirmed)
                - 'requiere_confirmacion': bool indicating if confirmation is needed
                - 'error': Error message if failed
        
        Example:
            >>> # First attempt (check what will be affected)
            >>> result = IngredientService.delete_ingredient(handler, 'pan_simple_id')
            >>> if result['requiere_confirmacion']:
            ...     print(f"Afectará {len(result['hotdogs_afectados'])} hot dogs")
            ...     # Then confirm
            ...     result = IngredientService.delete_ingredient(
            ...         handler, 'pan_simple_id', confirmar_eliminar_hotdogs=True
            ...     )
        """
        try:
            # Check if ingredient exists
            ingrediente = handler.ingredientes.get(ingrediente_id)
            if not ingrediente:
                return {
                    'exito': False,
                    'error': f"Ingrediente con ID '{ingrediente_id}' no encontrado"
                }
            
            # Find hot dogs that use this ingredient
            hotdogs_afectados = IngredientService._find_hotdogs_using_ingredient(
                handler, ingrediente_id, ingrediente.nombre
            )
            
            # If ingredient is used and no confirmation, return warning
            if hotdogs_afectados and not confirmar_eliminar_hotdogs:
                return {
                    'exito': False,
                    'ingrediente_eliminado': False,
                    'hotdogs_afectados': hotdogs_afectados,
                    'hotdogs_eliminados': [],
                    'requiere_confirmacion': True,
                    'error': f"Este ingrediente está siendo usado en {len(hotdogs_afectados)} hot dog(s)"
                }
            
            # Delete affected hot dogs if confirmed
            hotdogs_eliminados = []
            if hotdogs_afectados and confirmar_eliminar_hotdogs:
                for hotdog_id in hotdogs_afectados:
                    handler.menu.delete(hotdog_id)
                    hotdogs_eliminados.append(hotdog_id)
            
            # Delete ingredient
            handler.ingredientes.delete(ingrediente_id)
            
            return {
                'exito': True,
                'ingrediente_eliminado': True,
                'hotdogs_afectados': hotdogs_afectados,
                'hotdogs_eliminados': hotdogs_eliminados,
                'requiere_confirmacion': False
            }
            
        except Exception as e:
            return {
                'exito': False,
                'error': f"Error al eliminar ingrediente: {str(e)}"
            }
    
    @staticmethod
    def _find_hotdogs_using_ingredient(
        handler: DataHandler,
        ingrediente_id: str,
        ingrediente_nombre: str
    ) -> List[str]:
        """
        Find all hot dogs that use a specific ingredient.
        
        Args:
            handler: DataHandler instance
            ingrediente_id: ID of the ingredient
            ingrediente_nombre: Name of the ingredient (for comparison)
        
        Returns:
            List of hot dog IDs that use this ingredient
        """
        hotdogs_usando = []
        
        for hotdog in handler.menu.get_all():
            # Check if ingredient is used in any field
            # Hot dogs have: pan, salchicha, toppings, salsas, acompanante
            
            # Check pan (string field)
            if hasattr(hotdog, 'pan') and hotdog.pan == ingrediente_nombre:
                hotdogs_usando.append(hotdog.id)
                continue
            
            # Check salchicha (string field)
            if hasattr(hotdog, 'salchicha') and hotdog.salchicha == ingrediente_nombre:
                hotdogs_usando.append(hotdog.id)
                continue
            
            # Check toppings (list field)
            if hasattr(hotdog, 'toppings') and ingrediente_nombre in hotdog.toppings:
                hotdogs_usando.append(hotdog.id)
                continue
            
            # Check salsas (list field)
            if hasattr(hotdog, 'salsas') and ingrediente_nombre in hotdog.salsas:
                hotdogs_usando.append(hotdog.id)
                continue
            
            # Check acompanante (string field, nullable)
            if hasattr(hotdog, 'acompanante') and hotdog.acompanante == ingrediente_nombre:
                hotdogs_usando.append(hotdog.id)
                continue
        
        return hotdogs_usando
    
    # ═══════════════════════════════════════════════════════════════
    # INVENTORY MANAGEMENT
    # ═══════════════════════════════════════════════════════════════
    
    @staticmethod
    def get_full_inventory(handler: DataHandler) -> Dict[str, int]:
        """
        Get complete inventory of all ingredients.
        
        Args:
            handler: DataHandler instance
        
        Returns:
            Dict mapping ingredient_id to stock quantity
            Example: {'pan_id_123': 100, 'salchicha_id_456': 75}
        
        Example:
            >>> inventory = IngredientService.get_full_inventory(handler)
            >>> for ing_id, stock in inventory.items():
            ...     print(f"{ing_id}: {stock} units")
        """
        result = {}
        
        for ingredient in handler.ingredientes.get_all():
            stock = getattr(ingredient, 'stock', 0)
            result[ingredient.id] = stock
        
        return result
    
    @staticmethod
    def get_stock(handler: DataHandler, ingrediente_id: str) -> Optional[int]:
        """
        Get stock quantity for a specific ingredient.
        
        Args:
            handler: DataHandler instance
            ingrediente_id: ID of the ingredient
        
        Returns:
            Stock quantity, or None if ingredient not found
        
        Example:
            >>> stock = IngredientService.get_stock(handler, 'pan_id_123')
            >>> if stock is not None:
            ...     print(f"Stock available: {stock}")
        """
        ingredient = handler.ingredientes.get(ingrediente_id)
        
        if not ingredient:
            return None
        
        return getattr(ingredient, 'stock', 0)
    
    @staticmethod
    def get_inventory_by_category(handler: DataHandler, categoria: str) -> Dict[str, Dict]:
        """
        Get inventory details for all ingredients in a category.
        
        Args:
            handler: DataHandler instance
            categoria: Category name (e.g., 'Pan', 'Salchicha')
        
        Returns:
            Dict mapping ingredient_id to details dict with:
                - nombre: Ingredient name
                - tipo: Ingredient type (if exists)
                - stock: Current stock quantity
        
        Example:
            >>> inventory = IngredientService.get_inventory_by_category(handler, 'Pan')
            >>> for ing_id, details in inventory.items():
            ...     print(f"{details['nombre']}: {details['stock']} units")
        """
        result = {}
        
        ingredients = handler.ingredientes.get_by_category(categoria)
        
        for ingredient in ingredients:
            stock = getattr(ingredient, 'stock', 0)
            tipo = getattr(ingredient, 'tipo', None)
            
            result[ingredient.id] = {
                'nombre': ingredient.nombre,
                'tipo': tipo,
                'stock': stock
            }
        
        return result
    
    @staticmethod
    def update_stock(
        handler: DataHandler,
        ingrediente_id: str,
        cantidad: int
    ) -> Dict[str, Any]:
        """
        Update stock for an ingredient (add or subtract).
        
        Args:
            handler: DataHandler instance
            ingrediente_id: ID of the ingredient
            cantidad: Quantity to add (positive) or subtract (negative)
        
        Returns:
            Dict with:
                - 'exito': bool indicating success
                - 'stock_anterior': Previous stock value
                - 'stock_nuevo': New stock value
                - 'error': Error message if failed
        
        Example:
            >>> # Add 50 units
            >>> result = IngredientService.update_stock(handler, 'pan_id', 50)
            >>> # Subtract 10 units
            >>> result = IngredientService.update_stock(handler, 'pan_id', -10)
        """
        try:
            ingredient = handler.ingredientes.get(ingrediente_id)
            
            if not ingredient:
                return {
                    'exito': False,
                    'error': f"Ingrediente con ID '{ingrediente_id}' no encontrado"
                }
            
            # Get current stock
            stock_anterior = getattr(ingredient, 'stock', 0)
            
            # Calculate new stock
            stock_nuevo = stock_anterior + cantidad
            
            # Validate non-negative stock
            if stock_nuevo < 0:
                return {
                    'exito': False,
                    'stock_anterior': stock_anterior,
                    'error': f"Stock no puede ser negativo. Stock actual: {stock_anterior}, intentó restar: {abs(cantidad)}"
                }
            
            # Update stock
            setattr(ingredient, 'stock', stock_nuevo)
            
            # Update in collection (marks dirty)
            handler.ingredientes.update(ingredient)
            
            return {
                'exito': True,
                'stock_anterior': stock_anterior,
                'stock_nuevo': stock_nuevo
            }
            
        except Exception as e:
            return {
                'exito': False,
                'error': f"Error al actualizar stock: {str(e)}"
            }
    
    @staticmethod
    def check_hotdog_availability(
        handler: DataHandler,
        hotdog_id: str
    ) -> Dict[str, Any]:
        """
        Check if there's sufficient inventory to make a hot dog.
        
        Args:
            handler: DataHandler instance
            hotdog_id: ID of the hot dog to check
        
        Returns:
            Dict with:
                - 'disponible': bool indicating if all ingredients are available
                - 'faltantes': List of dicts with missing ingredients:
                    - 'ingrediente': Ingredient name
                    - 'categoria': Ingredient category
                    - 'necesita': Quantity needed (always 1)
                    - 'disponible': Current stock
                - 'error': Error message if hot dog not found
        
        Example:
            >>> result = IngredientService.check_hotdog_availability(handler, 'hotdog_id')
            >>> if result['disponible']:
            ...     print("Can make this hot dog!")
            >>> else:
            ...     for faltante in result['faltantes']:
            ...         print(f"Missing: {faltante['ingrediente']}")
        """
        try:
            # Get hot dog
            hotdog = handler.menu.get(hotdog_id)
            
            if not hotdog:
                return {
                    'disponible': False,
                    'faltantes': [],
                    'error': f"Hot dog con ID '{hotdog_id}' no encontrado"
                }
            
            faltantes = []
            
            # Check pan
            if hasattr(hotdog, 'pan') and hotdog.pan:
                # hotdog.pan es {'id': '...', 'nombre': '...'} después de IngredientReferenceAdapter
                pan_ref = hotdog.pan
                pan_id = pan_ref['id'] if isinstance(pan_ref, dict) else None
                pan_nombre = pan_ref['nombre'] if isinstance(pan_ref, dict) else pan_ref
                
                pan = handler.ingredientes.get(pan_id) if pan_id else handler.ingredientes.get_by_name(pan_nombre, 'Pan')
                if pan:
                    stock = getattr(pan, 'stock', 0)
                    if stock < 1:
                        faltantes.append({
                            'ingrediente': pan_nombre,
                            'categoria': 'Pan',
                            'necesita': 1,
                            'disponible': stock
                        })
            
            # Check salchicha
            if hasattr(hotdog, 'salchicha') and hotdog.salchicha:
                salchicha_ref = hotdog.salchicha
                salchicha_id = salchicha_ref['id'] if isinstance(salchicha_ref, dict) else None
                salchicha_nombre = salchicha_ref['nombre'] if isinstance(salchicha_ref, dict) else salchicha_ref
                
                salchicha = handler.ingredientes.get(salchicha_id) if salchicha_id else handler.ingredientes.get_by_name(salchicha_nombre, 'Salchicha')
                if salchicha:
                    stock = getattr(salchicha, 'stock', 0)
                    if stock < 1:
                        faltantes.append({
                            'ingrediente': salchicha_nombre,
                            'categoria': 'Salchicha',
                            'necesita': 1,
                            'disponible': stock
                        })
            
            # Check toppings
            if hasattr(hotdog, 'toppings') and hotdog.toppings:
                for topping_ref in hotdog.toppings:
                    topping_id = topping_ref['id'] if isinstance(topping_ref, dict) else None
                    topping_nombre = topping_ref['nombre'] if isinstance(topping_ref, dict) else topping_ref
                    
                    topping = handler.ingredientes.get(topping_id) if topping_id else handler.ingredientes.get_by_name(topping_nombre, 'Toppings')
                    if topping:
                        stock = getattr(topping, 'stock', 0)
                        if stock < 1:
                            faltantes.append({
                                'ingrediente': topping_nombre,
                                'categoria': 'Toppings',
                                'necesita': 1,
                                'disponible': stock
                            })
            
            # Check salsas
            if hasattr(hotdog, 'salsas') and hotdog.salsas:
                for salsa_ref in hotdog.salsas:
                    salsa_id = salsa_ref['id'] if isinstance(salsa_ref, dict) else None
                    salsa_nombre = salsa_ref['nombre'] if isinstance(salsa_ref, dict) else salsa_ref
                    
                    salsa = handler.ingredientes.get(salsa_id) if salsa_id else handler.ingredientes.get_by_name(salsa_nombre, 'Salsa')
                    if salsa:
                        stock = getattr(salsa, 'stock', 0)
                        if stock < 1:
                            faltantes.append({
                                'ingrediente': salsa_nombre,
                                'categoria': 'Salsa',
                                'necesita': 1,
                                'disponible': stock
                            })
            
            # Check acompanante
            if hasattr(hotdog, 'acompanante') and hotdog.acompanante:
                acompanante_ref = hotdog.acompanante
                acompanante_id = acompanante_ref['id'] if isinstance(acompanante_ref, dict) else None
                acompanante_nombre = acompanante_ref['nombre'] if isinstance(acompanante_ref, dict) else acompanante_ref
                
                acompanante = handler.ingredientes.get(acompanante_id) if acompanante_id else handler.ingredientes.get_by_name(acompanante_nombre, 'Acompañante')
                if acompanante:
                    stock = getattr(acompanante, 'stock', 0)
                    if stock < 1:
                        faltantes.append({
                            'ingrediente': acompanante_nombre,
                            'categoria': 'Acompañante',
                            'necesita': 1,
                            'disponible': stock
                        })
            
            return {
                'disponible': len(faltantes) == 0,
                'faltantes': faltantes
            }
            
        except Exception as e:
            return {
                'disponible': False,
                'faltantes': [],
                'error': f"Error al verificar disponibilidad: {str(e)}"
            }
