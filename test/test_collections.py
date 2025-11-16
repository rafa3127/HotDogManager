"""
Test suite for Collections and DataHandler.

This module tests the complete collection system including:
- BaseCollection abstract functionality
- IngredientCollection with GROUPED structure
- HotDogCollection with FLAT structure
- DataHandler with Unit of Work pattern

Tests use real DataSourceClient (not mocks) for integration testing.

Author: Rafael Correa
Date: November 15, 2025
"""

import sys
import os
import tempfile
import shutil

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from clients.external_sources.github_client import GitHubClient
from clients.data_source_client import DataSourceClient
from clients.adapters.id_adapter import IDAdapter
from clients.adapters.key_normalization_adapter import KeyNormalizationAdapter
from clients.id_processors import (
    generate_stable_id,
    process_grouped_structure_ids,
    process_flat_structure_ids
)
from models.collections import IngredientCollection, HotDogCollection
from handlers.data_handler import DataHandler
import config


# ────────────────────────────────────────────────────────────
# Test Setup Utilities
# ────────────────────────────────────────────────────────────

def create_test_data_source():
    """
    Create a DataSourceClient with real GitHub data for testing.
    
    Uses a temporary directory to avoid polluting the main data/ folder.
    
    Returns:
        DataSourceClient instance ready for testing
    """
    print("🔧 Setting up test data source...")
    
    # Create temporary directory for test data
    temp_dir = tempfile.mkdtemp(prefix='hotdog_test_')
    print(f"   📁 Temp directory: {temp_dir}")
    
    # Setup GitHub client
    github = GitHubClient(
        owner=config.GITHUB_OWNER,
        repo=config.GITHUB_REPO,
        branch=config.GITHUB_BRANCH
    )
    
    # Setup adapters for ingredientes (GROUPED structure)
    ingredientes_with_ids = IDAdapter(github, process_grouped_structure_ids)
    ingredientes_processed = KeyNormalizationAdapter(ingredientes_with_ids)
    
    # Setup adapters for menu (FLAT structure)
    menu_with_ids = IDAdapter(github, process_flat_structure_ids)
    menu_processed = KeyNormalizationAdapter(menu_with_ids)
    
    # Initialize data source
    data_source = DataSourceClient(data_dir=temp_dir)
    data_source.initialize({
        'ingredientes': ingredientes_processed,
        'menu': menu_processed
    }, force_external=True)  # Force download from GitHub
    
    print("   ✅ Data source ready\n")
    return data_source, temp_dir


def cleanup_test_data(temp_dir):
    """Clean up temporary test directory."""
    print(f"\n🧹 Cleaning up temp directory: {temp_dir}")
    shutil.rmtree(temp_dir)
    print("   ✅ Cleanup complete")


# ────────────────────────────────────────────────────────────
# Test 1: IngredientCollection - Load and Read
# ────────────────────────────────────────────────────────────

def test_ingredient_collection_load():
    """Test that IngredientCollection loads data correctly from GROUPED structure."""
    print("🧪 Test 1: IngredientCollection - Load and Read")
    print("=" * 60)
    
    data_source, temp_dir = create_test_data_source()
    
    try:
        # Initialize collection
        print("📦 Initializing IngredientCollection...")
        collection = IngredientCollection(data_source)
        
        # Test basic loading
        assert len(collection) > 0, "Collection should have items"
        print(f"   ✅ Loaded {len(collection)} ingredients")
        
        # Test categories
        categories = collection.get_categories()
        print(f"   ✅ Found categories: {categories}")
        assert 'Pan' in categories, "Should have Pan category"
        assert 'Salchicha' in categories, "Should have Salchicha category"
        
        # Test get_by_category
        panes = collection.get_by_category('Pan')
        print(f"   ✅ Found {len(panes)} panes")
        assert len(panes) > 0, "Should have at least one pan"
        
        # Test get_by_name
        pan_simple = collection.get_by_name('simple', 'Pan')
        assert pan_simple is not None, "Should find 'simple' pan"
        print(f"   ✅ Found pan 'simple': {pan_simple.tipo}")
        
        # Test entity validation
        pan_simple.validate()
        print(f"   ✅ Pan validation passed")
        
        # Test stats
        stats = collection.get_category_stats()
        print(f"   ✅ Category stats: {stats}")
        
        # Verify not dirty (just loaded)
        assert not collection.is_dirty, "Collection should not be dirty after load"
        print(f"   ✅ Collection not dirty after load\n")
        
    finally:
        cleanup_test_data(temp_dir)


