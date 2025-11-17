"""
Main application setup and initialization.

This module is responsible for:
- Setting up the data source with all adapters
- Initializing the DataHandler
- Creating entity classes from data
- Setting up the CLI router (when menus are implemented)

Author: Rafael Correa
Date: November 16, 2025
"""

import os
from typing import Tuple

# Data layer
from clients import DataSourceClient, GitHubClient
from clients.adapters import (
    IDAdapter,
    KeyNormalizationAdapter,
    StockInitializationAdapter,
    IngredientReferenceAdapter
)
from clients.id_processors import (
    process_grouped_structure_ids,
    process_flat_structure_ids
)

# Handler layer
from handlers import DataHandler

# Entity creation
from models import (
    create_ingredient_entities,
    create_hotdog_entities,
    create_venta_entities
)

# Config
import config


# ──────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────

DATA_DIR = 'data'

# Default stock by category
DEFAULT_STOCK_CONFIG = {
    'default_stock': 50,
    'stock_by_category': {
        'pan': 1000,
        'salchicha': 1000,
        'toppings': 200,
        'salsa': 200,
        'acompañante': 1000
    }
}


# ──────────────────────────────────────────────────────
# Data Source Setup
# ──────────────────────────────────────────────────────

def setup_data_source(force_external: bool = False) -> DataSourceClient:
    """
    Sets up the complete data source with all adapters.
    
    Creates the full adapter chain:
    - GitHub → IDs → KeyNormalization → StockInit (for ingredients)
    - GitHub → IDs → KeyNormalization → IngredientRef (for menu)
    - No external source for ventas (local only)
    
    Args:
        force_external: If True, forces reload from GitHub
        
    Returns:
        Initialized DataSourceClient ready to use
    """
    print("🔧 Setting up data sources...")
    
    # ──────────────────────────────────────────────────────
    # Base GitHub client
    # ──────────────────────────────────────────────────────
    github = GitHubClient(
        owner=config.GITHUB_OWNER,
        repo=config.GITHUB_REPO,
        branch=config.GITHUB_BRANCH
    )
    
    # ──────────────────────────────────────────────────────
    # Ingredients chain: GitHub → IDs → KeyNorm → Stock
    # ──────────────────────────────────────────────────────
    print("  📦 Configuring ingredients source...")
    
    ingredientes_with_ids = IDAdapter(
        external_source=github,
        id_processor=process_grouped_structure_ids
    )
    
    ingredientes_normalized = KeyNormalizationAdapter(
        external_source=ingredientes_with_ids
    )
    
    ingredientes_source = StockInitializationAdapter(
        external_source=ingredientes_normalized,
        **DEFAULT_STOCK_CONFIG
    )
    
    # ──────────────────────────────────────────────────────
    # Menu chain: GitHub → IDs → KeyNorm → IngredientRef
    # ──────────────────────────────────────────────────────
    print("  🌭 Configuring menu source...")
    
    menu_with_ids = IDAdapter(
        external_source=github,
        id_processor=process_flat_structure_ids
    )
    
    menu_normalized = KeyNormalizationAdapter(
        external_source=menu_with_ids
    )
    
    menu_source = IngredientReferenceAdapter(
        external_source=menu_normalized,
        ingredientes_source=ingredientes_source
    )
    
    # ──────────────────────────────────────────────────────
    # Initialize DataSourceClient
    # ──────────────────────────────────────────────────────
    print("  💾 Initializing data source client...")
    
    data_source = DataSourceClient(data_dir=DATA_DIR)
    
    data_source.initialize(
        sources={
            'ingredientes': ingredientes_source,
            'menu': menu_source,
            # 'ventas' has no external source, but needs to be initialized
        },
        force_external=force_external
    )
    
    # Initialize ventas manually (no external source, only local file)
    # Load from local file if exists, otherwise create empty
    try:
        ventas_data = data_source._load_local('ventas')
        data_source._data_store['ventas'] = ventas_data
        print(f"✅ Initialized ventas (loaded {len(ventas_data)} items from local file)")
    except FileNotFoundError:
        # ventas.json doesn't exist yet, create it with empty array
        data_source.save('ventas', [])
        print("✅ Initialized ventas (created new empty file)")
    
    print("✅ Data sources ready!")
    return data_source


# ──────────────────────────────────────────────────────
# Entity Classes Setup
# ──────────────────────────────────────────────────────

def setup_entity_classes(data_source: DataSourceClient) -> Tuple:
    """
    Creates all entity classes from data.
    
    This performs schema inference and generates dynamic classes
    with all plugins (validators, methods) injected.
    
    Args:
        data_source: Initialized DataSourceClient
        
    Returns:
        Tuple of (ingredient_classes, hotdog_classes, venta_classes)
        where each is a dict of {entity_type: Class}
    """
    print("\n🏗️  Setting up entity classes...")
    
    # ──────────────────────────────────────────────────────
    # Ingredient entities (with schema inference)
    # ──────────────────────────────────────────────────────
    print("  📦 Creating ingredient entities...")
    
    ingredientes_data = data_source.get('ingredientes')
    ingredient_classes = create_ingredient_entities(ingredientes_data)
    
    print(f"     ✓ Created {len(ingredient_classes)} ingredient types")
    
    # ──────────────────────────────────────────────────────
    # HotDog entities (with schema inference)
    # ──────────────────────────────────────────────────────
    print("  🌭 Creating hotdog entities...")
    
    menu_data = data_source.get('menu')
    hotdog_classes = create_hotdog_entities(menu_data)
    
    print(f"     ✓ Created {len(hotdog_classes)} hotdog types")
    
    # ──────────────────────────────────────────────────────
    # Venta entities (hardcoded schema, no external data)
    # ──────────────────────────────────────────────────────
    print("  💰 Creating venta entities...")
    
    venta_classes = create_venta_entities()
    
    print(f"     ✓ Created {len(venta_classes)} venta types")
    
    print("✅ Entity classes ready!")
    
    return ingredient_classes, hotdog_classes, venta_classes


