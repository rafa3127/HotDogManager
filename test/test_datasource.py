"""
Comprehensive test suite for DataSource and Adapter system.

Tests the complete chain of adapters from GitHub to persisted local files,
verifying that all transformations (IDs, key normalization, stock, and 
ingredient references) work correctly and persist properly.

Author: Rafael Correa
Date: November 15, 2025
"""

import sys
import os
import json

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from clients.external_sources.github_client import GitHubClient
from clients.data_source_client import DataSourceClient
from clients.adapters import (
    IDAdapter,
    KeyNormalizationAdapter,
    StockInitializationAdapter,
    IngredientReferenceAdapter
)
from clients.id_processors import (
    generate_stable_id,
    process_grouped_structure_ids,
    process_flat_structure_ids
)
import config


def test_1_github_client_raw():
    """Test 1: GitHub client fetches raw data without any transformations."""
    print("\n" + "=" * 70)
    print("🧪 Test 1: GitHub Client - Raw Data Fetch")
    print("=" * 70)
    
    github = GitHubClient(
        owner=config.GITHUB_OWNER,
        repo=config.GITHUB_REPO,
        branch=config.GITHUB_BRANCH
    )
    
    # Fetch ingredientes
    print("\n📥 Fetching ingredientes.json from GitHub...")
    ingredientes = github.fetch_data("ingredientes.json")
    
    assert isinstance(ingredientes, list), "Should return a list"
    assert len(ingredientes) > 0, "Should have data"
    
    first_group = ingredientes[0]
    assert 'Categoria' in first_group, "Raw data has 'Categoria' (capital C)"
    assert 'Opciones' in first_group, "Raw data has 'Opciones' (capital O)"
    
    first_item = first_group['Opciones'][0]
    assert 'id' not in first_item, "Raw data should NOT have IDs"
    assert 'stock' not in first_item, "Raw data should NOT have stock"
    
    print(f"✅ Fetched {len(ingredientes)} categories")
    print(f"   First category: {first_group['Categoria']}")
    print(f"   First item: {first_item['nombre']}")
    print(f"   Keys are original (not normalized): {list(first_group.keys())}")
    
    # Fetch menu
    print("\n📥 Fetching menu.json from GitHub...")
    menu = github.fetch_data("menu.json")
    
    assert isinstance(menu, list), "Should return a list"
    assert len(menu) > 0, "Should have data"
    
    first_hotdog = menu[0]
    # Some hotdogs might not have all fields, check if pan exists
    if 'pan' in first_hotdog:
        assert isinstance(first_hotdog['pan'], str), "Ingredients should be strings (not objects)"
        print(f"✅ Fetched {len(menu)} hot dogs")
        print(f"   First hotdog: {first_hotdog['nombre']}")
        print(f"   Pan is string: '{first_hotdog['pan']}' (not object yet)")
    else:
        print(f"✅ Fetched {len(menu)} hot dogs")
        print(f"   First hotdog: {first_hotdog['nombre']}")
        print(f"   Note: This hotdog doesn't have 'pan' field (nullable)")
    
    print("\n✅ Test 1 PASSED: GitHub client works correctly\n")


def test_2_stable_ids():
    """Test 2: Stable ID generation is deterministic."""
    print("\n" + "=" * 70)
    print("🧪 Test 2: Stable ID Generation")
    print("=" * 70)
    
    # Same input = same ID
    id1 = generate_stable_id("simple", "Pan")
    id2 = generate_stable_id("simple", "Pan")
    assert id1 == id2, "Same input should produce same ID"
    print(f"\n✅ Deterministic: Pan:simple → {id1}")
    
    # Different input = different ID
    id_pan = generate_stable_id("simple", "Pan")
    id_salsa = generate_stable_id("simple", "Salsa")
    assert id_pan != id_salsa, "Different category should produce different ID"
    print(f"✅ Category matters: Pan:simple ≠ Salsa:simple")
    
    # Valid UUID format
    parts = id1.split('-')
    assert len(parts) == 5, "Should be valid UUID format"
    assert len(parts[0]) == 8, "UUID part 1 should be 8 chars"
    print(f"✅ Valid UUID format: {id1}")
    
    print("\n✅ Test 2 PASSED: IDs are stable and deterministic\n")