# ────────────────────────────────────────────────────────────
# Test 2: IngredientCollection - CRUD Operations
# ────────────────────────────────────────────────────────────

def test_ingredient_collection_crud():
    """Test CRUD operations on IngredientCollection."""
    print("🧪 Test 2: IngredientCollection - CRUD Operations")
    print("=" * 60)
    
    data_source, temp_dir = create_test_data_source()
    
    try:
        collection = IngredientCollection(data_source)
        initial_count = len(collection)
        print(f"📊 Initial count: {initial_count}")
        
        # ── CREATE ──
        print("\n➕ Testing CREATE...")
        nuevo_pan = collection._entity_classes['Pan'](
            id=generate_stable_id('test pan deluxe', 'Pan'),
            entity_type='Pan',
            nombre='test pan deluxe',
            tipo='artesanal',
            tamano=8,
            unidad='pulgadas'
        )
        
        collection.add(nuevo_pan)
        assert len(collection) == initial_count + 1, "Should have one more item"
        assert collection.is_dirty, "Collection should be dirty after add"
        print(f"   ✅ Added pan, count: {len(collection)}, dirty: {collection.is_dirty}")
        
        # ── READ ──
        print("\n🔍 Testing READ...")
        found = collection.get(nuevo_pan.id)
        assert found is not None, "Should find newly added pan"
        assert found.nombre == 'test pan deluxe', "Should have correct name"
        print(f"   ✅ Found pan by ID: {found.nombre}")
        
        found_by_name = collection.get_by_name('test pan deluxe', 'Pan')
        assert found_by_name is not None, "Should find by name"
        print(f"   ✅ Found pan by name")
        
        # ── UPDATE ──
        print("\n✏️  Testing UPDATE...")
        nuevo_pan.tipo = 'masa madre'
        collection.update(nuevo_pan)
        assert collection.is_dirty, "Collection should be dirty after update"
        
        updated = collection.get(nuevo_pan.id)
        assert updated.tipo == 'masa madre', "Should have updated tipo"
        print(f"   ✅ Updated pan tipo to: {updated.tipo}")
        
        # ── FLUSH ──
        print("\n💾 Testing FLUSH...")
        collection.flush()
        assert not collection.is_dirty, "Collection should not be dirty after flush"
        print(f"   ✅ Flushed changes, dirty: {collection.is_dirty}")
        
        # Verify persistence - reload and check
        print("\n🔄 Testing PERSISTENCE (reload)...")
        collection.reload()
        persisted = collection.get_by_name('test pan deluxe', 'Pan')
        assert persisted is not None, "Should find after reload"
        assert persisted.tipo == 'masa madre', "Should have persisted changes"
        print(f"   ✅ Data persisted correctly after reload")
        
        # ── DELETE ──
        print("\n🗑️  Testing DELETE...")
        collection.delete(nuevo_pan.id)
        assert len(collection) == initial_count, "Should be back to initial count"
        assert collection.is_dirty, "Collection should be dirty after delete"
        print(f"   ✅ Deleted pan, count: {len(collection)}, dirty: {collection.is_dirty}")
        
        deleted = collection.get(nuevo_pan.id)
        assert deleted is None, "Should not find deleted item"
        print(f"   ✅ Item no longer in collection")
        
        # Flush delete
        collection.flush()
        print(f"   ✅ Delete flushed\n")
        
    finally:
        cleanup_test_data(temp_dir)


# ────────────────────────────────────────────────────────────
# Test 3: IngredientCollection - Validation
# ────────────────────────────────────────────────────────────

