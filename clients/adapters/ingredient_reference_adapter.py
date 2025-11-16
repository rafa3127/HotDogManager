"""
Ingredient Reference Adapter

Converts ingredient name references in menu items to structured objects with {id, nombre}.

This adapter processes menu data (hot dogs) and replaces string references to ingredients
with objects containing both the ID and name of the ingredient. This enables proper
relational integrity using IDs while maintaining human-readable names.

Author: Rafael Correa
Date: November 16, 2025
"""

from typing import Dict, List, Any, Optional
from clients.external_sources.external_source_client import ExternalSourceClient


class IngredientReferenceAdapter(ExternalSourceClient):
    """
    Adapter that converts ingredient name references to {id, nombre} objects.
    
    This adapter transforms menu items (hot dogs) by replacing string ingredient
    names with structured objects containing both ID and name.
    
    Example transformation:
        BEFORE: {"pan": "simple", "salchicha": "weiner", ...}
        AFTER:  {"pan": {"id": "pan_simple_abc", "nombre": "simple"}, ...}
    
    Args:
        external_source: Source client that provides menu data
        ingredientes_source: Source client that provides ingredients data (will be fetched once)
    """
    
    def __init__(
        self,
        external_source: ExternalSourceClient,
        ingredientes_source: ExternalSourceClient
    ):
        """
        Initialize the adapter.
        
        Args:
            external_source: Source providing menu data
            ingredientes_source: Source providing ingredients with IDs (will fetch once on first use)
        """
        self.external_source = external_source
        self.ingredientes_source = ingredientes_source
        self._ingredientes_lookup: Optional[Dict[str, Dict[str, str]]] = None
        self._ingredientes_fetched = False
    
    def _build_ingredientes_lookup(self, ingredientes_data: Any) -> Dict[str, Dict[str, str]]:
        """
        Build a lookup table: {categoria: {nombre: id}}.
        
        Args:
            ingredientes_data: Ingredients data structure (can be list or dict)
        
        Returns:
            Nested dict for fast ingredient ID lookup
        
        Example:
            {
                'Pan': {'simple': 'pan_simple_abc123', 'frances': 'pan_frances_def456'},
                'Salchicha': {'weiner': 'salchicha_weiner_ghi789'},
                ...
            }
        """
        lookup = {}
        
        # Handle GROUPED structure as list (after normalization)
        # Format: [{'categoria': 'pan', 'opciones': [...]}, ...]
        if isinstance(ingredientes_data, list):
            for group in ingredientes_data:
                if not isinstance(group, dict):
                    continue
                
                # Get category name (normalized key)
                categoria = group.get('categoria')
                opciones = group.get('opciones', [])
                
                if not categoria or not isinstance(opciones, list):
                    continue
                
                # Capitalize categoria for lookup (Pan, Salchicha, etc.)
                categoria_key = categoria.capitalize()
                lookup[categoria_key] = {}
                
                # Build name -> id mapping
                for item in opciones:
                    if isinstance(item, dict) and 'id' in item and 'nombre' in item:
                        nombre = item['nombre']
                        item_id = item['id']
                        lookup[categoria_key][nombre] = item_id
        
        # Handle GROUPED structure as dict (original format)
        # Format: {'Pan': [...], 'Salchicha': [...], ...}
        elif isinstance(ingredientes_data, dict):
            for categoria, items in ingredientes_data.items():
                if not isinstance(items, list):
                    continue
                
                lookup[categoria] = {}
                
                # Build name -> id mapping
                for item in items:
                    if isinstance(item, dict) and 'id' in item and 'nombre' in item:
                        nombre = item['nombre']
                        item_id = item['id']
                        lookup[categoria][nombre] = item_id
        
        return lookup
    
    def _get_ingredient_id(self, nombre: str, categoria: str) -> Optional[str]:
        """
        Get ingredient ID by name and category.
        
        Args:
            nombre: Ingredient name
            categoria: Ingredient category
        
        Returns:
            Ingredient ID or None if not found
        """
        if not self._ingredientes_lookup:
            return None
        
        categoria_lookup = self._ingredientes_lookup.get(categoria, {})
        return categoria_lookup.get(nombre)
    
    def _convert_reference(
        self,
        nombre: Optional[str],
        categoria: str
    ) -> Optional[Dict[str, str]]:
        """
        Convert a name reference to {id, nombre} object.
        
        Args:
            nombre: Ingredient name (can be None)
            categoria: Ingredient category
        
        Returns:
            Dict with {id, nombre} or None if input is None or not found
        """
        if nombre is None:
            return None
        
        ingredient_id = self._get_ingredient_id(nombre, categoria)
        
        if ingredient_id is None:
            # If ingredient not found, return None to maintain data integrity
            # The service layer will handle validation
            return None
        
        return {
            'id': ingredient_id,
            'nombre': nombre
        }
    
    def _convert_reference_list(
        self,
        nombres: Optional[List[str]],
        categoria: str
    ) -> List[Dict[str, str]]:
        """
        Convert a list of name references to list of {id, nombre} objects.
        
        Args:
            nombres: List of ingredient names (can be None or empty)
            categoria: Ingredient category
        
        Returns:
            List of dicts with {id, nombre}, skipping any not found
        """
        if not nombres:
            return []
        
        result = []
        for nombre in nombres:
            ref = self._convert_reference(nombre, categoria)
            if ref is not None:
                result.append(ref)
        
        return result
    
    def _process_hotdog(self, hotdog: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single hot dog, converting ingredient references.
        
        Args:
            hotdog: Hot dog data dict
        
        Returns:
            Hot dog with converted references
        """
        processed = hotdog.copy()
        
        # Convert pan (single reference)
        if 'pan' in processed and isinstance(processed['pan'], str):
            processed['pan'] = self._convert_reference(processed['pan'], 'Pan')
        
        # Convert salchicha (single reference)
        if 'salchicha' in processed and isinstance(processed['salchicha'], str):
            processed['salchicha'] = self._convert_reference(processed['salchicha'], 'Salchicha')
        
        # Convert toppings (list of references)
        if 'toppings' in processed and isinstance(processed['toppings'], list):
            # Only convert if list contains strings
            if all(isinstance(t, str) for t in processed['toppings']):
                processed['toppings'] = self._convert_reference_list(processed['toppings'], 'Toppings')
        
        # Convert salsas (list of references)
        if 'salsas' in processed and isinstance(processed['salsas'], list):
            # Only convert if list contains strings
            if all(isinstance(s, str) for s in processed['salsas']):
                processed['salsas'] = self._convert_reference_list(processed['salsas'], 'Salsa')
        
        # Convert acompañante (single reference, nullable)
        if 'acompanante' in processed and isinstance(processed['acompanante'], str):
            processed['acompanante'] = self._convert_reference(processed['acompanante'], 'Acompañante')
        
        return processed
    
    def fetch_data(self, identifier: str, **kwargs) -> Any:
        """
        Fetch and process menu data, converting ingredient references.
        
        Args:
            identifier: Data identifier
            **kwargs: Additional arguments
        
        Returns:
            Menu data with ingredient references converted to {id, nombre} objects
        """
        # Fetch ingredientes ONCE on first call
        if not self._ingredientes_fetched:
            ingredientes_data = self.ingredientes_source.fetch_data('ingredientes.json', **kwargs)
            self._ingredientes_lookup = self._build_ingredientes_lookup(ingredientes_data)
            self._ingredientes_fetched = True
        
        # Fetch menu data
        menu_data = self.external_source.fetch_data(identifier, **kwargs)
        
        # Process menu data (lookup already built)
        if isinstance(menu_data, list):
            # FLAT structure (list of hot dogs)
            return [self._process_hotdog(hotdog) for hotdog in menu_data]
        
        elif isinstance(menu_data, dict):
            # GROUPED structure (categories with lists)
            processed = {}
            for key, value in menu_data.items():
                if isinstance(value, list):
                    processed[key] = [self._process_hotdog(item) for item in value]
                else:
                    processed[key] = value
            return processed
        
        else:
            # Unknown structure, return as-is
            return menu_data
