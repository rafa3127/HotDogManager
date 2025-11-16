"""
Test suite for VentaService.

Tests the deferred venta builder pattern with step-by-step construction,
preview, and confirmation with inventory deduction.

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
from services import VentaService, IngredientService
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
        'menu': menu_source,
        'ventas': None  # Load from local
    }, force_external=False)
    
    return DataHandler(data_source)


def teardown_test_handler(handler):
    """Teardown: commit changes to persist test state."""
    if handler.has_changes:
        handler.commit()


# ────────────────────────────────────────────────────────────
# TESTS - VENTA BUILDER (DRAFT MANAGEMENT)
# ────────────────────────────────────────────────────────────

def test_1_create_draft():
    """Test 1: Create empty venta draft."""
    print("\n" + "="*70)
    print("🧪 Test 1: Create venta draft")
    print("="*70)
    
    builder = VentaService.create_draft()
    
    assert builder is not None, "Should create builder"
    assert len(builder.items) == 0, "Should start empty"
    assert builder.get_total_items() == 0, "Total should be 0"
    
    print(f"\n✅ Draft created: {builder}")
    print("\n✅ Test 1 PASSED\n")


def test_2_add_items_to_draft():
    """Test 2: Add items to draft."""
    print("\n" + "="*70)
    print("🧪 Test 2: Add items to draft")
    print("="*70)
    
    handler = setup_test_handler()
    builder = VentaService.create_draft()
    
    # Get some hotdogs from menu
    all_hotdogs = handler.menu.get_all()
    assert len(all_hotdogs) > 0, "Should have hotdogs in menu"
    
    hotdog1 = all_hotdogs[0]
    hotdog2 = all_hotdogs[1] if len(all_hotdogs) > 1 else all_hotdogs[0]
    
    # Add first item
    result1 = VentaService.add_item(handler, builder, hotdog1.id, cantidad=2)
    assert result1['exito'], f"Should add item 1: {result1.get('error', '')}"
    assert not result1['merged'], "First add should not be merged"
    
    print(f"\n✅ Added item 1: {hotdog1.nombre} x 2")
    
    # Add second item
    result2 = VentaService.add_item(handler, builder, hotdog2.id, cantidad=1)
    assert result2['exito'], f"Should add item 2: {result2.get('error', '')}"
    
    print(f"✅ Added item 2: {hotdog2.nombre} x 1")
    
    # Verify builder state
    assert len(builder.items) > 0, "Should have items"
    print(f"✅ Builder has {len(builder.items)} items, total cantidad: {builder.get_total_items()}")
    
    teardown_test_handler(handler)
    print("\n✅ Test 2 PASSED\n")


def test_3_add_same_item_merges_quantity():
    """Test 3: Adding same item merges quantity."""
    print("\n" + "="*70)
    print("🧪 Test 3: Add same item - quantity merging")
    print("="*70)
    
    handler = setup_test_handler()
    builder = VentaService.create_draft()
    
    hotdog = handler.menu.get_all()[0]
    
    # Add first time
    result1 = VentaService.add_item(handler, builder, hotdog.id, cantidad=2)
    assert result1['exito'], "Should add first time"
    assert not result1['merged'], "First add should not be merged"
    
    print(f"\n✅ First add: {hotdog.nombre} x 2")
    
    # Add same hotdog again
    result2 = VentaService.add_item(handler, builder, hotdog.id, cantidad=3)
    assert result2['exito'], "Should add second time"
    assert result2['merged'], "Second add SHOULD be merged"
    
    print(f"✅ Second add: {hotdog.nombre} x 3 (merged)")
    
    # Should only have 1 item with cantidad=5
    assert len(builder.items) == 1, f"Should have 1 item, got {len(builder.items)}"
    assert builder.items[0]['cantidad'] == 5, f"Cantidad should be 5, got {builder.items[0]['cantidad']}"
    assert builder.get_total_items() == 5, "Total should be 5"
    
    print(f"✅ Merged correctly: 1 item with cantidad=5")
    
    teardown_test_handler(handler)
    print("\n✅ Test 3 PASSED\n")


def test_4_remove_item_from_draft():
    """Test 4: Remove item from draft."""
    print("\n" + "="*70)
    print("🧪 Test 4: Remove item from draft")
    print("="*70)
    
    handler = setup_test_handler()
    builder = VentaService.create_draft()
    
    hotdogs = handler.menu.get_all()[:2]
    
    # Add two items
    VentaService.add_item(handler, builder, hotdogs[0].id, cantidad=2)
    VentaService.add_item(handler, builder, hotdogs[1].id, cantidad=1)
    
    assert len(builder.items) == 2, "Should have 2 items"
    print(f"\n✅ Added 2 items")
    
    # Remove first item
    result = VentaService.remove_item(builder, hotdogs[0].id)
    assert result['exito'], "Should succeed"
    assert result['removed'], "Should be removed"
    
    assert len(builder.items) == 1, "Should have 1 item left"
    assert builder.items[0]['hotdog_id'] == hotdogs[1].id, "Should have second item"
    
    print(f"✅ Removed first item, 1 item remaining")
    
    # Try to remove non-existent
    result2 = VentaService.remove_item(builder, 'non-existent-id')
    assert result2['exito'], "Should succeed (but not removed)"
    assert not result2['removed'], "Should not be removed"
    
    print(f"✅ Removing non-existent returns removed=False")
    
    teardown_test_handler(handler)
    print("\n✅ Test 4 PASSED\n")


def test_5_update_quantity():
    """Test 5: Update item quantity."""
    print("\n" + "="*70)
    print("🧪 Test 5: Update item quantity")
    print("="*70)
    
    handler = setup_test_handler()
    builder = VentaService.create_draft()
    
    hotdog = handler.menu.get_all()[0]
    
    # Add item
    VentaService.add_item(handler, builder, hotdog.id, cantidad=2)
    assert builder.items[0]['cantidad'] == 2, "Should start with 2"
    
    print(f"\n✅ Initial cantidad: 2")
    
    # Update to 5
    result = VentaService.update_quantity(builder, hotdog.id, cantidad=5)
    assert result['exito'], "Should succeed"
    assert result['updated'], "Should be updated"
    assert builder.items[0]['cantidad'] == 5, "Should be 5 now"
    
    print(f"✅ Updated to cantidad: 5")
    
    # Try invalid cantidad
    result2 = VentaService.update_quantity(builder, hotdog.id, cantidad=0)
    assert not result2['exito'], "Should fail with 0"
    assert 'error' in result2, "Should have error"
    
    print(f"✅ Rejected invalid cantidad (0)")
    
    teardown_test_handler(handler)
    print("\n✅ Test 5 PASSED\n")


def test_6_clear_draft():
    """Test 6: Clear all items from draft."""
    print("\n" + "="*70)
    print("🧪 Test 6: Clear draft")
    print("="*70)
    
    handler = setup_test_handler()
    builder = VentaService.create_draft()
    
    # Add multiple items
    hotdogs = handler.menu.get_all()[:3]
    for hotdog in hotdogs:
        VentaService.add_item(handler, builder, hotdog.id, cantidad=1)
    
    assert len(builder.items) > 0, "Should have items"
    print(f"\n✅ Added {len(builder.items)} items")
    
    # Clear
    result = VentaService.clear_draft(builder)
    assert result['exito'], "Should succeed"
    assert len(builder.items) == 0, "Should be empty"
    assert builder.get_total_items() == 0, "Total should be 0"
    
    print(f"✅ Cleared all items")
    
    teardown_test_handler(handler)
    print("\n✅ Test 6 PASSED\n")


# ────────────────────────────────────────────────────────────
# TESTS - PREVIEW
# ────────────────────────────────────────────────────────────

def test_7_preview_draft():
    """Test 7: Preview draft before confirming."""
    print("\n" + "="*70)
    print("🧪 Test 7: Preview draft")
    print("="*70)
    
    handler = setup_test_handler()
    builder = VentaService.create_draft()
    
    # Add items
    hotdogs = handler.menu.get_all()[:2]
    VentaService.add_item(handler, builder, hotdogs[0].id, cantidad=2)
    VentaService.add_item(handler, builder, hotdogs[1].id, cantidad=1)
    
    # Preview
    preview = VentaService.preview_draft(handler, builder)
    
    assert 'items' in preview, "Should have items"
    assert 'total_items' in preview, "Should have total"
    assert 'disponible' in preview, "Should have disponible flag"
    
    print(f"\n✅ Preview generated:")
    print(f"   - Items: {len(preview['items'])}")
    print(f"   - Total cantidad: {preview['total_items']}")
    print(f"   - Disponible: {preview['disponible']}")
    
    if not preview['disponible']:
        print(f"   - Faltantes: {preview['hotdogs_sin_inventario']}")
    
    teardown_test_handler(handler)
    print("\n✅ Test 7 PASSED\n")


def test_8_preview_empty_draft():
    """Test 8: Preview empty draft."""
    print("\n" + "="*70)
    print("🧪 Test 8: Preview empty draft")
    print("="*70)
    
    handler = setup_test_handler()
    builder = VentaService.create_draft()
    
    # Preview empty
    preview = VentaService.preview_draft(handler, builder)
    
    assert preview['total_items'] == 0, "Should be 0"
    assert preview['disponible'], "Empty should be disponible"
    assert len(preview['items']) == 0, "Should have no items"
    
    print(f"\n✅ Empty draft preview works correctly")
    
    teardown_test_handler(handler)
    print("\n✅ Test 8 PASSED\n")


# ────────────────────────────────────────────────────────────
# TESTS - CONFIRM SALE
# ────────────────────────────────────────────────────────────

def test_9_confirm_sale_success():
    """Test 9: Confirm sale successfully."""
    print("\n" + "="*70)
    print("🧪 Test 9: Confirm sale - Success")
    print("="*70)
    
    handler = setup_test_handler()
    builder = VentaService.create_draft()
    
    # Get hotdog and check initial stock
    hotdog = handler.menu.get_all()[0]
    
    # Get stock before sale
    pan_id = hotdog.pan['id']
    salchicha_id = hotdog.salchicha['id']
    
    pan_stock_before = IngredientService.get_stock(handler, pan_id)
    salchicha_stock_before = IngredientService.get_stock(handler, salchicha_id)
    
    print(f"\n📊 Stock BEFORE sale:")
    print(f"   - Pan: {pan_stock_before}")
    print(f"   - Salchicha: {salchicha_stock_before}")
    
    # Add item
    cantidad_vendida = 2
    VentaService.add_item(handler, builder, hotdog.id, cantidad=cantidad_vendida)
    
    # Confirm
    result = VentaService.confirm_sale(handler, builder, fecha='2024-11-16T10:00:00')
    
    assert result['exito'], f"Should succeed: {result.get('error', '')}"
    assert 'venta' in result, "Should have venta entity"
    assert 'inventario_descontado' in result, "Should have inventory info"
    
    print(f"\n✅ Sale confirmed!")
    print(f"   - Venta ID: {result['venta'].id}")
    print(f"   - Items: {len(result['venta'].items)}")
    print(f"   - Inventario descontado: {len(result['inventario_descontado'])} ingredientes")
    
    # Commit to persist
    handler.commit()
    
    # Verify stock was deducted
    pan_stock_after = IngredientService.get_stock(handler, pan_id)
    salchicha_stock_after = IngredientService.get_stock(handler, salchicha_id)
    
    print(f"\n📊 Stock AFTER sale:")
    print(f"   - Pan: {pan_stock_after} (was {pan_stock_before})")
    print(f"   - Salchicha: {salchicha_stock_after} (was {salchicha_stock_before})")
    
    assert pan_stock_after == pan_stock_before - cantidad_vendida, "Pan stock should decrease"
    assert salchicha_stock_after == salchicha_stock_before - cantidad_vendida, "Salchicha stock should decrease"
    
    print(f"✅ Inventory correctly deducted ({cantidad_vendida} units)")
    
    # Verify venta exists in collection
    venta_saved = handler.ventas.get(result['venta'].id)
    assert venta_saved is not None, "Venta should be in collection"
    
    print(f"✅ Venta persisted in collection")
    
    teardown_test_handler(handler)
    print("\n✅ Test 9 PASSED\n")


def test_10_confirm_empty_draft_fails():
    """Test 10: Confirm empty draft should fail."""
    print("\n" + "="*70)
    print("🧪 Test 10: Confirm empty draft - Should fail")
    print("="*70)
    
    handler = setup_test_handler()
    builder = VentaService.create_draft()
    
    # Try to confirm empty
    result = VentaService.confirm_sale(handler, builder)
    
    assert not result['exito'], "Should fail"
    assert 'error' in result, "Should have error message"
    
    print(f"\n✅ Empty draft rejected: {result['error']}")
    
    teardown_test_handler(handler)
    print("\n✅ Test 10 PASSED\n")


def test_11_confirm_without_inventory_fails():
    """Test 11: Confirm sale without inventory should fail."""
    print("\n" + "="*70)
    print("🧪 Test 11: Confirm sale without inventory - Should fail")
    print("="*70)
    
    handler = setup_test_handler()
    builder = VentaService.create_draft()
    
    # Get hotdog
    hotdog = handler.menu.get_all()[0]
    
    # Deplete stock
    pan_id = hotdog.pan['id']
    salchicha_id = hotdog.salchicha['id']
    
    pan = handler.ingredientes.get(pan_id)
    salchicha = handler.ingredientes.get(salchicha_id)
    
    IngredientService.update_stock(handler, pan_id, -pan.stock)
    IngredientService.update_stock(handler, salchicha_id, -salchicha.stock)
    
    print(f"\n✅ Depleted stock to 0")
    
    # Add item to draft
    VentaService.add_item(handler, builder, hotdog.id, cantidad=1)
    
    # Try to confirm
    result = VentaService.confirm_sale(handler, builder)
    
    assert not result['exito'], "Should fail"
    assert 'error' in result, "Should have error"
    assert 'faltantes' in result or 'hotdogs_sin_inventario' in result, "Should list what's missing"
    
    print(f"\n✅ Sale rejected: {result['error']}")
    if 'hotdogs_sin_inventario' in result:
        print(f"   - Hot dogs sin inventario: {result['hotdogs_sin_inventario']}")
    
    # Restore stock
    IngredientService.update_stock(handler, pan_id, 100)
    IngredientService.update_stock(handler, salchicha_id, 75)
    
    teardown_test_handler(handler)
    print("\n✅ Test 11 PASSED\n")


def test_12_complete_workflow():
    """Test 12: Complete workflow - Create, build, preview, confirm."""
    print("\n" + "="*70)
    print("🧪 Test 12: Complete workflow")
    print("="*70)
    
    handler = setup_test_handler()
    
    # Step 1: Create draft
    print("\n1️⃣ Creating draft...")
    builder = VentaService.create_draft()
    print(f"   ✅ {builder}")
    
    # Step 2: Add items
    print("\n2️⃣ Adding items...")
    hotdogs = handler.menu.get_all()[:3]
    
    for i, hotdog in enumerate(hotdogs[:2]):
        result = VentaService.add_item(handler, builder, hotdog.id, cantidad=i+1)
        if result['exito']:
            print(f"   ✅ Added: {hotdog.nombre} x {i+1}")
    
    # Step 3: Preview
    print("\n3️⃣ Previewing...")
    preview = VentaService.preview_draft(handler, builder)
    print(f"   📋 Items: {len(preview['items'])}")
    print(f"   📊 Total: {preview['total_items']}")
    print(f"   {'✅' if preview['disponible'] else '❌'} Disponible: {preview['disponible']}")
    
    # Step 4: Confirm (only if available)
    if preview['disponible']:
        print("\n4️⃣ Confirming sale...")
        result = VentaService.confirm_sale(handler, builder)
        
        if result['exito']:
            print(f"   ✅ Venta confirmed: {result['venta'].id}")
            print(f"   📦 Inventory deducted: {len(result['inventario_descontado'])} ingredients")
            handler.commit()
            print(f"   💾 Changes committed")
        else:
            print(f"   ❌ Failed: {result['error']}")
    else:
        print("\n⚠️  Skipping confirmation - no inventory")
    
    teardown_test_handler(handler)
    print("\n✅ Test 12 PASSED\n")


# ────────────────────────────────────────────────────────────
# RUN ALL TESTS
# ────────────────────────────────────────────────────────────

def run_all_tests():
    """Run all VentaService tests."""
    print("\n" + "="*70)
    print("🚀 VENTA SERVICE TEST SUITE")
    print("="*70)
    
    tests = [
        test_1_create_draft,
        test_2_add_items_to_draft,
        test_3_add_same_item_merges_quantity,
        test_4_remove_item_from_draft,
        test_5_update_quantity,
        test_6_clear_draft,
        test_7_preview_draft,
        test_8_preview_empty_draft,
        test_9_confirm_sale_success,
        test_10_confirm_empty_draft_fails,
        test_11_confirm_without_inventory_fails,
        test_12_complete_workflow,
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