def test_3_id_adapter():
    """Test 3: ID Adapter adds IDs to data."""
    print("\n" + "=" * 70)
    print("🧪 Test 3: ID Adapter")
    print("=" * 70)
    
    github = GitHubClient(
        owner=config.GITHUB_OWNER,
        repo=config.GITHUB_REPO,
        branch=config.GITHUB_BRANCH
    )
    
    # Test with GROUPED structure (ingredientes)
    print("\n📋 Testing with GROUPED structure (ingredientes)...")
    adapter = IDAdapter(github, process_grouped_structure_ids)
    ingredientes = adapter.fetch_data("ingredientes.json")
    
    first_item = ingredientes[0]['Opciones'][0]
    assert 'id' in first_item, "Should have ID"
    print(f"✅ {first_item['nombre']} → ID: {first_item['id']}")
    
    # Test with FLAT structure (menu)
    print("\n📋 Testing with FLAT structure (menu)...")
    adapter = IDAdapter(github, process_flat_structure_ids)
    menu = adapter.fetch_data("menu.json")
    
    first_hotdog = menu[0]
    assert 'id' in first_hotdog, "Should have ID"
    print(f"✅ {first_hotdog['nombre']} → ID: {first_hotdog['id']}")
    
    # Test stability
    ingredientes2 = IDAdapter(github, process_grouped_structure_ids).fetch_data("ingredientes.json")
    assert ingredientes[0]['Opciones'][0]['id'] == ingredientes2[0]['Opciones'][0]['id']
    print(f"✅ IDs are stable across fetches")
    
    print("\n✅ Test 3 PASSED: ID Adapter works correctly\n")


def test_4_key_normalization_adapter():
    """Test 4: Key Normalization Adapter normalizes keys."""
    print("\n" + "=" * 70)
    print("🧪 Test 4: Key Normalization Adapter")
    print("=" * 70)
    
    github = GitHubClient(
        owner=config.GITHUB_OWNER,
        repo=config.GITHUB_REPO,
        branch=config.GITHUB_BRANCH
    )
    
    # Test with GROUPED structure
    print("\n📋 Testing with GROUPED structure...")
    adapter = KeyNormalizationAdapter(github)
    ingredientes = adapter.fetch_data("ingredientes.json")
    
    first_group = ingredientes[0]
    assert 'categoria' in first_group, "Should have 'categoria' (lowercase)"
    assert 'opciones' in first_group, "Should have 'opciones' (lowercase)"
    assert 'Categoria' not in first_group, "Should NOT have 'Categoria'"
    
    print(f"✅ Keys normalized: {list(first_group.keys())}")
    
    # Test with FLAT structure
    print("\n📋 Testing with FLAT structure...")
    menu = adapter.fetch_data("menu.json")
    
    first_hotdog = menu[0]
    all_lowercase = all(key.islower() for key in first_hotdog.keys())
    assert all_lowercase, "All keys should be lowercase"
    
    print(f"✅ All keys lowercase: {list(first_hotdog.keys())}")
    
    print("\n✅ Test 4 PASSED: Key Normalization works correctly\n")


def test_5_stock_initialization_adapter():
    """Test 5: Stock Initialization Adapter adds stock field."""
    print("\n" + "=" * 70)
    print("🧪 Test 5: Stock Initialization Adapter")
    print("=" * 70)
    
    github = GitHubClient(
        owner=config.GITHUB_OWNER,
        repo=config.GITHUB_REPO,
        branch=config.GITHUB_BRANCH
    )
    
    # Chain: GitHub → IDs → KeyNorm → Stock
    print("\n🔗 Building chain: GitHub → IDs → KeyNorm → Stock...")
    adapter = StockInitializationAdapter(
        KeyNormalizationAdapter(
            IDAdapter(github, process_grouped_structure_ids)
        ),
        default_stock=50,
        stock_by_category={
            'pan': 100,
            'salchicha': 75,
            'toppings': 200,
            'salsa': 150,
            'acompañante': 80
        }
    )
    
    ingredientes = adapter.fetch_data("ingredientes.json")
    
    # Verify stock was added
    print("\n📊 Verifying stock by category:")
    for group in ingredientes:
        categoria = group['categoria']
        first_item = group['opciones'][0]
        
        assert 'stock' in first_item, f"Should have stock in {categoria}"
        stock = first_item['stock']
        
        print(f"   {categoria.capitalize():15s} → stock: {stock}")
        
        # Verify correct values
        if categoria == 'pan':
            assert stock == 100
        elif categoria == 'salchicha':
            assert stock == 75
        elif categoria == 'toppings':
            assert stock == 200
        elif categoria == 'salsa':
            assert stock == 150
        elif categoria == 'acompañante':
            assert stock == 80
    
    print("\n✅ Test 5 PASSED: Stock initialization works correctly\n")


