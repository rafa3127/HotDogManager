"""
Test suite for IngredientService.

Tests all ingredient management operations using real DataSource with temporary files.

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
from clients.adapters.id_adapter import IDAdapter
from clients.adapters.key_normalization_adapter import KeyNormalizationAdapter
from clients.data_source_client import DataSourceClient
from clients.id_processors import process_grouped_structure_ids, process_flat_structure_ids
from handlers.data_handler import DataHandler
from services.ingredient_service import IngredientService
import config


def setup_test_handler():
    """
    Setup a DataHandler with real GitHub data in a temporary directory.
    
    Returns:
        tuple: (handler, temp_dir) - DataHandler instance and temp directory path
    """
    # Create temporary directory for test data
    temp_dir = tempfile.mkdtemp(prefix='hotdog_test_')
    
    # Setup GitHub client with adapters (same as production)
    github = GitHubClient(
        owner=config.GITHUB_OWNER,
        repo=config.GITHUB_REPO,
        branch=config.GITHUB_BRANCH
    )
    
    # Ingredientes: GROUPED structure
    ingredientes_with_ids = IDAdapter(github, process_grouped_structure_ids)
    ingredientes_processed = KeyNormalizationAdapter(ingredientes_with_ids)
    
    # Menu: FLAT structure
    menu_with_ids = IDAdapter(github, process_flat_structure_ids)
    menu_processed = KeyNormalizationAdapter(menu_with_ids)
    
    # Initialize DataSource with temporary directory
    data_source = DataSourceClient(data_dir=temp_dir)
    data_source.initialize({
        'ingredientes': ingredientes_processed,
        'menu': menu_processed
    }, force_external=True)
    
    # Create DataHandler
    handler = DataHandler(data_source)
    
    return handler, temp_dir


def teardown_test_handler(temp_dir):
    """Clean up temporary directory."""
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        print(f"🧹 Cleaned up temporary directory: {temp_dir}")


def test_list_by_category():
    """Test 1: List ingredients by category."""
    print("\n" + "=" * 70)
    print("🧪 Test 1: IngredientService.list_by_category()")
    print("=" * 70)
    
    handler, temp_dir = setup_test_handler()
    
    try:
        # Test with 'Pan' category
        panes = IngredientService.list_by_category(handler, 'Pan')
        print(f"\n📋 Found {len(panes)} panes in catalog")
        
        assert len(panes) > 0, "Should have at least one pan"
        
        # Display first few
        for i, pan in enumerate(panes[:3], 1):
            print(f"   {i}. {pan.nombre} - {pan.tipo} ({pan.tamano} {pan.unidad})")
        
        # Test with 'Salchicha' category
        salchichas = IngredientService.list_by_category(handler, 'Salchicha')
        print(f"\n📋 Found {len(salchichas)} salchichas in catalog")
        
        assert len(salchichas) > 0, "Should have at least one salchicha"
        
        # Test with invalid category
        invalid = IngredientService.list_by_category(handler, 'InvalidCategory')
        assert len(invalid) == 0, "Invalid category should return empty list"
        
        print("\n✅ Test 1 PASSED: list_by_category works correctly")
        
    finally:
        teardown_test_handler(temp_dir)


def test_list_by_type():
    """Test 2: List ingredients by category and type."""
    print("\n" + "=" * 70)
    print("🧪 Test 2: IngredientService.list_by_type()")
    print("=" * 70)
    
    handler, temp_dir = setup_test_handler()
    
    try:
        # Get all panes first
        all_panes = IngredientService.list_by_category(handler, 'Pan')
        print(f"\n📋 Total panes: {len(all_panes)}")
        
        # Get unique types
        tipos = set(pan.tipo for pan in all_panes if hasattr(pan, 'tipo'))
        print(f"📋 Tipos disponibles: {tipos}")
        
        # Test filtering by specific type
        if tipos:
            test_tipo = list(tipos)[0]
            filtered = IngredientService.list_by_type(handler, 'Pan', test_tipo)
            print(f"\n🔍 Panes tipo '{test_tipo}': {len(filtered)}")
            
            # Verify all returned items have the correct type
            for pan in filtered:
                assert pan.tipo == test_tipo, f"Pan should have tipo={test_tipo}"
            
            # Verify count matches
            expected = sum(1 for p in all_panes if hasattr(p, 'tipo') and p.tipo == test_tipo)
            assert len(filtered) == expected, "Filtered count should match"
            
            print(f"✅ All {len(filtered)} items have tipo='{test_tipo}'")
        
        # Test with non-existent type
        empty = IngredientService.list_by_type(handler, 'Pan', 'tipo_inexistente')
        assert len(empty) == 0, "Non-existent type should return empty list"
        
        print("\n✅ Test 2 PASSED: list_by_type works correctly")
        
    finally:
        teardown_test_handler(temp_dir)


def test_add_ingredient():
    """Test 3: Add new ingredient."""
    print("\n" + "=" * 70)
    print("🧪 Test 3: IngredientService.add_ingredient()")
    print("=" * 70)
    
    handler, temp_dir = setup_test_handler()
    
    try:
        # Get initial count
        initial_panes = len(handler.ingredientes.get_by_category('Pan'))
        print(f"\n📊 Initial panes count: {initial_panes}")
        
        # Add new ingredient
        result = IngredientService.add_ingredient(
            handler,
            categoria='Pan',
            nombre='test_pan_nuevo',
            tipo='test',
            tamano=10,
            unidad='pulgadas'
        )
        
        print(f"\n➕ Add result: {result['exito']}")
        
        assert result['exito'] == True, "Should successfully add ingredient"
        assert 'ingrediente' in result, "Should return created ingredient"
        
        nuevo_pan = result['ingrediente']
        print(f"   Created: {nuevo_pan.nombre} ({nuevo_pan.tipo}, {nuevo_pan.tamano} {nuevo_pan.unidad})")
        
        # Verify it's in the collection
        final_panes = len(handler.ingredientes.get_by_category('Pan'))
        assert final_panes == initial_panes + 1, "Should have one more pan"
        print(f"📊 Final panes count: {final_panes}")
        
        # Verify we can retrieve it
        retrieved = handler.ingredientes.get_by_name('test_pan_nuevo', 'Pan')
        assert retrieved is not None, "Should be able to retrieve new ingredient"
        assert retrieved.nombre == 'test_pan_nuevo', "Name should match"
        
        # Test duplicate name (should fail)
        duplicate_result = IngredientService.add_ingredient(
            handler,
            categoria='Pan',
            nombre='test_pan_nuevo',
            tipo='otro',
            tamano=8,
            unidad='pulgadas'
        )
        
        print(f"\n🔒 Duplicate attempt: {duplicate_result['exito']}")
        assert duplicate_result['exito'] == False, "Duplicate name should fail"
        assert 'error' in duplicate_result, "Should return error message"
        print(f"   Error: {duplicate_result['error']}")
        
        # Test invalid category
        invalid_result = IngredientService.add_ingredient(
            handler,
            categoria='InvalidCategory',
            nombre='test',
            tipo='test'
        )
        
        assert invalid_result['exito'] == False, "Invalid category should fail"
        print(f"\n🔒 Invalid category: {invalid_result['error']}")
        
        # Test validation (missing required field for Pan)
        # Pan requires: tipo, tamano, unidad
        invalid_result = IngredientService.add_ingredient(
            handler,
            categoria='Pan',
            nombre='pan_sin_tamano',
            tipo='test'
            # Missing tamano and unidad - validation should fail
        )
        
        print(f"\n🔒 Missing required fields: {invalid_result['exito']}")
        if not invalid_result['exito']:
            print(f"   Error: {invalid_result['error']}")
        
        print("\n✅ Test 3 PASSED: add_ingredient works correctly")
        
    finally:
        teardown_test_handler(temp_dir)


def test_delete_ingredient_simple():
    """Test 4: Delete ingredient (not used in menu)."""
    print("\n" + "=" * 70)
    print("🧪 Test 4: IngredientService.delete_ingredient() - Simple case")
    print("=" * 70)
    
    handler, temp_dir = setup_test_handler()
    
    try:
        # Add a test ingredient that won't be used
        # Toppings requires: nombre, tipo, presentacion
        add_result = IngredientService.add_ingredient(
            handler,
            categoria='Toppings',
            nombre='test_topping_temporal',
            tipo='test',
            presentacion='test_presentacion'
        )
        
        assert add_result['exito'], "Should add test ingredient"
        ingredient_id = add_result['ingrediente'].id
        print(f"\n➕ Added test ingredient: {add_result['ingrediente'].nombre} (ID: {ingredient_id})")
        
        # Delete it (should succeed immediately since it's not used)
        delete_result = IngredientService.delete_ingredient(handler, ingredient_id)
        
        print(f"\n🗑️  Delete result: {delete_result}")
        
        assert delete_result['exito'] == True, "Should delete successfully"
        assert delete_result['ingrediente_eliminado'] == True, "Ingredient should be deleted"
        assert len(delete_result['hotdogs_afectados']) == 0, "No hot dogs should be affected"
        assert delete_result['requiere_confirmacion'] == False, "No confirmation needed"
        
        # Verify it's gone
        deleted = handler.ingredientes.get(ingredient_id)
        assert deleted is None, "Ingredient should be deleted from collection"
        
        print(f"✅ Ingredient successfully deleted")
        print("\n✅ Test 4 PASSED: delete_ingredient (simple) works correctly")
        
    finally:
        teardown_test_handler(temp_dir)


def test_delete_ingredient_with_menu_dependencies():
    """Test 5: Delete ingredient used in menu (requires confirmation)."""
    print("\n" + "=" * 70)
    print("🧪 Test 5: IngredientService.delete_ingredient() - With menu dependencies")
    print("=" * 70)
    
    handler, temp_dir = setup_test_handler()
    
    try:
        # Find an ingredient that's used in the menu
        # Let's look for 'simple' pan which is likely used
        pan_simple = handler.ingredientes.get_by_name('simple', 'Pan')
        
        if not pan_simple:
            print("⚠️  'simple' pan not found, using first pan")
            panes = handler.ingredientes.get_by_category('Pan')
            pan_simple = panes[0] if panes else None
        
        assert pan_simple is not None, "Need a pan to test"
        print(f"\n🎯 Testing deletion of: {pan_simple.nombre} (ID: {pan_simple.id})")
        
        # First attempt: WITHOUT confirmation (should warn)
        result_no_confirm = IngredientService.delete_ingredient(handler, pan_simple.id)
        
        print(f"\n🔍 First attempt (no confirmation):")
        print(f"   Exito: {result_no_confirm['exito']}")
        print(f"   Requiere confirmación: {result_no_confirm.get('requiere_confirmacion', False)}")
        print(f"   Hot dogs afectados: {len(result_no_confirm.get('hotdogs_afectados', []))}")
        
        if result_no_confirm.get('requiere_confirmacion'):
            # Should require confirmation
            assert result_no_confirm['exito'] == False, "Should not delete without confirmation"
            assert result_no_confirm['ingrediente_eliminado'] == False, "Ingredient should NOT be deleted"
            
            affected_count = len(result_no_confirm['hotdogs_afectados'])
            print(f"   ⚠️  Warning: {affected_count} hot dog(s) use this ingredient")
            
            # Second attempt: WITH confirmation
            result_confirm = IngredientService.delete_ingredient(
                handler,
                pan_simple.id,
                confirmar_eliminar_hotdogs=True
            )
            
            print(f"\n🔍 Second attempt (with confirmation):")
            print(f"   Exito: {result_confirm['exito']}")
            print(f"   Ingrediente eliminado: {result_confirm['ingrediente_eliminado']}")
            print(f"   Hot dogs eliminados: {len(result_confirm['hotdogs_eliminados'])}")
            
            assert result_confirm['exito'] == True, "Should delete with confirmation"
            assert result_confirm['ingrediente_eliminado'] == True, "Ingredient should be deleted"
            assert len(result_confirm['hotdogs_eliminados']) == affected_count, "All affected hot dogs should be deleted"
            
            # Verify ingredient is gone
            deleted_ing = handler.ingredientes.get(pan_simple.id)
            assert deleted_ing is None, "Ingredient should be deleted"
            
            # Verify hot dogs are gone
            for hotdog_id in result_confirm['hotdogs_eliminados']:
                deleted_hd = handler.menu.get(hotdog_id)
                assert deleted_hd is None, f"Hot dog {hotdog_id} should be deleted"
            
            print(f"✅ Ingredient and {len(result_confirm['hotdogs_eliminados'])} hot dog(s) deleted")
        
        else:
            # Pan not used in menu (rare but possible)
            print("   ℹ️  This ingredient is not used in any hot dog")
            assert result_no_confirm['exito'] == True, "Should delete immediately if not used"
        
        print("\n✅ Test 5 PASSED: delete_ingredient (with dependencies) works correctly")
        
    finally:
        teardown_test_handler(temp_dir)


def test_delete_nonexistent_ingredient():
    """Test 6: Delete non-existent ingredient."""
    print("\n" + "=" * 70)
    print("🧪 Test 6: IngredientService.delete_ingredient() - Non-existent")
    print("=" * 70)
    
    handler, temp_dir = setup_test_handler()
    
    try:
        # Try to delete ingredient that doesn't exist
        result = IngredientService.delete_ingredient(handler, 'fake_id_12345')
        
        print(f"\n🔍 Delete non-existent result:")
        print(f"   Exito: {result['exito']}")
        print(f"   Error: {result.get('error', 'N/A')}")
        
        assert result['exito'] == False, "Should fail when ingredient doesn't exist"
        assert 'error' in result, "Should return error message"
        assert 'no encontrado' in result['error'].lower(), "Error should mention not found"
        
        print("\n✅ Test 6 PASSED: Correctly handles non-existent ingredient")
        
    finally:
        teardown_test_handler(temp_dir)


def run_all_tests():
    """Run all ingredient service tests."""
    print("\n" + "=" * 70)
    print("🌭 INGREDIENT SERVICE TEST SUITE")
    print("=" * 70)
    
    tests = [
        ("List by category", test_list_by_category),
        ("List by type", test_list_by_type),
        ("Add ingredient", test_add_ingredient),
        ("Delete ingredient (simple)", test_delete_ingredient_simple),
        ("Delete ingredient (dependencies)", test_delete_ingredient_with_menu_dependencies),
        ("Delete non-existent", test_delete_nonexistent_ingredient),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ Test FAILED: {name}")
            print(f"   Error: {e}")
            failed += 1
        except Exception as e:
            print(f"\n💥 Test ERROR: {name}")
            print(f"   Exception: {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    print("=" * 70)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
