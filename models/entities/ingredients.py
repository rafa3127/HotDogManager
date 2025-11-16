from models.schemas.ingredient_schemas import get_ingredient_schemas
from models.core.entity_factory import create_base_class, create_entities_from_schemas


def create_ingredient_entities(raw_data=None):
    """
    Create and return all ingredient entity classes.
    
    Args:
        raw_data: Optional raw ingredient data to infer schemas from.
                  If None, uses fallback hardcoded schemas.
    
    Returns:
        Dictionary mapping entity type names to their classes.
        Includes 'Ingredient' (base class) and all specific types.
        Example: {'Ingredient': IngredientClass, 'Pan': PanClass, ...}
    """
    import models.plugins.ingredients 
    
    # Infer or use fallback schemas
    specific_schemas, common_props = get_ingredient_schemas(raw_data)
    
    # Create base Ingredient class
    Ingredient = create_base_class('Ingredient', common_props)
    
    # Create specific classes
    entities = create_entities_from_schemas(specific_schemas, base_class=Ingredient)
    
    # Add base class to the dict
    entities['Ingredient'] = Ingredient
    
    return entities