def test_6_ingredient_reference_adapter():
    """Test 6: Ingredient Reference Adapter converts names to {id, nombre} objects."""
    print("\n" + "=" * 70)
    print("🧪 Test 6: Ingredient Reference Adapter")
    print("=" * 70)
    
    github = GitHubClient(
        owner=config.GITHUB_OWNER,
        repo=config.GITHUB_REPO,
        branch=config.GITHUB_BRANCH
    )
    
    # Setup ingredientes source (fully processed)
    print("\n🔗 Building ingredientes chain: GitHub → IDs → KeyNorm → Stock...")
    ingredientes_source = StockInitializationAdapter(
        KeyNormalizationAdapter(
            IDAdapter(github, process_grouped_structure_ids)
        ),
        default_stock=50
    )
    
    # Setup menu with IngredientReferenceAdapter
    print("🔗 Building menu chain: GitHub → IDs → KeyNorm → IngredientRef...")
    menu_adapter = IngredientReferenceAdapter(
        KeyNormalizationAdapter(
            IDAdapter(github, process_flat_structure_ids)
        ),
        ingredientes_source
    )
    
    menu = menu_adapter.fetch_data("menu.json")
    
    # Verify conversion
    first_hotdog = menu[0]
    print(f"\n🔍 Inspecting: {first_hotdog['nombre']}")
    
    # Check pan
    pan = first_hotdog['pan']
    assert isinstance(pan, dict), "Pan should be an object"
    assert 'id' in pan and 'nombre' in pan, "Pan should have id and nombre"
    print(f"   ✅ Pan: {{id: '{pan['id'][:25]}...', nombre: '{pan['nombre']}'}}")
    
    # Check salchicha
    salchicha = first_hotdog['salchicha']
    assert isinstance(salchicha, dict), "Salchicha should be an object"
    print(f"   ✅ Salchicha: {{id: '{salchicha['id'][:25]}...', nombre: '{salchicha['nombre']}'}}")
    
    # Check toppings (list)
    if first_hotdog.get('toppings') and len(first_hotdog['toppings']) > 0:
        topping = first_hotdog['toppings'][0]
        assert isinstance(topping, dict), "Topping should be an object"
        print(f"   ✅ Topping: {{id: '{topping['id'][:25]}...', nombre: '{topping['nombre']}'}}")
    
    print("\n✅ Test 6 PASSED: Ingredient references converted correctly\n")


