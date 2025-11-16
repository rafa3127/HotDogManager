"""
Temporary testing file for datasource and ID system.

Author: Rafael Correa
Date: November 12, 2025
Updated: November 14, 2025 - Added ID adapter tests and Key Normalization tests
"""

import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from clients.external_sources.external_source_client import ExternalSourceClient
from clients.external_sources.github_client import GitHubClient
from clients.data_source_client import DataSourceClient
from clients.adapters.id_adapter import IDAdapter
from clients.adapters.key_normalization_adapter import (
    KeyNormalizationAdapter,
    normalize_key,
    normalize_keys_recursive
)
from clients.id_processors import (
    generate_stable_id,
    process_grouped_structure_ids,
    process_flat_structure_ids
)
import config


def test_external_source_interface():
    """Test that GitHubClient implements ExternalSourceClient correctly."""
    print("🧪 Test 1: External Source Interface")
    print("=" * 50)
    
    github = GitHubClient(
        owner=config.GITHUB_OWNER,
        repo=config.GITHUB_REPO,
        branch=config.GITHUB_BRANCH
    )
    
    # Verify it's an instance of the abstract class
    assert isinstance(github, ExternalSourceClient), "GitHubClient should inherit from ExternalSourceClient"
    print("✅ GitHubClient correctly implements ExternalSourceClient interface")
    
    # Verify it has the required method
    assert hasattr(github, 'fetch_data'), "GitHubClient should have fetch_data method"
    print("✅ GitHubClient has fetch_data method\n")


