"""
Temporary testing file for Phase 1 development.

Author: Rafael Correa
Date: November 12, 2025
"""

from clients.external_sources.external_source_client import ExternalSourceClient
from clients.external_sources.github_client import GitHubClient
from clients.data_source_client import DataSourceClient
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
    """Test the GitHub client by fetching data from the repo."""
    print("🧪 Test 2: GitHub Client Direct Fetch")
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


def test_data_source_client():
    """Test the full DataSourceClient with GitHub as external source."""
    print("🧪 Test 3: DataSourceClient Integration")
    print("=" * 50)
    
    # Setup with config
    github = GitHubClient(
        owner=config.GITHUB_OWNER,
        repo=config.GITHUB_REPO,
        branch=config.GITHUB_BRANCH
    )
    data_source = DataSourceClient(data_dir=config.DATA_DIR)
    
    # Test 3.1: Initialize with force_external=True (ignore local, force download)
    print("\n📋 Test 3.1: Force external fetch")
    print("-" * 50)
    try:
        data_source.initialize(
            sources={
                'ingredientes': github,
                'menu': github
            },
            force_external=True
        )
        print("✅ Initialization with force_external succeeded")
    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        raise
    
    # Test 3.2: Get data from memory
    print("\n📋 Test 3.2: Get data from in-memory store")
    print("-" * 50)
    try:
        ingredientes = data_source.get('ingredientes')
        menu = data_source.get('menu')
        print(f"✅ Retrieved ingredientes: {len(ingredientes)} categories")
        print(f"✅ Retrieved menu: {len(menu)} hot dogs")
    except Exception as e:
        print(f"❌ Error retrieving data: {e}")
        raise
    
    # Test 3.3: Save modified data
    print("\n📋 Test 3.3: Save modified data")
    print("-" * 50)
    try:
        # Modify data
        menu_copy = menu.copy()
        menu_copy.append({"nombre": "test_hotdog", "Pan": "test"})
        
        # Save
        data_source.save('menu', menu_copy)
        print("✅ Saved modified menu data")
    except Exception as e:
        print(f"❌ Error saving data: {e}")
        raise
    
    # Test 3.4: Re-initialize with local fallback (should use local files now)
    print("\n📋 Test 3.4: Re-initialize with local fallback")
    print("-" * 50)
    try:
        data_source_2 = DataSourceClient(data_dir=config.DATA_DIR)
        data_source_2.initialize(
            sources={
                'ingredientes': github,
                'menu': github
            },
            force_external=False  # Should use local files
        )
        
        # Verify we got the modified data
        menu_reloaded = data_source_2.get('menu')
        assert menu_reloaded[-1]['nombre'] == 'test_hotdog', "Should have loaded modified data from local file"
        print("✅ Successfully loaded from local files")
        print(f"✅ Verified modified data persisted (last item: {menu_reloaded[-1]['nombre']})")
    except Exception as e:
        print(f"❌ Error with local fallback: {e}")
        raise
    
    print("\n" + "=" * 50)
    print("🎉 All DataSourceClient tests passed!\n")


def run_all_tests():
    """Run all tests in sequence."""
    print("\n" + "=" * 50)
    print("🚀 Starting Phase 1 Tests")
    print(f"📁 Using GitHub: {config.GITHUB_OWNER}/{config.GITHUB_REPO}")
    print(f"📂 Data directory: {config.DATA_DIR}")
    print("=" * 50 + "\n")
    
    try:
        test_external_source_interface()
        print()
        test_github_client()
        print()
        test_data_source_client()
        
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