def test_7_full_integration_with_persistence():
    """Test 7: COMPLETE integration - All adapters + DataSource + Persistence."""
    print("\n" + "=" * 70)
    print("🧪 Test 7: FULL INTEGRATION - All Adapters + Persistence")
    print("=" * 70)
    
    github = GitHubClient(
        owner=config.GITHUB_OWNER,
        repo=config.GITHUB_REPO,
        branch=config.GITHUB_BRANCH
    )
    
    print("\n🔗 Building COMPLETE adapter chains...")
    print("-" * 70)
    
    # Ingredientes: GitHub → IDs → KeyNorm → Stock
    ingredientes_source = StockInitializationAdapter(
        KeyNormalizationAdapter(
            IDAdapter(github, process_grouped_structure_ids)
        ),
        default_stock=50,
        stock_by_category={
            'pan': 100,
            'salchicha': 75,
            'toppings': 200,
            'salsa': 150,
            'acompañante': 80
        }
    )
    print("✅ Ingredientes chain: GitHub → IDs → KeyNorm → Stock")
    
    # Menu: GitHub → IDs → KeyNorm → IngredientRef
    menu_source = IngredientReferenceAdapter(
        KeyNormalizationAdapter(
            IDAdapter(github, process_flat_structure_ids)
        ),
        ingredientes_source
    )
    print("✅ Menu chain: GitHub → IDs → KeyNorm → IngredientRef")
    
    # Initialize DataSource (this will persist everything)
    print("\n💾 Initializing DataSource with force_external=True...")
    data_source = DataSourceClient(data_dir=config.DATA_DIR)
    data_source.initialize(
        sources={
            'ingredientes': ingredientes_source,
            'menu': menu_source
        },
        force_external=True
    )
    print("✅ DataSource initialized - ALL DATA FETCHED AND PERSISTED")
    
    # Verify ingredientes in memory
    print("\n🔍 Verifying ingredientes in memory...")
    print("-" * 70)
    ingredientes = data_source.get('ingredientes')
    
    first_group = ingredientes[0]
    first_item = first_group['opciones'][0]
    
    assert 'categoria' in first_group, "Should have normalized keys"
    assert 'id' in first_item, "Should have ID"
    assert 'stock' in first_item, "Should have stock"
    
    print(f"✅ Loaded {len(ingredientes)} categories")
    print(f"   Category: {first_group['categoria']}")
    print(f"   Item: {first_item['nombre']}")
    print(f"   - ID: {first_item['id'][:35]}...")
    print(f"   - Stock: {first_item['stock']}")
    print(f"   - Keys: {list(first_group.keys())}")
    
    # Verify menu in memory
    print("\n🔍 Verifying menu in memory...")
    print("-" * 70)
    menu = data_source.get('menu')
    
    first_hotdog = menu[0]
    
    assert 'id' in first_hotdog, "Should have ID"
    assert isinstance(first_hotdog['pan'], dict), "Pan should be object"
    assert 'id' in first_hotdog['pan'], "Pan should have id"
    
    print(f"✅ Loaded {len(menu)} hot dogs")
    print(f"   Hotdog: {first_hotdog['nombre']}")
    print(f"   - ID: {first_hotdog['id'][:35]}...")
    print(f"   - Pan: {{id: '{first_hotdog['pan']['id'][:25]}...', nombre: '{first_hotdog['pan']['nombre']}'}}")
    print(f"   - Keys: {list(first_hotdog.keys())}")
    
    # Verify persistence in files
    print("\n💾 Verifying persistence in JSON files...")
    print("-" * 70)
    
    # Check ingredientes.json
    with open('data/ingredientes.json', 'r', encoding='utf-8') as f:
        saved_ingredientes = json.load(f)
    
    saved_group = saved_ingredientes[0]
    saved_item = saved_group['opciones'][0]
    
    assert 'categoria' in saved_group, "File should have normalized keys"
    assert 'id' in saved_item, "File should have IDs"
    assert 'stock' in saved_item, "File should have stock"
    
    print(f"✅ ingredientes.json saved correctly")
    print(f"   - Has normalized keys: {list(saved_group.keys())}")
    print(f"   - Has IDs: {saved_item['id'][:35]}...")
    print(f"   - Has stock: {saved_item['stock']}")
    
    # Check menu.json
    with open('data/menu.json', 'r', encoding='utf-8') as f:
        saved_menu = json.load(f)
    
    saved_hotdog = saved_menu[0]
    saved_pan = saved_hotdog['pan']
    
    assert 'id' in saved_hotdog, "File should have IDs"
    assert isinstance(saved_pan, dict), "File should have pan as object"
    assert 'id' in saved_pan and 'nombre' in saved_pan, "Pan should have id and nombre"
    
    print(f"✅ menu.json saved correctly")
    print(f"   - Has IDs: {saved_hotdog['id'][:35]}...")
    print(f"   - Has ingredient refs: pan = {{id: '{saved_pan['id'][:25]}...', nombre: '{saved_pan['nombre']}'}}")
    
    # Verify reload from files
    print("\n🔄 Verifying reload from local files...")
    print("-" * 70)
    
    data_source_2 = DataSourceClient(data_dir=config.DATA_DIR)
    data_source_2.initialize(
        sources={
            'ingredientes': ingredientes_source,
            'menu': menu_source
        },
        force_external=False  # Load from local files
    )
    
    reloaded_ingredientes = data_source_2.get('ingredientes')
    reloaded_menu = data_source_2.get('menu')
    
    assert reloaded_ingredientes[0]['opciones'][0]['id'] == first_item['id']
    assert reloaded_menu[0]['id'] == first_hotdog['id']
    
    print(f"✅ Reloaded from local files successfully")
    print(f"   - Ingredientes ID matches: {reloaded_ingredientes[0]['opciones'][0]['id'][:35]}...")
    print(f"   - Menu ID matches: {reloaded_menu[0]['id'][:35]}...")
    
    print("\n" + "=" * 70)
    print("🎉 TEST 7 PASSED - FULL INTEGRATION SUCCESSFUL!")
    print("=" * 70)
    print("\n📊 Summary of what was tested:")
    print("   ✅ All adapters work together in chains")
    print("   ✅ IDs are stable and deterministic")
    print("   ✅ Keys are normalized (lowercase, no accents)")
    print("   ✅ Stock is initialized by category")
    print("   ✅ Ingredient references are {id, nombre} objects")
    print("   ✅ Everything persists correctly to JSON files")
    print("   ✅ Data reloads correctly from local files")
    print("=" * 70 + "\n")


def run_all_tests():
    """Run all tests in sequence."""
    print("\n" + "=" * 70)
    print("🚀 DATASOURCE & ADAPTER TEST SUITE")
    print(f"📁 GitHub: {config.GITHUB_OWNER}/{config.GITHUB_REPO}")
    print(f"📂 Data directory: {config.DATA_DIR}")
    print("=" * 70)
    
    tests = [
        test_1_github_client_raw,
        test_2_stable_ids,
        test_3_id_adapter,
        test_4_key_normalization_adapter,
        test_5_stock_initialization_adapter,
        test_6_ingredient_reference_adapter,
        test_7_full_integration_with_persistence,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ TEST FAILED: {test_func.__name__}")
            print(f"   Error: {e}")
            failed += 1
        except Exception as e:
            print(f"\n💥 TEST ERROR: {test_func.__name__}")
            print(f"   Exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 70)
    print("📊 FINAL RESULTS")
    print("=" * 70)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! System is ready for use.")
    
    print("=" * 70 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