def test_ingredient_collection_validation():
    """Test validation methods in IngredientCollection."""
    print("🧪 Test 3: IngredientCollection - Validation")
    print("=" * 60)
    
    data_source, temp_dir = create_test_data_source()
    
    try:
        collection = IngredientCollection(data_source)
        
        # Test exists_in_category
        print("🔍 Testing exists_in_category...")
        assert collection.exists_in_category('simple', 'Pan'), "Should find existing pan"
        assert not collection.exists_in_category('fake pan', 'Pan'), "Should not find fake pan"
        print("   ✅ exists_in_category works correctly")
        
        # Test validate_unique_name (should pass for new name)
        print("\n✅ Testing validate_unique_name (new name)...")
        try:
            collection.validate_unique_name('nuevo pan único', 'Pan')
            print("   ✅ Validation passed for new name")
        except ValueError:
            assert False, "Should not raise error for new name"
        
        # Test validate_unique_name (should fail for existing name)
        print("\n❌ Testing validate_unique_name (duplicate name)...")
        try:
            collection.validate_unique_name('simple', 'Pan')
            assert False, "Should raise error for duplicate name"
        except ValueError as e:
            print(f"   ✅ Correctly raised error: {e}")
        
        # Test validate_unique_name with exclude_id (for updates)
        print("\n🔄 Testing validate_unique_name with exclude_id...")
        pan_simple = collection.get_by_name('simple', 'Pan')
        try:
            collection.validate_unique_name('simple', 'Pan', exclude_id=pan_simple.id)
            print("   ✅ Validation passed when excluding same ID (update scenario)")
        except ValueError:
            assert False, "Should not raise error when excluding same ID"
        
        print()
        
    finally:
        cleanup_test_data(temp_dir)


# ────────────────────────────────────────────────────────────
# Test 4: HotDogCollection - Load and Read
# ────────────────────────────────────────────────────────────

def test_hotdog_collection_load():
    """Test that HotDogCollection loads data correctly from FLAT structure."""
    print("🧪 Test 4: HotDogCollection - Load and Read")
    print("=" * 60)
    
    data_source, temp_dir = create_test_data_source()
    
    try:
        print("📦 Initializing HotDogCollection...")
        collection = HotDogCollection(data_source)
        
        # Test basic loading
        assert len(collection) > 0, "Collection should have items"
        print(f"   ✅ Loaded {len(collection)} hot dogs")
        
        # Test get_by_name
        simple = collection.get_by_name('simple')
        assert simple is not None, "Should find 'simple' hot dog"
        print(f"   ✅ Found hot dog 'simple'")
        print(f"      Pan: {simple.pan}, Salchicha: {simple.salchicha}")
        
        # Test entity validation
        simple.validate()
        print(f"   ✅ HotDog validation passed")
        
        # Test combos
        combos = collection.get_combos()
        print(f"   ✅ Found {len(combos)} combos")
        
        # Test simples
        simples = collection.get_simple_hotdogs()
        print(f"   ✅ Found {len(simples)} simple hot dogs")
        
        # Test stats
        stats = collection.get_stats()
        print(f"   ✅ Stats: {stats}")
        
        # Verify not dirty
        assert not collection.is_dirty, "Collection should not be dirty after load"
        print(f"   ✅ Collection not dirty after load\n")
        
    finally:
        cleanup_test_data(temp_dir)


# ────────────────────────────────────────────────────────────
# Test 5: HotDogCollection - CRUD Operations
# ────────────────────────────────────────────────────────────

