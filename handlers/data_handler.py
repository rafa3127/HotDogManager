"""
Data Handler Module

This module provides the central orchestrator for all data collections,
implementing the Unit of Work pattern for transactional behavior.

The DataHandler manages multiple collections and coordinates their persistence,
allowing atomic commits and rollbacks across all data sources.

Classes:
    DataHandler: Central orchestrator for data collections

Author: Rafael Correa
Date: November 15, 2025
"""

from typing import Optional, List
from models.collections import IngredientCollection, HotDogCollection
from models.core.base_entity import Entity


class DataHandler:
    """
    Central orchestrator for all data collections.
    
    Implements the Unit of Work pattern, managing multiple collections and
    coordinating their persistence. This allows atomic commits (save all changes)
    and rollbacks (discard all changes) across all collections.
    
    The DataHandler acts as a facade, providing convenient access to all
    collections and their operations while managing transactional behavior.
    
    Attributes:
        ingredientes: IngredientCollection instance
        menu: HotDogCollection instance
        _collections: Internal list of all managed collections
    
    Usage:
        # Initialize
        handler = DataHandler(data_source)
        
        # Access collections
        panes = handler.ingredientes.get_by_category('Pan')
        hotdog = handler.menu.get_by_name('simple')
        
        # Make changes
        handler.ingredientes.add(nuevo_pan)
        handler.menu.update(hotdog)
        
        # Commit all changes at once
        handler.commit()
        
        # Or rollback if needed
        handler.rollback()
    """
    
    def __init__(self, data_source):
        """
        Initialize the data handler with all collections.
        
        Args:
            data_source: DataSourceClient instance for persistence
        """
        self._data_source = data_source
        
        # Initialize collections
        self.ingredientes = IngredientCollection(data_source)
        self.menu = HotDogCollection(data_source)
        
        # Track all collections for Unit of Work operations
        self._collections = [
            self.ingredientes,
            self.menu,
        ]
    
    # ────────────────────────────────────────────────────────────
    # Unit of Work Pattern - Transactional Operations
    # ────────────────────────────────────────────────────────────
    
    @property
    def has_changes(self) -> bool:
        """
        Check if there are unsaved changes in any collection.
        
        Returns:
            True if any collection has changes, False otherwise
            
        Example:
            if handler.has_changes:
                print("⚠️  Hay cambios sin guardar")
        """
        return any(collection.is_dirty for collection in self._collections)
    
    def commit(self) -> None:
        """
        Commit all changes across all collections.
        
        This method flushes all dirty collections to their respective data sources,
        implementing atomic persistence. If any collection has no changes, it is
        skipped for efficiency.
        
        This is the primary way to persist changes in the application. All
        modifications should be followed by a call to commit() to save them.
        
        Example:
            handler.ingredientes.add(nuevo_pan)
            handler.menu.add(nuevo_hotdog)
            handler.commit()  # Saves both changes atomically
            
        Note:
            Individual collection flush() methods are also available but
            using commit() is preferred for consistency.
        """
        dirty_collections = [col for col in self._collections if col.is_dirty]
        
        if not dirty_collections:
            print("ℹ️  No hay cambios que guardar")
            return
        
        # Flush all dirty collections
        for collection in dirty_collections:
            collection.flush()
        
        print(f"✅ Cambios guardados ({len(dirty_collections)} colecciones actualizadas)")
    
    def rollback(self) -> None:
        """
        Discard all unsaved changes across all collections.
        
        This method reloads all dirty collections from their data sources,
        effectively undoing any changes made since the last commit.
        
        Use this when you want to cancel a set of operations or when an
        error occurs during a transaction.
        
        Example:
            try:
                handler.ingredientes.add(nuevo_pan)
                handler.menu.add(nuevo_hotdog)
                # Something goes wrong...
                raise Exception("Error de validación")
            except Exception as e:
                handler.rollback()  # Undo all changes
                print(f"Error: {e}")
        """
        dirty_collections = [col for col in self._collections if col.is_dirty]
        
        if not dirty_collections:
            print("ℹ️  No hay cambios que descartar")
            return
        
        # Reload all dirty collections
        for collection in dirty_collections:
            collection.reload()
        
        print(f"↩️  Cambios descartados ({len(dirty_collections)} colecciones revertidas)")
    
    # ────────────────────────────────────────────────────────────
    # Convenience Methods - Ingredients
    # ────────────────────────────────────────────────────────────
    
    def get_ingredient(self, id: str) -> Optional[Entity]:
        """
        Get an ingredient by ID.
        
        Args:
            id: Ingredient ID
            
        Returns:
            Ingredient entity if found, None otherwise
        """
        return self.ingredientes.get(id)
    
    def get_ingredient_by_name(self, nombre: str, categoria: str) -> Optional[Entity]:
        """
        Get an ingredient by name and category.
        
        Args:
            nombre: Ingredient name
            categoria: Category (e.g., 'Pan', 'Salchicha')
            
        Returns:
            Ingredient entity if found, None otherwise
            
        Example:
            pan = handler.get_ingredient_by_name('simple', 'Pan')
        """
        return self.ingredientes.get_by_name(nombre, categoria)
    
    def get_ingredients_by_category(self, categoria: str) -> List[Entity]:
        """
        Get all ingredients in a category.
        
        Args:
            categoria: Category name (e.g., 'Pan', 'Salchicha')
            
        Returns:
            List of ingredients in that category
            
        Example:
            panes = handler.get_ingredients_by_category('Pan')
        """
        return self.ingredientes.get_by_category(categoria)
    
    # ────────────────────────────────────────────────────────────
    # Convenience Methods - Hot Dogs
    # ────────────────────────────────────────────────────────────
    
    def get_hotdog(self, id: str) -> Optional[Entity]:
        """
        Get a hot dog by ID.
        
        Args:
            id: Hot dog ID
            
        Returns:
            HotDog entity if found, None otherwise
        """
        return self.menu.get(id)
    
    def get_hotdog_by_name(self, nombre: str) -> Optional[Entity]:
        """
        Get a hot dog by name.
        
        Args:
            nombre: Hot dog name (e.g., 'simple', 'inglés')
            
        Returns:
            HotDog entity if found, None otherwise
            
        Example:
            hotdog = handler.get_hotdog_by_name('simple')
        """
        return self.menu.get_by_name(nombre)
    
    # ────────────────────────────────────────────────────────────
    # Validation Helpers
    # ────────────────────────────────────────────────────────────
    
    def validate_hotdog_ingredients(self, pan: str, salchicha: str,
                                    toppings: List[str], salsas: List[str],
                                    acompanante: Optional[str] = None) -> None:
        """
        Validate that all ingredients for a hot dog exist.
        
        This is a convenience wrapper around HotDogCollection's validation
        that automatically passes the ingredient collection.
        
        Args:
            pan: Pan name
            salchicha: Salchicha name
            toppings: List of topping names
            salsas: List of salsa names
            acompanante: Optional acompañante name
            
        Raises:
            ValueError: If any ingredient doesn't exist
            
        Example:
            handler.validate_hotdog_ingredients(
                pan='simple',
                salchicha='weiner',
                toppings=['cebolla'],
                salsas=['mostaza'],
                acompanante='Papas'
            )
        """
        self.menu.validate_ingredients_exist(
            pan=pan,
            salchicha=salchicha,
            toppings=toppings,
            salsas=salsas,
            acompanante=acompanante,
            ingredient_collection=self.ingredientes
        )
    
    # ────────────────────────────────────────────────────────────
    # Statistics and Reporting
    # ────────────────────────────────────────────────────────────
    
    def get_summary(self) -> dict:
        """
        Get a summary of all data in the system.
        
        Returns:
            Dict with statistics from all collections
            
        Example:
            summary = handler.get_summary()
            print(f"Ingredientes: {summary['ingredientes']}")
            print(f"Hot dogs: {summary['menu']}")
        """
        return {
            'ingredientes': self.ingredientes.get_category_stats(),
            'menu': self.menu.get_stats(),
            'has_changes': self.has_changes,
        }
    
    def print_summary(self) -> None:
        """
        Print a formatted summary of all data.
        
        Example:
            handler.print_summary()
            # 
            # === RESUMEN DEL SISTEMA ===
            # 
            # Ingredientes:
            #   Pan: 2
            #   Salchicha: 3
            #   ...
            # 
            # Hot Dogs:
            #   Total: 10
            #   Combos: 3
            #   ...
        """
        summary = self.get_summary()
        
        print("\n" + "="*40)
        print("RESUMEN DEL SISTEMA")
        print("="*40)
        
        print("\nIngredientes:")
        for categoria, count in summary['ingredientes'].items():
            print(f"  {categoria}: {count}")
        
        print(f"\nTotal ingredientes: {self.ingredientes.count()}")
        
        print("\nHot Dogs:")
        menu_stats = summary['menu']
        print(f"  Total: {menu_stats['total']}")
        print(f"  Combos: {menu_stats['combos']}")
        print(f"  Simples: {menu_stats['simples']}")
        print(f"  Con toppings: {menu_stats['con_toppings']}")
        print(f"  Con salsas: {menu_stats['con_salsas']}")
        
        if summary['has_changes']:
            print("\n⚠️  Hay cambios sin guardar")
        else:
            print("\n✅ Todos los cambios guardados")
        
        print("="*40 + "\n")
    
    # ────────────────────────────────────────────────────────────
    # Context Manager Support
    # ────────────────────────────────────────────────────────────
    
    def __enter__(self):
        """
        Enter context manager (for use with 'with' statement).
        
        Returns:
            self for use in with statement
            
        Example:
            with DataHandler(data_source) as handler:
                handler.ingredientes.add(nuevo_pan)
                # Auto-commits on successful exit
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit context manager.
        
        Automatically commits if no exception occurred, otherwise rolls back.
        
        Args:
            exc_type: Exception type (None if no exception)
            exc_val: Exception value
            exc_tb: Exception traceback
            
        Returns:
            False to propagate exceptions
        """
        if exc_type is None:
            # No exception - commit changes
            if self.has_changes:
                self.commit()
        else:
            # Exception occurred - rollback changes
            if self.has_changes:
                self.rollback()
                print(f"❌ Error: {exc_val}")
        
        # Don't suppress exceptions
        return False
    
    def __repr__(self) -> str:
        """
        Get string representation of the handler.
        
        Returns:
            String showing handler state
        """
        changes_marker = " (*)" if self.has_changes else ""
        return (
            f"DataHandler("
            f"ingredientes={len(self.ingredientes)}, "
            f"menu={len(self.menu)}"
            f"{changes_marker})"
        )
