from models.schemas.ingredient_schemas import get_ingredient_schemas
from models.core.entity_factory import create_base_class, create_entities_from_schemas


def create_ingredient_entities(raw_data=None):
    """
    Create and return all ingredient entity classes.
    
    Args:
        raw_data: Optional raw ingredient data to infer schemas from.
                  If None, uses fallback hardcoded schemas.
    
    Returns:
        Tuple of (Ingredient, Pan, Salchicha, Topping, Salsa, Acompañante)
    """
    import models.plugins.ingredients 
    
    # Infer or use fallback schemas
    specific_schemas, common_props = get_ingredient_schemas(raw_data)
    
    # Create base Ingredient class
    Ingredient = create_base_class('Ingredient', common_props)
    
    # Create specific classes
    entities = create_entities_from_schemas(specific_schemas, base_class=Ingredient)
    
    Pan = entities['Pan']
    Salchicha = entities['Salchicha']
    Topping = entities['Topping']
    Salsa = entities['Salsa']
    Acompañante = entities['Acompañante']
    
    return Ingredient, Pan, Salchicha, Topping, Salsa, Acompañante