def test_hotdog_collection_crud():
    """Test CRUD operations on HotDogCollection."""
    print("🧪 Test 5: HotDogCollection - CRUD Operations")
    print("=" * 60)
    
    data_source, temp_dir = create_test_data_source()
    
    try:
        collection = HotDogCollection(data_source)
        initial_count = len(collection)
        print(f"📊 Initial count: {initial_count}")
        
        # ── CREATE ──
        print("\n➕ Testing CREATE...")
        nuevo_hotdog = collection._hotdog_class(
            id=generate_stable_id('test hotdog deluxe'),
            entity_type='HotDog',
            nombre='test hotdog deluxe',
            pan='simple',
            salchicha='weiner',
            toppings=['cebolla'],
            salsas=['mostaza'],
            acompanante='Papas'
        )
        
        collection.add(nuevo_hotdog)
        assert len(collection) == initial_count + 1, "Should have one more item"
        assert collection.is_dirty, "Collection should be dirty after add"
        print(f"   ✅ Added hotdog, count: {len(collection)}")
        
        # ── READ ──
        print("\n🔍 Testing READ...")
        found = collection.get_by_name('test hotdog deluxe')
        assert found is not None, "Should find newly added hotdog"
        print(f"   ✅ Found hotdog: {found.nombre}")
        
        # Test searching by ingredient
        con_cebolla = collection.get_with_topping('cebolla')
        assert any(hd.nombre == 'test hotdog deluxe' for hd in con_cebolla), "Should find in topping search"
        print(f"   ✅ Found in topping search ({len(con_cebolla)} with cebolla)")
        
        # ── UPDATE ──
        print("\n✏️  Testing UPDATE...")
        nuevo_hotdog.toppings.append('queso')
        collection.update(nuevo_hotdog)
        assert collection.is_dirty, "Collection should be dirty after update"
        
        updated = collection.get(nuevo_hotdog.id)
        assert 'queso' in updated.toppings, "Should have updated toppings"
        print(f"   ✅ Updated toppings: {updated.toppings}")
        
        # ── FLUSH & PERSIST ──
        print("\n💾 Testing FLUSH and PERSISTENCE...")
        collection.flush()
        collection.reload()
        
        persisted = collection.get_by_name('test hotdog deluxe')
        assert persisted is not None, "Should persist after reload"
        assert 'queso' in persisted.toppings, "Should have persisted changes"
        print(f"   ✅ Changes persisted correctly")
        
        # ── DELETE ──
        print("\n🗑️  Testing DELETE...")
        collection.delete(nuevo_hotdog.id)
        assert len(collection) == initial_count, "Should be back to initial count"
        collection.flush()
        print(f"   ✅ Deleted and flushed\n")
        
    finally:
        cleanup_test_data(temp_dir)


# ────────────────────────────────────────────────────────────
# Test 6: HotDogCollection - Validation
# ────────────────────────────────────────────────────────────

def test_hotdog_collection_validation():
    """Test validation methods in HotDogCollection."""
    print("🧪 Test 6: HotDogCollection - Validation")
    print("=" * 60)
    
    data_source, temp_dir = create_test_data_source()
    
    try:
        ingredientes = IngredientCollection(data_source)
        menu = HotDogCollection(data_source)
        
        # Test validate_unique_name
        print("✅ Testing validate_unique_name (new name)...")
        try:
            menu.validate_unique_name('nuevo hotdog único')
            print("   ✅ Validation passed for new name")
        except ValueError:
            assert False, "Should not raise error for new name"
        
        print("\n❌ Testing validate_unique_name (duplicate)...")
        try:
            menu.validate_unique_name('simple')
            assert False, "Should raise error for duplicate name"
        except ValueError as e:
            print(f"   ✅ Correctly raised error: {e}")
        
        # Test validate_ingredients_exist (valid ingredients)
        print("\n✅ Testing validate_ingredients_exist (valid)...")
        try:
            menu.validate_ingredients_exist(
                pan='simple',
                salchicha='weiner',
                toppings=[],
                salsas=[],
                acompanante=None,
                ingredient_collection=ingredientes
            )
            print("   ✅ Validation passed for valid ingredients")
        except ValueError:
            assert False, "Should not raise error for valid ingredients"
        
        # Test validate_ingredients_exist (invalid pan)
        print("\n❌ Testing validate_ingredients_exist (invalid pan)...")
        try:
            menu.validate_ingredients_exist(
                pan='fake pan',
                salchicha='weiner',
                toppings=[],
                salsas=[],
                acompanante=None,
                ingredient_collection=ingredientes
            )
            assert False, "Should raise error for invalid pan"
        except ValueError as e:
            print(f"   ✅ Correctly raised error: {e}")
        
        print()
        
    finally:
        cleanup_test_data(temp_dir)


# ────────────────────────────────────────────────────────────
# Test 7: DataHandler - Unit of Work
# ────────────────────────────────────────────────────────────

