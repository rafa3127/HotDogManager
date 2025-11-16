"""
Debug menu - System introspection and diagnostics.

Allows inspection of entity classes, categories, and system state.

Author: Rafael Correa
Date: November 16, 2025
"""

from cli.core import MenuDefinition, MenuOption, ActionResult, Views, Colors


def action_show_entity_classes(context: dict) -> ActionResult:
    """
    Shows all entity classes available in the system.
    
    Args:
        context: Router context with entity_classes
        
    Returns:
        ActionResult
    """
    entity_classes = context.get('entity_classes', {})
    
    Views.clear_screen()
    Views.print_header("ENTITY CLASSES - SYSTEM INTROSPECTION")
    
    print("\n" + Colors.bold("Available Entity Classes:"))
    print("=" * 60)
    
    for module_name, classes in entity_classes.items():
        print(f"\n{Colors.blue(Colors.bold(f'{module_name.upper()}:'))}")
        
        if isinstance(classes, dict):
            for class_name, class_obj in classes.items():
                print(f"  • {Colors.green(class_name)}")
                
                # Show properties if it's a dataclass
                if hasattr(class_obj, '__dataclass_fields__'):
                    fields = class_obj.__dataclass_fields__.keys()
                    print(f"    Properties: {', '.join(fields)}")
        else:
            print(f"  {type(classes)}")
    
    Views.pause()
    return ActionResult.success()


def action_show_categories(context: dict) -> ActionResult:
    """
    Shows all categories from the ingredient collection.
    
    Args:
        context: Router context with handler
        
    Returns:
        ActionResult
    """
    handler = context['handler']
    
    Views.clear_screen()
    Views.print_header("CATEGORIES - FROM COLLECTION")
    
    categories = handler.ingredientes.get_categories()
    
    print("\n" + Colors.bold("Categories in collection:"))
    print("=" * 60)
    
    for i, cat in enumerate(categories, 1):
        print(f"{i}. {Colors.green(cat)}")
        print(f"   Type: {type(cat)}")
        print(f"   Repr: {repr(cat)}")
        print(f"   Bytes: {cat.encode('utf-8')}")
    
    Views.pause()
    return ActionResult.success()


def action_compare_classes_vs_categories(context: dict) -> ActionResult:
    """
    Compares entity classes with collection categories.
    
    Args:
        context: Router context
        
    Returns:
        ActionResult
    """
    handler = context['handler']
    entity_classes = context.get('entity_classes', {})
    
    Views.clear_screen()
    Views.print_header("CLASSES vs CATEGORIES - COMPARISON")
    
    # Get ingredient classes
    ingredient_classes = entity_classes.get('ingredients', {})
    
    # Get categories from collection
    categories = handler.ingredientes.get_categories()
    
    print("\n" + Colors.bold("INGREDIENT CLASSES:"))
    print("-" * 60)
    for class_name in ingredient_classes.keys():
        print(f"  • {Colors.blue(class_name)}")
    
    print("\n" + Colors.bold("COLLECTION CATEGORIES:"))
    print("-" * 60)
    for cat in categories:
        print(f"  • {Colors.green(cat)}")
    
    print("\n" + Colors.bold("MATCHING ANALYSIS:"))
    print("-" * 60)
    
    for cat in categories:
        if cat in ingredient_classes:
            print(f"  ✅ {cat} - MATCH")
        else:
            print(f"  ❌ {cat} - NO MATCH")
            print(f"      Looking for: '{cat}'")
            print(f"      Available: {list(ingredient_classes.keys())}")
    
    Views.pause()
    return ActionResult.success()


def create_debug_menu() -> MenuDefinition:
    """
    Creates the debug/diagnostics menu.
    
    Returns:
        MenuDefinition for debug menu
    """
    return MenuDefinition(
        id='debug',
        title='🔧 DEBUG - SYSTEM DIAGNOSTICS',
        description='Inspect entity classes, categories, and system state',
        options=[
            MenuOption(
                key='1',
                label='📋 Show Entity Classes',
                action=action_show_entity_classes
            ),
            
            MenuOption(
                key='2',
                label='📦 Show Categories',
                action=action_show_categories
            ),
            
            MenuOption(
                key='3',
                label='🔍 Compare Classes vs Categories',
                action=action_compare_classes_vs_categories
            ),
        ],
        parent_menu='main',
        auto_add_back=True,
        auto_add_exit=True,
        clear_screen=True
    )
