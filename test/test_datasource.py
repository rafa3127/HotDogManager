"""
Temporary testing file for datasource and ID system.

Author: Rafael Correa
Date: November 12, 2025
Updated: November 14, 2025 - Added ID adapter tests
"""

import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from clients.external_sources.external_source_client import ExternalSourceClient
from clients.external_sources.github_client import GitHubClient
from clients.data_source_client import DataSourceClient
from clients.adapters.id_adapter import IDAdapter
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


def test_id_adapter():
    """Test that IDAdapter adds stable IDs to data."""
    print("\n🧪 Test 4: ID Adapter")
    print("=" * 50)
    
    # Setup GitHub client
    github = GitHubClient(
        owner=config.GITHUB_OWNER,
        repo=config.GITHUB_REPO,
        branch=config.GITHUB_BRANCH
    )
    
    # Test 4.1: Adapter with grouped structure (ingredientes)
    print("\n📋 Test 4.1: ID Adapter with GROUPED structure")
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
                print(f"   ✅ {categoria}:{item['nombre']} → {item['id']}")
                id_count += 1
        
        print(f"✅ All {id_count} items have IDs")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    
    # Test 4.2: Adapter with flat structure (menu)
    print("\n📋 Test 4.2: ID Adapter with FLAT structure")
    print("-" * 50)
    try:
        menu_adapter = IDAdapter(github, process_flat_structure_ids)
        menu = menu_adapter.fetch_data("menu.json")
        
        print(f"✅ Fetched {len(menu)} hot dogs")
        
        # Verify all items have IDs
        for item in menu:
            assert 'id' in item, f"Hot dog {item['nombre']} should have ID"
            print(f"   ✅ {item['nombre']} → {item['id']}")
        
        print(f"✅ All {len(menu)} hot dogs have IDs")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    
    # Test 4.3: IDs are stable across multiple fetches
    print("\n📋 Test 4.3: ID stability across fetches")
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


def test_data_source_client_with_ids():
    """Test the full DataSourceClient with ID adapters."""
    print("\n🧪 Test 5: DataSourceClient Integration (with IDs)")
    print("=" * 50)
    
    # Setup GitHub client
    github = GitHubClient(
        owner=config.GITHUB_OWNER,
        repo=config.GITHUB_REPO,
        branch=config.GITHUB_BRANCH
    )
    
    # Wrap with ID adapters
    ingredientes_source = IDAdapter(github, process_grouped_structure_ids)
    menu_source = IDAdapter(github, process_flat_structure_ids)
    
    data_source = DataSourceClient(data_dir=config.DATA_DIR)
    
    # Test 5.1: Initialize with force_external=True
    print("\n📋 Test 5.1: Force external fetch (with ID adapters)")
    print("-" * 50)
    try:
        data_source.initialize(
            sources={
                'ingredientes': ingredientes_source,
                'menu': menu_source
            },
            force_external=True
        )
        print("✅ Initialization with ID adapters succeeded")
    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        raise
    
    # Test 5.2: Verify data has IDs
    print("\n📋 Test 5.2: Verify all data has IDs")
    print("-" * 50)
    try:
        ingredientes = data_source.get('ingredientes')
        menu = data_source.get('menu')
        
        # Check ingredientes
        for group in ingredientes:
            for item in group['Opciones']:
                assert 'id' in item, f"Item {item['nombre']} should have ID"
        print(f"✅ All ingredientes have IDs ({len(ingredientes)} categories)")
        
        # Check menu
        for item in menu:
            assert 'id' in item, f"Hot dog {item['nombre']} should have ID"
        print(f"✅ All menu items have IDs ({len(menu)} hot dogs)")
        
    except Exception as e:
        print(f"❌ Error verifying IDs: {e}")
        raise
    
    # Test 5.3: Save and reload - IDs should persist
    print("\n📋 Test 5.3: Save and reload - verify ID persistence")
    print("-" * 50)
    try:
        # Get first item's ID
        original_id = ingredientes[0]['Opciones'][0]['id']
        original_name = ingredientes[0]['Opciones'][0]['nombre']
        
        # Save (IDs should be saved to local file)
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
        
        # Verify ID persisted
        ingredientes_reloaded = data_source_2.get('ingredientes')
        reloaded_id = ingredientes_reloaded[0]['Opciones'][0]['id']
        
        assert reloaded_id == original_id, "IDs should persist across save/load"
        print(f"✅ Original:  {original_name} → {original_id}")
        print(f"✅ Reloaded:  {original_name} → {reloaded_id}")
        print(f"✅ IDs persisted correctly")
        
    except Exception as e:
        print(f"❌ Error testing persistence: {e}")
        raise
    
    # Test 5.4: Force reload from GitHub - IDs should remain stable
    print("\n📋 Test 5.4: Force reload from GitHub - verify ID stability")
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
        
        # Verify same ID for same item
        ingredientes_fresh = data_source_3.get('ingredientes')
        fresh_id = ingredientes_fresh[0]['Opciones'][0]['id']
        
        assert fresh_id == original_id, "Same item should have same ID even after reload from GitHub"
        print(f"✅ Original ID:     {original_id}")
        print(f"✅ After reload ID: {fresh_id}")
        print(f"✅ IDs are stable across GitHub reloads (deterministic generation)")
        
    except Exception as e:
        print(f"❌ Error testing GitHub reload: {e}")
        raise
    
    print("\n" + "=" * 50)
    print("🎉 All DataSourceClient + ID tests passed!\n")


def run_all_tests():
    """Run all tests in sequence."""
    print("\n" + "=" * 50)
    print("🚀 Starting Phase 1 Tests (with ID System)")
    print(f"📁 Using GitHub: {config.GITHUB_OWNER}/{config.GITHUB_REPO}")
    print(f"📂 Data directory: {config.DATA_DIR}")
    print("=" * 50 + "\n")
    
    try:
        test_external_source_interface()
        print()
        test_github_client()
        print()
        test_stable_id_generation()
        print()
        test_id_adapter()
        print()
        test_data_source_client_with_ids()
        
        print("=" * 50)
        print("✅ ALL TESTS PASSED!")
        print("=" * 50 + "\n")
        
    except Exception as e:
        print("\n" + "=" * 50)
        print(f"❌ TESTS FAILED: {e}")
        print("=" * 50 + "\n")
        raise


if __name__ == "__main__":
    run_all_tests()