def test_github_client():
    """Test the GitHub client by fetching data from the repo (without IDs)."""
    print("🧪 Test 2: GitHub Client Direct Fetch (Raw Data)")
    print("=" * 50)
    
    # Initialize client with config
    client = GitHubClient(
        owner=config.GITHUB_OWNER,
        repo=config.GITHUB_REPO,
        branch=config.GITHUB_BRANCH
    )
    
    # Test fetching ingredientes.json
    print("📥 Fetching ingredientes.json...")
    try:
        ingredientes = client.fetch_data("ingredientes.json")
        print(f"✅ Success! Found {len(ingredientes)} categories")
        print(f"   First category: {ingredientes[0]['Categoria']}")
        print(f"   First item: {ingredientes[0]['Opciones'][0]['nombre']}")
        
        # Verify NO IDs (raw GitHub data)
        first_item = ingredientes[0]['Opciones'][0]
        if 'id' in first_item:
            print(f"   ⚠️  Warning: Data already has IDs (expected raw data without IDs)")
        else:
            print(f"   ✅ Raw data has no IDs (as expected from GitHub)")
        
        # Verify keys are NOT normalized (raw data)
        assert 'Categoria' in ingredientes[0], "Raw data should have 'Categoria' with capital C"
        assert 'Opciones' in ingredientes[0], "Raw data should have 'Opciones' with capital O"
        print(f"   ✅ Raw data has original keys (not normalized)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    
    # Test fetching menu.json
    print("\n📥 Fetching menu.json...")
    try:
        menu = client.fetch_data("menu.json")
        print(f"✅ Success! Found {len(menu)} hot dogs in menu")
        print(f"   First hot dog: {menu[0]['nombre']}\n")
    except Exception as e:
        print(f"❌ Error: {e}")
        raise


def test_stable_id_generation():
    """Test that ID generation is deterministic."""
    print("🧪 Test 3: Stable ID Generation")
    print("=" * 50)
    
    # Test 3.1: Same input produces same ID
    print("\n📋 Test 3.1: Deterministic ID generation")
    print("-" * 50)
    id1 = generate_stable_id("simple", "Pan")
    id2 = generate_stable_id("simple", "Pan")
    assert id1 == id2, "Same inputs should produce same ID"
    print(f"✅ Pan:simple → {id1}")
    print(f"✅ Pan:simple → {id2}")
    print(f"✅ IDs are identical (deterministic)")
    
    # Test 3.2: Different inputs produce different IDs
    print("\n📋 Test 3.2: Different inputs produce different IDs")
    print("-" * 50)
    id_pan_simple = generate_stable_id("simple", "Pan")
    id_salsa_simple = generate_stable_id("simple", "Salsa")
    assert id_pan_simple != id_salsa_simple, "Different categories should produce different IDs"
    print(f"✅ Pan:simple   → {id_pan_simple}")
    print(f"✅ Salsa:simple → {id_salsa_simple}")
    print(f"✅ IDs are different (category matters)")
    
    # Test 3.3: ID format is valid UUID
    print("\n📋 Test 3.3: ID format validation")
    print("-" * 50)
    test_id = generate_stable_id("test", "Test")
    parts = test_id.split('-')
    assert len(parts) == 5, "UUID should have 5 parts separated by hyphens"
    assert len(parts[0]) == 8, "First part should be 8 chars"
    assert len(parts[1]) == 4, "Second part should be 4 chars"
    assert len(parts[2]) == 4, "Third part should be 4 chars"
    assert len(parts[3]) == 4, "Fourth part should be 4 chars"
    assert len(parts[4]) == 12, "Fifth part should be 12 chars"
    print(f"✅ Generated ID: {test_id}")
    print(f"✅ Format is valid UUID (8-4-4-4-12)")


def test_key_normalization():
    """Test key normalization functions."""
    print("\n🧪 Test 4: Key Normalization Functions")
    print("=" * 50)
    
    # Test 4.1: normalize_key function
    print("\n📋 Test 4.1: normalize_key() function")
    print("-" * 50)
    
    test_cases = [
        ('Categoria', 'categoria'),
        ('Categoría', 'categoria'),
        ('Tamaño', 'tamano'),
        ('Año', 'ano'),
        ('Opciones', 'opciones'),
        ('España', 'espana'),
        ('Niño', 'nino'),
        ('NOMBRE', 'nombre'),
        ('simple', 'simple'),  # Already normalized
    ]
    
    for original, expected in test_cases:
        result = normalize_key(original)
        assert result == expected, f"Failed: {original} → {result} != {expected}"
        print(f"   ✅ '{original}' → '{result}'")
    
    print("✅ All normalize_key tests passed")
    
    # Test 4.2: normalize_keys_recursive function
    print("\n📋 Test 4.2: normalize_keys_recursive() function")
    print("-" * 50)
    
    # Simple dict
    data = {'Nombre': 'Juan', 'Año': 2024}
    result = normalize_keys_recursive(data)
    assert result == {'nombre': 'Juan', 'ano': 2024}
    print(f"   ✅ Simple dict: {data} → {result}")
    
    # Nested dict
    data = {
        'Categoría': 'Pan',
        'Opciones': [
            {'Nombre': 'simple', 'Tamaño': 6},
            {'Nombre': 'integral', 'Tamaño': 9}
        ]
    }
    result = normalize_keys_recursive(data)
    assert 'categoria' in result
    assert 'opciones' in result
    assert 'tamano' in result['opciones'][0]
    print(f"   ✅ Nested structure normalized correctly")
    
    # List of dicts
    data = [
        {'Año': 2024, 'España': True},
        {'Año': 2025, 'España': False}
    ]
    result = normalize_keys_recursive(data)
    assert result[0] == {'ano': 2024, 'espana': True}
    assert result[1] == {'ano': 2025, 'espana': False}
    print(f"   ✅ List of dicts normalized correctly")
    
    print("✅ All normalize_keys_recursive tests passed")


def test_key_normalization_adapter():
    """Test KeyNormalizationAdapter standalone."""
    print("\n🧪 Test 5: Key Normalization Adapter (Standalone)")
    print("=" * 50)
    
    # Setup GitHub client
    github = GitHubClient(
        owner=config.GITHUB_OWNER,
        repo=config.GITHUB_REPO,
        branch=config.GITHUB_BRANCH
    )
    
    # Test 5.1: Adapter with ingredientes (GROUPED structure)
    print("\n📋 Test 5.1: Normalize keys in GROUPED structure")
    print("-" * 50)
    try:
        # Wrap GitHub with normalization adapter
        normalized_source = KeyNormalizationAdapter(github)
        ingredientes = normalized_source.fetch_data("ingredientes.json")
        
        print(f"✅ Fetched {len(ingredientes)} categories")
        
        # Verify keys are normalized
        first_group = ingredientes[0]
        assert 'categoria' in first_group, "Should have 'categoria' (normalized)"
        assert 'Categoria' not in first_group, "Should NOT have 'Categoria' (original)"
        assert 'opciones' in first_group, "Should have 'opciones' (normalized)"
        assert 'Opciones' not in first_group, "Should NOT have 'Opciones' (original)"
        
        first_item = first_group['opciones'][0]
        if 'tamaño' in first_item:
            print(f"   ⚠️  Item still has 'tamaño' (source data already has accents removed)")
        if 'tamano' in first_item:
            print(f"   ✅ Item has 'tamano' (normalized)")
        
        print(f"   ✅ Keys normalized: {list(first_group.keys())}")
        print(f"   ✅ Item keys: {list(first_item.keys())}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    
    # Test 5.2: Adapter with menu (FLAT structure)
    print("\n📋 Test 5.2: Normalize keys in FLAT structure")
    print("-" * 50)
    try:
        normalized_source = KeyNormalizationAdapter(github)
        menu = normalized_source.fetch_data("menu.json")
        
        print(f"✅ Fetched {len(menu)} hot dogs")
        
        # Verify keys are normalized
        first_item = menu[0]
        
        # Check that all keys are lowercase
        all_lowercase = all(key.islower() for key in first_item.keys())
        assert all_lowercase, "All keys should be lowercase"
        print(f"   ✅ All keys are lowercase: {list(first_item.keys())}")
        
        # Verify values are preserved (not modified)
        assert first_item['nombre'] is not None, "Values should be preserved"
        print(f"   ✅ Values preserved: nombre={first_item['nombre']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise


def test_id_adapter():
    """Test that IDAdapter adds stable IDs to data."""
    print("\n🧪 Test 6: ID Adapter")
    print("=" * 50)
    
    # Setup GitHub client
    github = GitHubClient(
        owner=config.GITHUB_OWNER,
        repo=config.GITHUB_REPO,
        branch=config.GITHUB_BRANCH
    )
    
    # Test 6.1: Adapter with grouped structure (ingredientes)
    print("\n📋 Test 6.1: ID Adapter with GROUPED structure")
    print("-" * 50)
    try:
        ingredientes_adapter = IDAdapter(github, process_grouped_structure_ids)
        ingredientes = ingredientes_adapter.fetch_data("ingredientes.json")
        
        print(f"✅ Fetched {len(ingredientes)} categories")
        
        # Verify all items have IDs
        id_count = 0
        for group in ingredientes:
            categoria = group['Categoria']
            for item in group['Opciones']:
                assert 'id' in item, f"Item {item['nombre']} in {categoria} should have ID"
                if id_count < 3:  # Only print first 3
                    print(f"   ✅ {categoria}:{item['nombre']} → {item['id']}")
                id_count += 1
        
        print(f"✅ All {id_count} items have IDs")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    
    # Test 6.2: Adapter with flat structure (menu)
    print("\n📋 Test 6.2: ID Adapter with FLAT structure")
    print("-" * 50)
    try:
        menu_adapter = IDAdapter(github, process_flat_structure_ids)
        menu = menu_adapter.fetch_data("menu.json")
        
        print(f"✅ Fetched {len(menu)} hot dogs")
        
        # Verify all items have IDs
        for i, item in enumerate(menu):
            assert 'id' in item, f"Hot dog {item['nombre']} should have ID"
            if i < 3:  # Only print first 3
                print(f"   ✅ {item['nombre']} → {item['id']}")
        
        print(f"✅ All {len(menu)} hot dogs have IDs")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    
    # Test 6.3: IDs are stable across multiple fetches
    print("\n📋 Test 6.3: ID stability across fetches")
    print("-" * 50)
    try:
        adapter = IDAdapter(github, process_grouped_structure_ids)
        data1 = adapter.fetch_data("ingredientes.json")
        data2 = adapter.fetch_data("ingredientes.json")
        
        # Compare first item's ID
        id1 = data1[0]['Opciones'][0]['id']
        id2 = data2[0]['Opciones'][0]['id']
        
        assert id1 == id2, "Same item should have same ID across fetches"
        print(f"✅ First fetch:  {data1[0]['Opciones'][0]['nombre']} → {id1}")
        print(f"✅ Second fetch: {data2[0]['Opciones'][0]['nombre']} → {id2}")
        print(f"✅ IDs are stable across fetches")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise


def test_chained_adapters():
    """Test chaining ID and KeyNormalization adapters."""
    print("\n🧪 Test 7: Chained Adapters (ID + KeyNormalization)")
    print("=" * 50)
    
    # Setup GitHub client
    github = GitHubClient(
        owner=config.GITHUB_OWNER,
        repo=config.GITHUB_REPO,
        branch=config.GITHUB_BRANCH
    )
    
    # Test 7.1: Chain with ingredientes (GROUPED)
    print("\n📋 Test 7.1: ID → KeyNormalization chain (GROUPED)")
    print("-" * 50)
    try:
        # Chain: GitHub → ID → KeyNormalization
        with_ids = IDAdapter(github, process_grouped_structure_ids)
        fully_processed = KeyNormalizationAdapter(with_ids)
        
        ingredientes = fully_processed.fetch_data("ingredientes.json")
        
        print(f"✅ Fetched {len(ingredientes)} categories")
        
        # Verify both IDs and normalized keys
        first_group = ingredientes[0]
        assert 'categoria' in first_group, "Should have normalized key 'categoria'"
        assert 'opciones' in first_group, "Should have normalized key 'opciones'"
        
        first_item = first_group['opciones'][0]
        assert 'id' in first_item, "Should have ID from IDAdapter"
        assert 'nombre' in first_item, "Should have 'nombre' key"
        
        print(f"   ✅ Group keys normalized: {list(first_group.keys())}")
        print(f"   ✅ Item has ID: {first_item['id']}")
        print(f"   ✅ Item keys normalized: {list(first_item.keys())}")
        
        # Verify ID format is still valid
        id_parts = first_item['id'].split('-')
        assert len(id_parts) == 5, "ID should still be valid UUID format"
        print(f"   ✅ ID format preserved: {first_item['id']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    
    # Test 7.2: Chain with menu (FLAT)
    print("\n📋 Test 7.2: ID → KeyNormalization chain (FLAT)")
    print("-" * 50)
    try:
        with_ids = IDAdapter(github, process_flat_structure_ids)
        fully_processed = KeyNormalizationAdapter(with_ids)
        
        menu = fully_processed.fetch_data("menu.json")
        
        print(f"✅ Fetched {len(menu)} hot dogs")
        
        first_item = menu[0]
        assert 'id' in first_item, "Should have ID"
        assert 'nombre' in first_item, "Should have 'nombre'"
        
        # All keys should be lowercase
        all_lowercase = all(key.islower() for key in first_item.keys())
        assert all_lowercase, "All keys should be lowercase"
        
        print(f"   ✅ Item has ID: {first_item['id']}")
        print(f"   ✅ All keys lowercase: {list(first_item.keys())}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    
    # Test 7.3: Verify order doesn't matter for these adapters
    print("\n📋 Test 7.3: Adapter order independence")
    print("-" * 50)
    try:
        # Order 1: ID → KeyNormalization
        chain1 = KeyNormalizationAdapter(
            IDAdapter(github, process_flat_structure_ids)
        )
        result1 = chain1.fetch_data("menu.json")
        
        # Order 2: KeyNormalization → ID (ID processor should still work on normalized keys)
        chain2 = IDAdapter(
            KeyNormalizationAdapter(github),
            process_flat_structure_ids
        )
        result2 = chain2.fetch_data("menu.json")
        
        # Both should have IDs and normalized keys
        assert 'id' in result1[0], "Order 1 should have ID"
        assert 'id' in result2[0], "Order 2 should have ID"
        assert 'nombre' in result1[0], "Order 1 should have normalized keys"
        assert 'nombre' in result2[0], "Order 2 should have normalized keys"
        
        # IDs should be the same (deterministic)
        assert result1[0]['id'] == result2[0]['id'], "Same item should have same ID regardless of adapter order"
        
        print(f"   ✅ Order 1 ID: {result1[0]['id']}")
        print(f"   ✅ Order 2 ID: {result2[0]['id']}")
        print(f"   ✅ Adapters are order-independent for these operations")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise


def test_data_source_client_with_all_adapters():
    """Test the full DataSourceClient with chained adapters."""
    print("\n🧪 Test 8: DataSourceClient Integration (Full Chain)")
    print("=" * 50)
    
    # Setup GitHub client
    github = GitHubClient(
        owner=config.GITHUB_OWNER,
        repo=config.GITHUB_REPO,
        branch=config.GITHUB_BRANCH
    )
    
    # Create fully processed sources with chained adapters
    print("\n📋 Setting up adapter chains...")
    print("-" * 50)
    
    # Ingredientes: GitHub → ID → KeyNormalization
    ingredientes_source = KeyNormalizationAdapter(
        IDAdapter(github, process_grouped_structure_ids)
    )
    print("✅ Ingredientes: GitHub → IDAdapter → KeyNormalizationAdapter")
    
    # Menu: GitHub → ID → KeyNormalization
    menu_source = KeyNormalizationAdapter(
        IDAdapter(github, process_flat_structure_ids)
    )
    print("✅ Menu: GitHub → IDAdapter → KeyNormalizationAdapter")
    
    data_source = DataSourceClient(data_dir=config.DATA_DIR)
    
    # Test 8.1: Initialize with force_external=True
    print("\n📋 Test 8.1: Force external fetch (with full adapter chain)")
    print("-" * 50)
    try:
        data_source.initialize(
            sources={
                'ingredientes': ingredientes_source,
                'menu': menu_source
            },
            force_external=True
        )
        print("✅ Initialization with full adapter chain succeeded")
    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        raise
    
    # Test 8.2: Verify data has IDs and normalized keys
    print("\n📋 Test 8.2: Verify data has IDs AND normalized keys")
    print("-" * 50)
    try:
        ingredientes = data_source.get('ingredientes')
        menu = data_source.get('menu')
        
        # Check ingredientes structure
        first_group = ingredientes[0]
        assert 'categoria' in first_group, "Should have normalized 'categoria'"
        assert 'opciones' in first_group, "Should have normalized 'opciones'"
        assert 'Categoria' not in first_group, "Should NOT have original 'Categoria'"
        
        first_item = first_group['opciones'][0]
        assert 'id' in first_item, "Should have ID"
        assert 'nombre' in first_item, "Should have 'nombre'"
        
        print(f"✅ Ingredientes: {len(ingredientes)} categories")
        print(f"   ✅ Keys normalized: {list(first_group.keys())}")
        print(f"   ✅ Items have IDs: {first_item['id']}")
        
        # Check menu structure
        first_hotdog = menu[0]
        assert 'id' in first_hotdog, "Should have ID"
        all_lowercase = all(key.islower() for key in first_hotdog.keys())
        assert all_lowercase, "All keys should be lowercase"
        
        print(f"✅ Menu: {len(menu)} hot dogs")
        print(f"   ✅ All keys lowercase: {list(first_hotdog.keys())}")
        print(f"   ✅ Has ID: {first_hotdog['id']}")
        
    except Exception as e:
        print(f"❌ Error verifying data: {e}")
        raise
    
    # Test 8.3: Save and reload - both IDs and normalized keys should persist
    print("\n📋 Test 8.3: Save and reload - verify persistence")
    print("-" * 50)
    try:
        # Get first item info
        original_id = ingredientes[0]['opciones'][0]['id']
        original_name = ingredientes[0]['opciones'][0]['nombre']
        
        # Save (both IDs and normalized keys should be saved)
        data_source.save('ingredientes', ingredientes)
        print(f"✅ Saved ingredientes to local file")
        
        # Create new DataSource and load from local
        data_source_2 = DataSourceClient(data_dir=config.DATA_DIR)
        data_source_2.initialize(
            sources={
                'ingredientes': ingredientes_source,
                'menu': menu_source
            },
            force_external=False  # Should load from local
        )
        
        # Verify both ID and keys persisted
        ingredientes_reloaded = data_source_2.get('ingredientes')
        reloaded_group = ingredientes_reloaded[0]
        reloaded_item = reloaded_group['opciones'][0]
        reloaded_id = reloaded_item['id']
        
        assert reloaded_id == original_id, "IDs should persist"
        assert 'categoria' in reloaded_group, "Normalized keys should persist"
        assert 'opciones' in reloaded_group, "Normalized keys should persist"
        
        print(f"✅ Original ID:  {original_id}")
        print(f"✅ Reloaded ID:  {reloaded_id}")
        print(f"✅ Keys still normalized: {list(reloaded_group.keys())}")
        print(f"✅ Both IDs and normalized keys persisted correctly")
        
    except Exception as e:
        print(f"❌ Error testing persistence: {e}")
        raise
    
    # Test 8.4: Force reload from GitHub - everything should remain consistent
    print("\n📋 Test 8.4: Force reload from GitHub - verify consistency")
    print("-" * 50)
    try:
        # Force reload from GitHub
        data_source_3 = DataSourceClient(data_dir=config.DATA_DIR)
        data_source_3.initialize(
            sources={
                'ingredientes': ingredientes_source,
                'menu': menu_source
            },
            force_external=True  # Force download from GitHub
        )
        
        # Verify same ID and normalized keys
        ingredientes_fresh = data_source_3.get('ingredientes')
        fresh_group = ingredientes_fresh[0]
        fresh_item = fresh_group['opciones'][0]
        fresh_id = fresh_item['id']
        
        assert fresh_id == original_id, "IDs should be stable even after GitHub reload"
        assert 'categoria' in fresh_group, "Keys should be normalized after reload"
        assert 'opciones' in fresh_group, "Keys should be normalized after reload"
        
        print(f"✅ Original ID:     {original_id}")
        print(f"✅ After reload ID: {fresh_id}")
        print(f"✅ Keys normalized: {list(fresh_group.keys())}")
        print(f"✅ Full consistency maintained across GitHub reloads")
        
    except Exception as e:
        print(f"❌ Error testing GitHub reload: {e}")
        raise
    
    print("\n" + "=" * 50)
    print("🎉 All DataSourceClient + Full Adapter Chain tests passed!")
    print("=" * 50 + "\n")


def run_all_tests():
    """Run all tests in sequence."""
    print("\n" + "=" * 60)
    print("🚀 Starting Phase 1 Tests (Complete System)")
    print(f"📁 Using GitHub: {config.GITHUB_OWNER}/{config.GITHUB_REPO}")
    print(f"📂 Data directory: {config.DATA_DIR}")
    print("=" * 60 + "\n")
    
    try:
        test_external_source_interface()
        print()
        test_github_client()
        print()
        test_stable_id_generation()
        print()
        test_key_normalization()
        print()
        test_key_normalization_adapter()
        print()
        test_id_adapter()
        print()
        test_chained_adapters()
        print()
        test_data_source_client_with_all_adapters()
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\n📊 Test Summary:")
        print("   ✅ External Source Interface")
        print("   ✅ GitHub Client (Raw Data)")
        print("   ✅ Stable ID Generation")
        print("   ✅ Key Normalization Functions")
        print("   ✅ Key Normalization Adapter")
        print("   ✅ ID Adapter")
        print("   ✅ Chained Adapters")
        print("   ✅ DataSourceClient Integration (Full)")
        print("\n🎉 System ready for Fase 2 development!\n")
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ TESTS FAILED: {e}")
        print("=" * 60 + "\n")
        raise


if __name__ == "__main__":
    run_all_tests()
