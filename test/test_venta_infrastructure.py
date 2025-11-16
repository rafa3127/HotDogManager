"""
Quick test to verify Venta entity infrastructure.

Tests:
    - Schema loading
    - Plugin registration
    - Entity creation
    - Collection CRUD
    - DataHandler integration

Author: Rafael Correa
Date: November 16, 2025
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import create_venta_entities
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
import config


def test_venta_infrastructure():
    """Test complete Venta infrastructure."""
    print("\n" + "="*70)
    print("🧪 VENTA INFRASTRUCTURE TEST")
    print("="*70)
    
    # ─── TEST 1: Entity Creation ───
    print("\n1️⃣ Creating Venta entity class...")
    venta_entities = create_venta_entities()
    Venta = venta_entities['Venta']
    print(f"   ✅ Venta class created: {Venta}")
    
    # ─── TEST 2: Create Instance ───
    print("\n2️⃣ Creating Venta instance...")
    venta = Venta(
        id='venta-test-001',
        entity_type='Venta',
        fecha='2024-11-16T14:30:00',
        items=[
            {
                'hotdog_id': 'hotdog-simple',
                'hotdog_nombre': 'simple',
                'cantidad': 2
            },
            {
                'hotdog_id': 'hotdog-combo',
                'hotdog_nombre': 'combo especial',
                'cantidad': 1
            }
        ]
    )
    print(f"   ✅ Instance created: {venta}")
    
    # ─── TEST 3: Validation ───
    print("\n3️⃣ Testing validation...")
    try:
        venta.validate()
        print(f"   ✅ Validation passed")
    except ValueError as e:
        print(f"   ❌ Validation failed: {e}")
        return False
    
    # ─── TEST 4: to_dict / from_dict ───
    print("\n4️⃣ Testing serialization...")
    venta_dict = venta.to_dict()
    print(f"   ✅ to_dict: {venta_dict}")
    
    venta_restored = Venta.from_dict(venta_dict)
    print(f"   ✅ from_dict: {venta_restored}")
    
    # ─── TEST 5: Invalid Venta (should fail validation) ───
    print("\n5️⃣ Testing invalid venta...")
    try:
        invalid_venta = Venta(
            id='invalid-001',
            entity_type='Venta',
            fecha='',  # Empty fecha (should fail)
            items=[]    # Empty items (should fail)
        )
        invalid_venta.validate()
        print(f"   ❌ Validation should have failed!")
        return False
    except ValueError as e:
        print(f"   ✅ Validation correctly failed: {e}")
    
    # ─── TEST 6: DataHandler Integration ───
    print("\n6️⃣ Testing DataHandler integration...")
    
    # Setup complete data source (like other tests)
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
    
    # Initialize DataSource with ALL collections
    data_source = DataSourceClient(data_dir=config.DATA_DIR)
    data_source.initialize({
        'ingredientes': ingredientes_source,
        'menu': menu_source,
        'ventas': None  # Will load from local ventas.json (empty list)
    }, force_external=False)
    
    handler = DataHandler(data_source)
    print(f"   ✅ DataHandler initialized with all collections")
    print(f"   - Ingredientes: {handler.ingredientes}")
    print(f"   - Menu: {handler.menu}")
    print(f"   - Ventas: {handler.ventas}")
    
    # ─── TEST 7: Collection CRUD ───
    print("\n7️⃣ Testing Collection CRUD...")
    
    # Add venta
    handler.ventas.add(venta)
    print(f"   ✅ Added venta to collection")
    
    # Get venta
    retrieved = handler.ventas.get('venta-test-001')
    assert retrieved is not None, "Should retrieve venta"
    print(f"   ✅ Retrieved venta: {retrieved.id}")
    
    # Check dirty flag
    assert handler.has_changes, "Should have changes"
    print(f"   ✅ Handler detected changes")
    
    # Commit
    handler.commit()
    print(f"   ✅ Changes committed")
    
    # Reload and verify persistence
    handler2 = DataHandler(data_source)
    retrieved2 = handler2.ventas.get('venta-test-001')
    assert retrieved2 is not None, "Should persist across reloads"
    print(f"   ✅ Venta persisted: {retrieved2.id}")
    
    # Cleanup
    handler2.ventas.delete('venta-test-001')
    handler2.commit()
    print(f"   ✅ Test venta cleaned up")
    
    # ─── TEST 8: Collection Query Methods ───
    print("\n8️⃣ Testing Collection query methods...")
    
    # Make sure we start clean
    handler.ventas.clear()
    handler.commit()
    print(f"   ✅ Cleared existing ventas")
    
    # Create test ventas
    venta1 = Venta(
        id='venta-2024-11-16-001',
        entity_type='Venta',
        fecha='2024-11-16T10:00:00',
        items=[{'hotdog_id': 'h1', 'hotdog_nombre': 'simple', 'cantidad': 1}]
    )
    
    venta2 = Venta(
        id='venta-2024-11-16-002',
        entity_type='Venta',
        fecha='2024-11-16T15:00:00',
        items=[{'hotdog_id': 'h2', 'hotdog_nombre': 'combo', 'cantidad': 2}]
    )
    
    venta3 = Venta(
        id='venta-2024-11-17-001',
        entity_type='Venta',
        fecha='2024-11-17T12:00:00',
        items=[{'hotdog_id': 'h1', 'hotdog_nombre': 'simple', 'cantidad': 3}]
    )
    
    handler.ventas.add(venta1)
    handler.ventas.add(venta2)
    handler.ventas.add(venta3)
    handler.commit()  # Save to disk so you can see the data
    print(f"   ✅ Created 3 test ventas and saved to disk")
    
    # Test get_by_date
    ventas_nov_16 = handler.ventas.get_by_date('2024-11-16')
    assert len(ventas_nov_16) == 2, f"Should find 2 ventas on 2024-11-16, found {len(ventas_nov_16)}"
    print(f"   ✅ get_by_date found {len(ventas_nov_16)} ventas")
    
    # Test get_by_hotdog
    ventas_with_h1 = handler.ventas.get_by_hotdog('h1')
    assert len(ventas_with_h1) == 2, f"Should find 2 ventas with h1, found {len(ventas_with_h1)}"
    print(f"   ✅ get_by_hotdog found {len(ventas_with_h1)} ventas")
    
    # Test get_stats
    stats = handler.ventas.get_stats()
    assert stats['total'] == 3, f"Should have 3 total ventas, got {stats['total']}"
    print(f"   ✅ get_stats: {stats}")
    
    # Keep test data so you can see it in ventas.json
    print(f"   💾 Test ventas saved to data/ventas.json for inspection")
    
    # ─── SUCCESS ───
    print("\n" + "="*70)
    print("🎉 ALL TESTS PASSED!")
    print("="*70 + "\n")
    
    return True


if __name__ == "__main__":
    try:
        success = test_venta_infrastructure()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n💥 TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