def test_data_handler_unit_of_work():
    """Test DataHandler's Unit of Work pattern (commit/rollback)."""
    print("🧪 Test 7: DataHandler - Unit of Work")
    print("=" * 60)
    
    data_source, temp_dir = create_test_data_source()
    
    try:
        handler = DataHandler(data_source)
        
        print("📊 Initial state:")
        print(f"   Ingredientes: {len(handler.ingredientes)}")
        print(f"   Menu: {len(handler.menu)}")
        print(f"   Has changes: {handler.has_changes}")
        
        # Make changes
        print("\n➕ Making changes...")
        nuevo_pan = handler.ingredientes._entity_classes['Pan'](
            id=generate_stable_id('test pan uow', 'Pan'),
            entity_type='Pan',
            nombre='test pan uow',
            tipo='test',
            tamano=6,
            unidad='pulgadas'
        )
        handler.ingredientes.add(nuevo_pan)
        
        nuevo_hotdog = handler.menu._hotdog_class(
            id=generate_stable_id('test hotdog uow'),
            entity_type='HotDog',
            nombre='test hotdog uow',
            pan='simple',
            salchicha='weiner',
            toppings=[],
            salsas=[],
            acompanante=None
        )
        handler.menu.add(nuevo_hotdog)
        
        assert handler.has_changes, "Should have changes"
        print(f"   ✅ Changes made, has_changes: {handler.has_changes}")
        
        # Test COMMIT
        print("\n💾 Testing COMMIT...")
        handler.commit()
        assert not handler.has_changes, "Should not have changes after commit"
        print(f"   ✅ Committed, has_changes: {handler.has_changes}")
        
        # Verify persistence
        print("\n🔄 Verifying persistence (create new handler)...")
        handler2 = DataHandler(data_source)
        found_pan = handler2.ingredientes.get_by_name('test pan uow', 'Pan')
        found_hotdog = handler2.menu.get_by_name('test hotdog uow')
        assert found_pan is not None, "Should find pan after commit"
        assert found_hotdog is not None, "Should find hotdog after commit"
        print(f"   ✅ Data persisted correctly")
        
        # Test ROLLBACK
        print("\n↩️  Testing ROLLBACK...")
        handler.ingredientes.delete(nuevo_pan.id)
        handler.menu.delete(nuevo_hotdog.id)
        assert handler.has_changes, "Should have changes"
        
        handler.rollback()
        assert not handler.has_changes, "Should not have changes after rollback"
        
        # Verify rollback worked
        rolled_back_pan = handler.ingredientes.get(nuevo_pan.id)
        rolled_back_hotdog = handler.menu.get(nuevo_hotdog.id)
        assert rolled_back_pan is not None, "Should restore pan after rollback"
        assert rolled_back_hotdog is not None, "Should restore hotdog after rollback"
        print(f"   ✅ Rollback restored data correctly")
        
        # Cleanup
        handler.ingredientes.delete(nuevo_pan.id)
        handler.menu.delete(nuevo_hotdog.id)
        handler.commit()
        print(f"   ✅ Cleanup complete\n")
        
    finally:
        cleanup_test_data(temp_dir)


# ────────────────────────────────────────────────────────────
# Test 8: DataHandler - Convenience Methods
# ────────────────────────────────────────────────────────────

