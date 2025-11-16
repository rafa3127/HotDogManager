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
        'pan': 100,
        'salchicha': 75,
        'toppings': 200,
        'salsa': 150,
        'acompañante': 80
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
    # If ventas.json doesn't exist, create empty list
    try:
        data_source.get('ventas')
    except KeyError:
        # ventas.json doesn't exist yet, create it with empty array
        data_source.save('ventas', [])
    
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
    
    This will be implemented once menus are created.
    
    Args:
        handler: Initialized DataHandler
        entity_classes: Dict with all entity classes
        
    Returns:
        Configured MenuRouter ready to run
    """
    # TODO: Implement when menus are ready
    
    raise NotImplementedError("CLI menus not implemented yet")


def run_cli(handler: DataHandler, entity_classes: dict):
    """
    Main CLI entry point.
    
    This will be implemented once menus are ready.
    
    Args:
        handler: Initialized DataHandler
        entity_classes: Dict with all entity classes
    """
    # TODO: Implement when menus are ready
    # router = setup_cli(handler, entity_classes)
    # router.run()
    
    raise NotImplementedError("CLI menus not implemented yet")


# ──────────────────────────────────────────────────────
# Test/Debug Entry Point
# ──────────────────────────────────────────────────────

if __name__ == "__main__":
    """
    Test the application setup.
    
    This is useful for debugging - it initializes everything and shows
    the status without running the CLI.
    """
    try:
        handler, entity_classes = initialize_application(force_external=False)
        
        # Show summary
        print("\n📊 SYSTEM SUMMARY")
        print("-" * 60)
        handler.print_summary()
        
        print("\n✅ Application initialized successfully!")
        print("   (CLI menus not implemented yet)")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error during initialization: {e}")
        import traceback
        traceback.print_exc()
