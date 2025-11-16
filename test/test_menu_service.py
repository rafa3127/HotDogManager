"""
Test suite for MenuService.

Tests all menu management operations including listing, adding, deleting,
and checking availability of hot dogs with proper business rule validation.

Author: Rafael Correa
Date: November 16, 2025
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from clients.external_sources.github_client import GitHubClient
from clients.adapters import (
    IDAdapter,
    KeyNormalizationAdapter,
    StockInitializationAdapter,
    IngredientReferenceAdapter
)
from clients.id_processors import process_grouped_structure_ids, process_flat_structure_ids
from clients.data_source_client import DataSourceClient
from handlers.data_handler import DataHandler
from services import MenuService, IngredientService
import config


def setup_test_handler():
    """Setup DataHandler with full adapter chain for testing."""
    github = GitHubClient(
        owner=config.GITHUB_OWNER,
        repo=config.GITHUB_REPO,
        branch=config.GITHUB_BRANCH
    )
    
    # Ingredientes chain
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
    
    # Menu chain
    menu_source = IngredientReferenceAdapter(
        KeyNormalizationAdapter(
            IDAdapter(github, process_flat_structure_ids)
        ),
        ingredientes_source
    )
    
    # Initialize DataSource
    data_source = DataSourceClient(data_dir=config.DATA_DIR)
    data_source.initialize({
        'ingredientes': ingredientes_source,
        'menu': menu_source
    }, force_external=False)  # Use local cache for faster tests
    
    return DataHandler(data_source)


def teardown_test_handler(handler):
    """Teardown: commit changes to persist test state."""
    if handler.has_changes:
        handler.commit()


# ────────────────────────────────────────────────────────────
# TESTS - LISTAR HOT DOGS
# ────────────────────────────────────────────────────────────

def test_1_list_all_hotdogs():
    """Test 1: List all hot dogs in menu."""
    print("\n" + "="*70)
    print("🧪 Test 1: List all hot dogs")
    print("="*70)
    
    handler = setup_test_handler()
    
    hotdogs = MenuService.list_all(handler)
    
    assert isinstance(hotdogs, list), "Should return a list"
    assert len(hotdogs) > 0, "Should have at least one hot dog"
    
    print(f"\n✅ Found {len(hotdogs)} hot dogs in menu")
    
    # Show first few
    for i, hd in enumerate(hotdogs[:3]):
        print(f"   {i+1}. {hd.nombre}")
        print(f"      Pan: {hd.pan['nombre']}")
        print(f"      Salchicha: {hd.salchicha['nombre']}")
    
    teardown_test_handler(handler)
    print("\n✅ Test 1 PASSED\n")


def test_2_get_by_name():
    """Test 2: Get specific hot dog by name."""
    print("\n" + "="*70)
    print("🧪 Test 2: Get hot dog by name")
    print("="*70)
    
    handler = setup_test_handler()
    
    # Get first hotdog name
    all_hotdogs = MenuService.list_all(handler)
    if not all_hotdogs:
        print("⚠️  No hay hot dogs para probar")
        return
    
    test_name = all_hotdogs[0].nombre
    
    hotdog = MenuService.get_by_name(handler, test_name)
    
    assert hotdog is not None, f"Should find hotdog '{test_name}'"
    assert hotdog.nombre == test_name, "Name should match"
    
    print(f"\n✅ Found hot dog: {hotdog.nombre}")
    print(f"   Pan: {hotdog.pan['nombre']}")
    print(f"   Salchicha: {hotdog.salchicha['nombre']}")
    print(f"   Toppings: {[t['nombre'] for t in hotdog.toppings]}")
    print(f"   Salsas: {[s['nombre'] for s in hotdog.salsas]}")
    
    # Test non-existent
    non_existent = MenuService.get_by_name(handler, 'no_existe_este_hotdog')
    assert non_existent is None, "Should return None for non-existent"
    
    print(f"✅ Non-existent hot dog returns None correctly")
    
    teardown_test_handler(handler)
    print("\n✅ Test 2 PASSED\n")


def test_3_get_combos_and_simple():
    """Test 3: Get combos and simple hot dogs."""
    print("\n" + "="*70)
    print("🧪 Test 3: Get combos and simple hot dogs")
    print("="*70)
    
    handler = setup_test_handler()
    
    combos = MenuService.get_combos(handler)
    simples = MenuService.get_simple_hotdogs(handler)
    
    print(f"\n✅ Found {len(combos)} combos")
    for combo in combos[:3]:
        print(f"   - {combo.nombre} (con {combo.acompanante['nombre']})")
    
    print(f"\n✅ Found {len(simples)} simple hot dogs")
    for simple in simples[:3]:
        print(f"   - {simple.nombre}")
    
    teardown_test_handler(handler)
    print("\n✅ Test 3 PASSED\n")


# ────────────────────────────────────────────────────────────
# TESTS - VERIFICAR DISPONIBILIDAD
# ────────────────────────────────────────────────────────────

def test_4_check_availability():
    """Test 4: Check inventory availability for a hot dog."""
    print("\n" + "="*70)
    print("🧪 Test 4: Check availability")
    print("="*70)
    
    handler = setup_test_handler()
    
    # Get a hotdog to check
    all_hotdogs = MenuService.list_all(handler)
    if not all_hotdogs:
        print("⚠️  No hay hot dogs para probar")
        return
    
    hotdog = all_hotdogs[0]
    
    result = MenuService.check_availability(handler, hotdog.id)
    
    assert 'disponible' in result, "Should return disponible status"
    
    print(f"\n🔍 Checking availability for: {hotdog.nombre}")
    
    if result['disponible']:
        print(f"✅ Hay inventario suficiente")
    else:
        print(f"❌ Inventario insuficiente")
        print(f"   Faltantes:")
        for faltante in result['faltantes']:
            print(f"   - {faltante['ingrediente']} ({faltante['categoria']}): "
                  f"necesita {faltante['necesita']}, disponible {faltante['disponible']}")
    
    teardown_test_handler(handler)
    print("\n✅ Test 4 PASSED\n")


# ────────────────────────────────────────────────────────────
# TESTS - AGREGAR HOT DOG
# ────────────────────────────────────────────────────────────

def test_5_add_hotdog_success():
    """Test 5: Add a new hot dog successfully."""
    print("\n" + "="*70)
    print("🧪 Test 5: Add hot dog - Success")
    print("="*70)
    
    handler = setup_test_handler()
    
    # Get ingredient IDs
    panes = handler.ingredientes.get_by_category('Pan')
    salchichas = handler.ingredientes.get_by_category('Salchicha')
    toppings = handler.ingredientes.get_by_category('Toppings')
    salsas = handler.ingredientes.get_by_category('Salsa')
    
    # Find pan and salchicha with matching size
    pan = None
    salchicha = None
    for p in panes:
        for s in salchichas:
            if s.matches_size(p):
                pan = p
                salchicha = s
                break
        if pan and salchicha:
            break
    
    assert pan is not None, "Should find a pan"
    assert salchicha is not None, "Should find a matching salchicha"
    
    result = MenuService.add_hotdog(
        handler,
        nombre='test_hotdog_automatico',
        pan_id=pan.id,
        salchicha_id=salchicha.id,
        topping_ids=[toppings[0].id] if toppings else [],
        salsa_ids=[salsas[0].id] if salsas else [],
        acompanante_id=None
    )
    
    assert result['exito'], f"Should succeed: {result.get('error', '')}"
    assert 'hotdog' in result, "Should return created hotdog"
    assert result['hotdog'].nombre == 'test_hotdog_automatico', "Name should match"
    
    print(f"\n✅ Hot dog creado exitosamente")
    print(f"   Nombre: {result['hotdog'].nombre}")
    print(f"   Pan: {result['hotdog'].pan['nombre']} ({pan.tamano} {pan.unidad})")
    print(f"   Salchicha: {result['hotdog'].salchicha['nombre']} ({salchicha.tamano} {salchicha.unidad})")
    
    if result.get('advertencias'):
        print(f"\n⚠️  Advertencias:")
        for adv in result['advertencias']:
            print(f"   {adv}")
    
    # Verify it exists
    created = MenuService.get_by_name(handler, 'test_hotdog_automatico')
    assert created is not None, "Should find newly created hotdog"
    
    # Cleanup
    handler.menu.delete(result['hotdog'].id)
    
    teardown_test_handler(handler)
    print("\n✅ Test 5 PASSED\n")


def test_6_add_hotdog_size_mismatch_warning():
    """Test 6: Add hot dog with size mismatch - Should warn."""
    print("\n" + "="*70)
    print("🧪 Test 6: Add hot dog - Size mismatch warning")
    print("="*70)
    
    handler = setup_test_handler()
    
    # Find pan and salchicha with DIFFERENT sizes
    panes = handler.ingredientes.get_by_category('Pan')
    salchichas = handler.ingredientes.get_by_category('Salchicha')
    
    pan = None
    salchicha = None
    for p in panes:
        for s in salchichas:
            if not s.matches_size(p):  # Find mismatch
                pan = p
                salchicha = s
                break
        if pan and salchicha:
            break
    
    if not pan or not salchicha:
        print("⚠️  No se encontraron ingredientes con tamaños diferentes, skipping test")
        return
    
    result = MenuService.add_hotdog(
        handler,
        nombre='test_size_mismatch',
        pan_id=pan.id,
        salchicha_id=salchicha.id,
        topping_ids=[],
        salsa_ids=[],
        acompanante_id=None
    )
    
    assert result['exito'], "Should still succeed (it's just a warning)"
    assert 'advertencias' in result, "Should have warnings"
    assert result['advertencias'] is not None, "Warnings should not be None"
    
    # Check that warning mentions size mismatch
    warning_text = ' '.join(result['advertencias'])
    assert 'tamaños diferentes' in warning_text.lower() or 'tamaño' in warning_text.lower(), \
        "Warning should mention size mismatch"
    
    print(f"\n✅ Hot dog creado con advertencia de tamaño")
    print(f"   Pan: {pan.nombre} ({pan.tamano} {pan.unidad})")
    print(f"   Salchicha: {salchicha.nombre} ({salchicha.tamano} {salchicha.unidad})")
    print(f"\n⚠️  Advertencias recibidas:")
    for adv in result['advertencias']:
        print(f"   {adv}")
    
    # Cleanup
    handler.menu.delete(result['hotdog'].id)
    
    teardown_test_handler(handler)
    print("\n✅ Test 6 PASSED\n")


def test_7_add_hotdog_validation_errors():
    """Test 7: Add hot dog - Validation errors."""
    print("\n" + "="*70)
    print("🧪 Test 7: Add hot dog - Validation errors")
    print("="*70)
    
    handler = setup_test_handler()
    
    # Test 1: Duplicate name
    existing = MenuService.list_all(handler)
    if existing:
        result = MenuService.add_hotdog(
            handler,
            nombre=existing[0].nombre,  # Duplicate
            pan_id='dummy',
            salchicha_id='dummy'
        )
        
        assert not result['exito'], "Should fail for duplicate name"
        assert 'error' in result, "Should have error message"
        print(f"✅ Duplicate name rejected: {result['error']}")
    
    # Test 2: Invalid ingredient ID
    result = MenuService.add_hotdog(
        handler,
        nombre='test_invalid_id',
        pan_id='id_que_no_existe_123',
        salchicha_id='otro_id_invalido_456'
    )
    
    assert not result['exito'], "Should fail for invalid ingredient ID"
    assert 'error' in result, "Should have error message"
    print(f"✅ Invalid ingredient ID rejected: {result['error']}")
    
    teardown_test_handler(handler)
    print("\n✅ Test 7 PASSED\n")


# ────────────────────────────────────────────────────────────
# TESTS - ELIMINAR HOT DOG
# ────────────────────────────────────────────────────────────

def test_8_delete_hotdog_with_inventory_requires_confirmation():
    """Test 8: Delete hot dog with inventory - Requires confirmation."""
    print("\n" + "="*70)
    print("🧪 Test 8: Delete hot dog - Requires confirmation")
    print("="*70)
    
    handler = setup_test_handler()
    
    # Create a test hotdog
    panes = handler.ingredientes.get_by_category('Pan')
    salchichas = handler.ingredientes.get_by_category('Salchicha')
    
    # Find matching sizes
    pan = salchicha = None
    for p in panes:
        for s in salchichas:
            if s.matches_size(p):
                pan = p
                salchicha = s
                break
        if pan and salchicha:
            break
    
    add_result = MenuService.add_hotdog(
        handler,
        nombre='test_delete_with_inventory',
        pan_id=pan.id,
        salchicha_id=salchicha.id
    )
    
    assert add_result['exito'], "Should create hotdog"
    hotdog_id = add_result['hotdog'].id
    
    # Try to delete WITHOUT confirmation (should require confirmation)
    result = MenuService.delete_hotdog(handler, hotdog_id, confirmar_con_inventario=False)
    
    assert not result['exito'], "Should not succeed without confirmation"
    assert result.get('requiere_confirmacion'), "Should require confirmation"
    assert 'advertencia' in result, "Should have warning message"
    
    print(f"\n✅ Deletion blocked, confirmation required")
    print(f"   {result['advertencia']}")
    
    # Now delete WITH confirmation
    result = MenuService.delete_hotdog(handler, hotdog_id, confirmar_con_inventario=True)
    
    assert result['exito'], "Should succeed with confirmation"
    assert 'hotdog_eliminado' in result, "Should return deleted hotdog"
    
    print(f"\n✅ Hot dog deleted with confirmation")
    print(f"   Deleted: {result['hotdog_eliminado'].nombre}")
    
    teardown_test_handler(handler)
    print("\n✅ Test 8 PASSED\n")


def test_9_delete_hotdog_without_inventory():
    """Test 9: Delete hot dog without inventory - Direct deletion."""
    print("\n" + "="*70)
    print("🧪 Test 9: Delete hot dog without inventory")
    print("="*70)
    
    handler = setup_test_handler()
    
    # Create a hotdog with ingredients that have NO inventory
    panes = handler.ingredientes.get_by_category('Pan')
    salchichas = handler.ingredientes.get_by_category('Salchicha')
    
    pan = panes[0]
    salchicha = None
    for s in salchichas:
        if s.matches_size(pan):
            salchicha = s
            break
    
    # Set stock to 0
    original_pan_stock = pan.stock
    original_salchicha_stock = salchicha.stock
    
    IngredientService.update_stock(handler, pan.id, -pan.stock)
    IngredientService.update_stock(handler, salchicha.id, -salchicha.stock)
    
    add_result = MenuService.add_hotdog(
        handler,
        nombre='test_delete_no_inventory',
        pan_id=pan.id,
        salchicha_id=salchicha.id
    )
    
    assert add_result['exito'], "Should create hotdog"
    hotdog_id = add_result['hotdog'].id
    
    # Debug: Check availability before deletion
    availability = MenuService.check_availability(handler, hotdog_id)
    print(f"\n🔍 Debug - Availability check:")
    print(f"   Disponible: {availability['disponible']}")
    if not availability['disponible']:
        print(f"   Faltantes: {availability.get('faltantes', [])}")
    
    # Try to delete (should succeed immediately since no inventory)
    result = MenuService.delete_hotdog(handler, hotdog_id, confirmar_con_inventario=False)
    
    print(f"\n🔍 Debug - Delete result:")
    print(f"   Exito: {result.get('exito')}")
    print(f"   Requiere confirmacion: {result.get('requiere_confirmacion')}")
    if 'advertencia' in result:
        print(f"   Advertencia: {result['advertencia']}")
    if 'error' in result:
        print(f"   Error: {result['error']}")
    
    assert result['exito'], f"Should succeed without confirmation (no inventory). Got: {result}"
    assert 'hotdog_eliminado' in result, "Should return deleted hotdog"
    assert not result.get('requiere_confirmacion'), "Should NOT require confirmation"
    
    print(f"\n✅ Hot dog deleted directly (no inventory)")
    print(f"   Deleted: {result['hotdog_eliminado'].nombre}")
    
    # Restore stock
    IngredientService.update_stock(handler, pan.id, original_pan_stock)
    IngredientService.update_stock(handler, salchicha.id, original_salchicha_stock)
    
    teardown_test_handler(handler)
    print("\n✅ Test 9 PASSED\n")


def test_10_delete_nonexistent_hotdog():
    """Test 10: Delete non-existent hot dog."""
    print("\n" + "="*70)
    print("🧪 Test 10: Delete non-existent hot dog")
    print("="*70)
    
    handler = setup_test_handler()
    
    result = MenuService.delete_hotdog(handler, 'id_que_no_existe_xyz')
    
    assert not result['exito'], "Should fail"
    assert 'error' in result, "Should have error message"
    
    print(f"✅ Non-existent hotdog deletion rejected: {result['error']}")
    
    teardown_test_handler(handler)
    print("\n✅ Test 10 PASSED\n")


# ────────────────────────────────────────────────────────────
# TESTS - ESTADÍSTICAS
# ────────────────────────────────────────────────────────────

def test_11_get_stats():
    """Test 11: Get menu statistics."""
    print("\n" + "="*70)
    print("🧪 Test 11: Get menu statistics")
    print("="*70)
    
    handler = setup_test_handler()
    
    stats = MenuService.get_stats(handler)
    
    assert 'total' in stats, "Should have total count"
    assert 'combos' in stats, "Should have combos count"
    assert 'simples' in stats, "Should have simples count"
    
    print(f"\n📊 Menu Statistics:")
    print(f"   Total hot dogs: {stats['total']}")
    print(f"   Combos: {stats['combos']}")
    print(f"   Simples: {stats['simples']}")
    print(f"   Con toppings: {stats['con_toppings']}")
    print(f"   Con salsas: {stats['con_salsas']}")
    
    teardown_test_handler(handler)
    print("\n✅ Test 11 PASSED\n")


# ────────────────────────────────────────────────────────────
# RUN ALL TESTS
# ────────────────────────────────────────────────────────────

def run_all_tests():
    """Run all MenuService tests."""
    print("\n" + "="*70)
    print("🚀 MENU SERVICE TEST SUITE")
    print("="*70)
    
    tests = [
        test_1_list_all_hotdogs,
        test_2_get_by_name,
        test_3_get_combos_and_simple,
        test_4_check_availability,
        test_5_add_hotdog_success,
        test_6_add_hotdog_size_mismatch_warning,
        test_7_add_hotdog_validation_errors,
        test_8_delete_hotdog_with_inventory_requires_confirmation,
        test_9_delete_hotdog_without_inventory,
        test_10_delete_nonexistent_hotdog,
        test_11_get_stats,
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
    
    print("\n" + "="*70)
    print("📊 FINAL RESULTS")
    print("="*70)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
    
    print("="*70 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