def test_data_handler_convenience():
    """Test DataHandler's convenience methods."""
    print("🧪 Test 8: DataHandler - Convenience Methods")
    print("=" * 60)
    
    data_source, temp_dir = create_test_data_source()
    
    try:
        handler = DataHandler(data_source)
        
        # Test ingredient shortcuts
        print("🔍 Testing ingredient shortcuts...")
        pan = handler.get_ingredient_by_name('simple', 'Pan')
        assert pan is not None, "Should find pan via shortcut"
        print(f"   ✅ get_ingredient_by_name: {pan.nombre}")
        
        panes = handler.get_ingredients_by_category('Pan')
        assert len(panes) > 0, "Should find panes via shortcut"
        print(f"   ✅ get_ingredients_by_category: {len(panes)} panes")
        
        # Test hotdog shortcuts
        print("\n🌭 Testing hotdog shortcuts...")
        hotdog = handler.get_hotdog_by_name('simple')
        assert hotdog is not None, "Should find hotdog via shortcut"
        print(f"   ✅ get_hotdog_by_name: {hotdog.nombre}")
        
        # Test validation shortcut
        print("\n✅ Testing validation shortcut...")
        try:
            handler.validate_hotdog_ingredients(
                pan='simple',
                salchicha='weiner',
                toppings=[],
                salsas=[],
                acompanante=None
            )
            print(f"   ✅ validate_hotdog_ingredients passed")
        except ValueError:
            assert False, "Should not raise error for valid ingredients"
        
        # Test summary
        print("\n📊 Testing summary methods...")
        summary = handler.get_summary()
        assert 'ingredientes' in summary, "Summary should have ingredientes"
        assert 'menu' in summary, "Summary should have menu"
        print(f"   ✅ get_summary returned data")
        
        print("\n📋 Testing print_summary...")
        handler.print_summary()
        print(f"   ✅ print_summary executed\n")
        
    finally:
        cleanup_test_data(temp_dir)


# ────────────────────────────────────────────────────────────
# Test 9: DataHandler - Context Manager
# ────────────────────────────────────────────────────────────

def test_data_handler_context_manager():
    """Test DataHandler as context manager (auto-commit/rollback)."""
    print("🧪 Test 9: DataHandler - Context Manager")
    print("=" * 60)
    
    data_source, temp_dir = create_test_data_source()
    
    try:
        # Test auto-commit on success
        print("✅ Testing auto-commit on success...")
        with DataHandler(data_source) as handler:
            nuevo_pan = handler.ingredientes._entity_classes['Pan'](
                id=generate_stable_id('test pan ctx', 'Pan'),
                entity_type='Pan',
                nombre='test pan ctx',
                tipo='test',
                tamano=6,
                unidad='pulgadas'
            )
            handler.ingredientes.add(nuevo_pan)
            # Should auto-commit on exit
        
        # Verify it was committed
        handler2 = DataHandler(data_source)
        found = handler2.ingredientes.get_by_name('test pan ctx', 'Pan')
        assert found is not None, "Should auto-commit on success"
        print(f"   ✅ Auto-committed on successful exit")
        
        # Test auto-rollback on exception
        print("\n❌ Testing auto-rollback on exception...")
        try:
            with DataHandler(data_source) as handler:
                nuevo_pan2 = handler.ingredientes._entity_classes['Pan'](
                    id=generate_stable_id('test pan ctx fail', 'Pan'),
                    entity_type='Pan',
                    nombre='test pan ctx fail',
                    tipo='test',
                    tamano=6,
                    unidad='pulgadas'
                )
                handler.ingredientes.add(nuevo_pan2)
                raise Exception("Simulated error")
        except Exception:
            pass
        
        # Verify it was rolled back
        handler3 = DataHandler(data_source)
        found_fail = handler3.ingredientes.get_by_name('test pan ctx fail', 'Pan')
        assert found_fail is None, "Should auto-rollback on exception"
        print(f"   ✅ Auto-rolled back on exception")
        
        # Cleanup
        handler3.ingredientes.delete_where(nombre='test pan ctx')
        handler3.commit()
        print(f"   ✅ Cleanup complete\n")
        
    finally:
        cleanup_test_data(temp_dir)


# ────────────────────────────────────────────────────────────
# Main Test Runner
# ────────────────────────────────────────────────────────────

def run_all_tests():
    """Run all collection tests."""
    print("\n" + "="*60)
    print("🧪 COLLECTION & DATAHANDLER TEST SUITE")
    print("="*60 + "\n")
    
    tests = [
        test_ingredient_collection_load,
        test_ingredient_collection_crud,
        test_ingredient_collection_validation,
        test_hotdog_collection_load,
        test_hotdog_collection_crud,
        test_hotdog_collection_validation,
        test_data_handler_unit_of_work,
        test_data_handler_convenience,
        test_data_handler_context_manager,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"\n❌ Test failed: {test.__name__}")
            print(f"   Error: {e}\n")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("📊 TEST RESULTS")
    print("="*60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Total:  {len(tests)}")
    print("="*60 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
