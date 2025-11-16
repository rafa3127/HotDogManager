from models.schemas.hotdog_schemas import get_hotdog_schemas
from models.core.entity_factory import create_base_class, create_entities_from_schemas

def create_hotdog_entities(raw_data=None):
    """
    Create and return hotdog entity classes.
    
    Args:
        raw_data: Optional raw menu data to infer schemas from
    
    Returns:
        Dictionary mapping entity type names to their classes.
        Example: {'HotDog': HotDogClass}
    """
    import models.plugins.hotdogs
    schemas = get_hotdog_schemas(raw_data)
    entities = create_entities_from_schemas(schemas)
    return entities