# ──────────────────────────────────────────────────────
# DataHandler Setup
# ──────────────────────────────────────────────────────

def setup_handler(data_source: DataSourceClient) -> DataHandler:
    """
    Creates the DataHandler with all collections.
    
    Args:
        data_source: Initialized DataSourceClient
        
    Returns:
        DataHandler ready to use
    """
    print("\n📊 Setting up data handler...")
    
    handler = DataHandler(data_source)
    
    print(f"  ✓ Ingredientes: {len(handler.ingredientes)} items")
    print(f"  ✓ Menu: {len(handler.menu)} items")
    print(f"  ✓ Ventas: {len(handler.ventas)} items")
    
    print("✅ Data handler ready!")
    
    return handler


# ──────────────────────────────────────────────────────
# Complete Application Setup
# ──────────────────────────────────────────────────────

def initialize_application(force_external: bool = False) -> Tuple[DataHandler, dict]:
    """
    Complete application initialization.
    
    This is the main entry point for setting up the entire system:
    1. Data sources with adapter chains
    2. Entity classes with schema inference
    3. DataHandler with all collections
    
    Args:
        force_external: If True, forces reload from GitHub
        
    Returns:
        Tuple of (handler, entity_classes) where:
        - handler: DataHandler ready to use
        - entity_classes: Dict with all entity classes organized by type
    """
    print("=" * 60)
    print("🌭 HOT DOG CCS - APPLICATION INITIALIZATION")
    print("=" * 60)
    
    # ──────────────────────────────────────────────────────
    # Step 1: Data sources
    # ──────────────────────────────────────────────────────
    data_source = setup_data_source(force_external=force_external)
    
    # ──────────────────────────────────────────────────────
    # Step 2: Entity classes
    # ──────────────────────────────────────────────────────
    ingredient_classes, hotdog_classes, venta_classes = setup_entity_classes(data_source)
    
    # ──────────────────────────────────────────────────────
    # Step 3: DataHandler
    # ──────────────────────────────────────────────────────
    handler = setup_handler(data_source)
    
    # ──────────────────────────────────────────────────────
    # Organize entity classes for easy access
    # ──────────────────────────────────────────────────────
    entity_classes = {
        'ingredients': ingredient_classes,
        'hotdogs': hotdog_classes,
        'ventas': venta_classes
    }
    
    print("\n" + "=" * 60)
    print("✅ APPLICATION READY!")
    print("=" * 60 + "\n")
    
    return handler, entity_classes


# ──────────────────────────────────────────────────────
# CLI Setup (will be implemented when menus are ready)
# ──────────────────────────────────────────────────────

def setup_cli(handler: DataHandler, entity_classes: dict):
    """
    Sets up the CLI router with all menus.
    
    Registers all menu definitions and configures the router context
    with handler and entity classes.
    
    Args:
        handler: Initialized DataHandler
        entity_classes: Dict with all entity classes
        
    Returns:
        Configured MenuRouter ready to run
    """
    from cli.core import MenuRouter
    from cli.menus import (
        create_main_menu, 
        create_not_found_menu, 
        create_ingredients_menu,
        create_menu_hotdogs_menu,
        create_ventas_menu,
        create_reportes_menu,
        create_debug_menu
    )
    
    print("🎮 Setting up CLI router...")
    
    # Create router
    router = MenuRouter()
    
    # Configure context (shared across all actions)
    router.context['handler'] = handler
    router.context['entity_classes'] = entity_classes
    
    # Register menus
    router.register_menu(create_main_menu())
    router.register_menu(create_not_found_menu())  # Fallback for non-existent routes
    router.register_menu(create_ingredients_menu())  # Ingredients management
    router.register_menu(create_menu_hotdogs_menu())  # Menu (Hot Dogs) management
    router.register_menu(create_ventas_menu())  # Sales management
    router.register_menu(create_reportes_menu())  # Reports and charts
    router.register_menu(create_debug_menu())  # Debug/diagnostics
    
    print("✅ CLI router ready!")
    
    return router


def run_cli(handler: DataHandler, entity_classes: dict):
    """
    Main CLI entry point.
    
    Sets up the router and starts the main navigation loop.
    
    Args:
        handler: Initialized DataHandler
        entity_classes: Dict with all entity classes
    """
    # Setup router with all menus
    router = setup_cli(handler, entity_classes)
    
    # Navigate to main menu
    router.navigate_to('main')
    
    # Start main loop
    router.run()


# ──────────────────────────────────────────────────────
# Test/Debug Entry Point
# ──────────────────────────────────────────────────────

if __name__ == "__main__":
    """
    Test/Debug entry point.
    
    Runs the full CLI application for testing.
    Use this to test the application: python app.py
    """
    try:
        # Initialize and run CLI
        handler, entity_classes = initialize_application(force_external=False)
        run_cli(handler, entity_classes)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error during initialization: {e}")
        import traceback
        traceback.print_exc()
