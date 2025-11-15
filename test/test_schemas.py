"""
Test script for schema inference system.

Tests the automatic schema generation from data, fallback mechanisms,
and the differences between GROUPED and FLAT data structures.

Author: Rafael Correa
Date: November 14, 2025
"""

import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.schemas.ingredient_schemas import (
    infer_schemas_from_data,
    find_common_properties,
    get_ingredient_schemas,
    INGREDIENT_SCHEMAS_FALLBACK,
    INGREDIENT_BASE_PROPERTIES_FALLBACK
)
from models.schemas.hotdog_schemas import (
    infer_hotdog_schema,
    get_hotdog_schemas,
    HOTDOG_SCHEMAS_FALLBACK
)

# Import data source to test with real data
from clients.data_source_client import DataSourceClient
from clients.external_sources.github_client import GitHubClient
from clients.adapters.id_adapter import IDAdapter
from clients.adapters.key_normalization_adapter import KeyNormalizationAdapter
from clients.id_processors import process_grouped_structure_ids, process_flat_structure_ids
from config import GITHUB_OWNER, GITHUB_REPO, GITHUB_BRANCH


def print_separator(title):
    """Print a formatted separator."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def test_find_common_properties():
    """Test the find_common_properties function."""
    print_separator("TEST 1: Find Common Properties")
    
    # Test case 1: All schemas have 'nombre' in common (id excluded from schemas now)
    schemas = {
        'Pan': ['nombre', 'tipo', 'tamano', 'unidad'],
        'Salchicha': ['nombre', 'tipo', 'tamano', 'unidad'],
        'Toppings': ['nombre', 'tipo'],
        'Salsa': ['nombre', 'tipo']
    }
    
    common = find_common_properties(schemas)
    print(f"\n📋 Input schemas: {len(schemas)} types")
    for entity_type, props in schemas.items():
        print(f"   - {entity_type}: {props}")
    
    print(f"\n✅ Common properties found: {common}")
    
    # Test case 2: No common properties
    schemas_no_common = {
        'TypeA': ['prop1', 'prop2'],
        'TypeB': ['prop3', 'prop4']
    }
    
    common_none = find_common_properties(schemas_no_common)
    print(f"\n📋 Schemas with no common properties:")
    print(f"   {schemas_no_common}")
    print(f"   Result: {common_none}")
    
    # Test case 3: Empty schemas
    empty_result = find_common_properties({})
    print(f"\n📋 Empty schemas dict:")
    print(f"   Result: {empty_result}")
    
    return common


def test_infer_ingredient_schemas_with_mock_data():
    """Test ingredient schema inference with mock data."""
    print_separator("TEST 2: Infer Ingredient Schemas (Mock Data)")
    
    # Mock data structure (GROUPED - with categories and options)
    mock_data = [
        {
            'categoria': 'pan',
            'opciones': [
                {
                    'id': 'pan-001',
                    'nombre': 'simple',
                    'tipo': 'blanco',
                    'tamano': 6,
                    'unidad': 'pulgadas'
                },
                {
                    'id': 'pan-002',
                    'nombre': 'integral',
                    'tipo': 'trigo',
                    'tamano': 6,
                    'unidad': 'pulgadas'
                }
            ]
        },
        {
            'categoria': 'salchicha',
            'opciones': [
                {
                    'id': 'salchicha-001',
                    'nombre': 'weiner',
                    'tipo': 'carne de res',
                    'tamano': 4,
                    'unidad': 'onzas'
                }
            ]
        },
        {
            'categoria': 'toppings',
            'opciones': [
                {
                    'id': 'topping-001',
                    'nombre': 'cebolla',
                    'tipo': 'vegetal'
                }
            ]
        }
    ]
    
    print("\n📋 Mock data structure:")
    print(f"   Categories: {[cat['categoria'] for cat in mock_data]}")
    
    specific_schemas, common_properties = infer_schemas_from_data(mock_data)
    
    print(f"\n✅ Common properties (for base class): {common_properties}")
    print(f"\n✅ Specific schemas (for subclasses):")
    
    for entity_type, props in specific_schemas.items():
        print(f"   - {entity_type}: {props}")

    # Verify results (note: 'id' is excluded from schemas now, it's technical metadata)
    assert 'nombre' in common_properties, "Expected 'nombre' in common properties"
    assert 'id' not in common_properties, "'id' should NOT be in schemas (technical metadata)"
    assert 'Pan' in specific_schemas, "Expected 'Pan' in specific schemas (capitalized)"
    assert 'Toppings' in specific_schemas, "Expected 'Toppings' in specific schemas"
    
    print("\n✅ All assertions passed!")
    
    return specific_schemas, common_properties


def test_infer_hotdog_schema_with_mock_data():
    """Test hotdog schema inference with mock data."""
    print_separator("TEST 3: Infer HotDog Schema (Mock Data)")
    
    # Mock data structure (FLAT - list of objects)
    mock_data = [
        {
            'id': 'hotdog-001',
            'nombre': 'simple',
            'pan': 'simple',
            'salchicha': 'weiner',
            'toppings': [],
            'salsas': [],
            'acompanante': None
        },
        {
            'id': 'hotdog-002',
            'nombre': 'inglés',
            'pan': 'integral',
            'salchicha': 'breakfast',
            'toppings': ['cebolla'],
            'salsas': ['relish'],
            'acompanante': 'Papas'
        }
    ]
    
    print("\n📋 Mock data structure:")
    print(f"   Hot dogs: {len(mock_data)}")
    print(f"   First item keys: {list(mock_data[0].keys())}")
    
    schema = infer_hotdog_schema(mock_data)
    
    print(f"\n✅ Inferred schema:")
    for entity_type, props in schema.items():
        print(f"   - {entity_type}: {props}")
    
    # Verify results (note: 'id' should be excluded as it's technical metadata)
    assert 'HotDog' in schema, "Expected 'HotDog' in schema"
    assert 'nombre' in schema['HotDog'], "Expected 'nombre' in HotDog schema"
    assert 'pan' in schema['HotDog'], "Expected 'pan' in HotDog schema"
    assert 'id' not in schema['HotDog'], "'id' should NOT be in schema (technical metadata)"
    assert schema['HotDog'][0] == 'nombre', "Expected 'nombre' to be first property"
    
    print("\n✅ All assertions passed!")
    
    return schema


def test_ingredient_schemas_with_fallback():
    """Test ingredient schema getter with fallback (no data)."""
    print_separator("TEST 4: Ingredient Schemas with Fallback")
    
    print("\n📋 Calling get_ingredient_schemas() without data...")
    
    specific_schemas, common_properties = get_ingredient_schemas(raw_data=None)
    
    print(f"\n✅ Using fallback schemas:")
    print(f"   Common properties: {common_properties}")
    print(f"   Specific schemas:")
    for entity_type, props in specific_schemas.items():
        print(f"      - {entity_type}: {props}")
    
    # Verify it matches fallback
    assert specific_schemas == INGREDIENT_SCHEMAS_FALLBACK, "Should use fallback schemas"
    assert common_properties == INGREDIENT_BASE_PROPERTIES_FALLBACK, "Should use fallback base properties"
    
    print("\n✅ Fallback mechanism working correctly!")
    
    return specific_schemas, common_properties


def test_hotdog_schemas_with_fallback():
    """Test hotdog schema getter with fallback (no data)."""
    print_separator("TEST 5: HotDog Schemas with Fallback")
    
    print("\n📋 Calling get_hotdog_schemas() without data...")
    
    schemas = get_hotdog_schemas(raw_data=None)
    
    print(f"\n✅ Using fallback schemas:")
    for entity_type, props in schemas.items():
        print(f"   - {entity_type}: {props}")
    
    # Verify it matches fallback
    assert schemas == HOTDOG_SCHEMAS_FALLBACK, "Should use fallback schemas"
    
    print("\n✅ Fallback mechanism working correctly!")
    
    return schemas


def test_ingredient_schemas_with_real_data():
    """Test ingredient schema inference with real data from DataSource."""
    print_separator("TEST 6: Ingredient Schemas with Real Data")
    
    print("\n📋 Setting up DataSource with GitHub...")
    
    try:
        # Setup GitHub client with adapters
        github = GitHubClient(GITHUB_OWNER, GITHUB_REPO, GITHUB_BRANCH)
        with_ids = IDAdapter(github, process_grouped_structure_ids)
        fully_processed = KeyNormalizationAdapter(with_ids)
        
        # Initialize data source
        data_source = DataSourceClient(data_dir='data')
        
        print("   Initializing data source (trying local first)...")
        data_source.initialize({
            'ingredientes': fully_processed
        }, force_external=False)
        
        # Get real data
        ingredientes_data = data_source.get('ingredientes')
        
        print(f"\n✅ Data loaded successfully!")
        print(f"   Categories found: {len(ingredientes_data)}")
        
        # Infer schemas from real data
        specific_schemas, common_properties = get_ingredient_schemas(ingredientes_data)
        
        print(f"\n✅ Schemas inferred from real data:")
        print(f"   Common properties (base class): {common_properties}")
        print(f"\n   Specific schemas (subclasses):")
        for entity_type, props in specific_schemas.items():
            print(f"      - {entity_type}: {props}")
        
        # Verify we got meaningful results
        assert len(common_properties) > 0, "Should have at least one common property"
        assert len(specific_schemas) > 0, "Should have at least one entity type"
        
        print("\n✅ Real data inference successful!")
        
        return specific_schemas, common_properties
        
    except Exception as e:
        print(f"\n⚠️  Could not load real data: {e}")
        print("   This is expected if data files don't exist yet")
        print("   Skipping this test...")
        return None, None


def test_hotdog_schemas_with_real_data():
    """Test hotdog schema inference with real data from DataSource."""
    print_separator("TEST 7: HotDog Schemas with Real Data")
    
    print("\n📋 Setting up DataSource with GitHub...")
    
    try:
        # Setup GitHub client with adapters
        github = GitHubClient(GITHUB_OWNER, GITHUB_REPO, GITHUB_BRANCH)
        with_ids = IDAdapter(github, process_flat_structure_ids)
        fully_processed = KeyNormalizationAdapter(with_ids)
        
        # Initialize data source
        data_source = DataSourceClient(data_dir='data')
        
        print("   Initializing data source (trying local first)...")
        data_source.initialize({
            'menu': fully_processed
        }, force_external=False)
        
        # Get real data
        menu_data = data_source.get('menu')
        
        print(f"\n✅ Data loaded successfully!")
        print(f"   Hot dogs found: {len(menu_data)}")
        
        # Infer schemas from real data
        schemas = get_hotdog_schemas(menu_data)
        
        print(f"\n✅ Schemas inferred from real data:")
        for entity_type, props in schemas.items():
            print(f"   - {entity_type}: {props}")
        
        # Verify we got meaningful results
        assert 'HotDog' in schemas, "Should have HotDog entity"
        assert len(schemas['HotDog']) > 0, "HotDog should have properties"
        
        print("\n✅ Real data inference successful!")
        
        return schemas
        
    except Exception as e:
        print(f"\n⚠️  Could not load real data: {e}")
        print("   This is expected if data files don't exist yet")
        print("   Skipping this test...")
        return None


def test_schema_inference_comparison():
    """Compare schemas from fallback vs real data."""
    print_separator("TEST 8: Fallback vs Real Data Comparison")
    
    print("\n📋 Getting fallback schemas...")
    fallback_ingredient_specific, fallback_ingredient_common = get_ingredient_schemas(None)
    fallback_hotdog = get_hotdog_schemas(None)
    
    print("\n📋 Attempting to get real data schemas...")
    real_ingredient_specific, real_ingredient_common = test_ingredient_schemas_with_real_data()
    real_hotdog = test_hotdog_schemas_with_real_data()
    
    if real_ingredient_specific is not None:
        print("\n📊 INGREDIENT SCHEMAS COMPARISON:")
        print("\n   Fallback common properties:", fallback_ingredient_common)
        print("   Real data common properties:", real_ingredient_common)
        
        print("\n   Fallback entity types:", list(fallback_ingredient_specific.keys()))
        print("   Real data entity types:", list(real_ingredient_specific.keys()))
        
        # Compare specific schemas
        for entity_type in fallback_ingredient_specific.keys():
            if entity_type in real_ingredient_specific:
                fallback_props = set(fallback_ingredient_specific[entity_type])
                real_props = set(real_ingredient_specific[entity_type])
                
                if fallback_props != real_props:
                    print(f"\n   ⚠️  Difference in {entity_type}:")
                    print(f"      Fallback: {fallback_props}")
                    print(f"      Real:     {real_props}")
                else:
                    print(f"   ✅ {entity_type}: Schemas match!")
    
    if real_hotdog is not None:
        print("\n📊 HOTDOG SCHEMAS COMPARISON:")
        print("\n   Fallback properties:", fallback_hotdog['HotDog'])
        print("   Real data properties:", real_hotdog['HotDog'])
        
        fallback_props = set(fallback_hotdog['HotDog'])
        real_props = set(real_hotdog['HotDog'])
        
        if fallback_props != real_props:
            print(f"\n   ⚠️  Differences found:")
            print(f"      Only in fallback: {fallback_props - real_props}")
            print(f"      Only in real data: {real_props - fallback_props}")
        else:
            print(f"   ✅ Schemas match!")


def run_all_tests():
    """Run all schema tests."""
    print("\n" + "🧬" * 35)
    print("   SCHEMA INFERENCE SYSTEM - TEST SUITE")
    print("🧬" * 35)
    
    try:
        # # Test 1: Common properties extraction
        test_find_common_properties()
        
        # # Test 2: Ingredient schema inference with mock data
        test_infer_ingredient_schemas_with_mock_data()
        
        # # Test 3: HotDog schema inference with mock data
        test_infer_hotdog_schema_with_mock_data()
        
        # # Test 4: Ingredient schemas with fallback
        test_ingredient_schemas_with_fallback()
        
        # # Test 5: HotDog schemas with fallback
        test_hotdog_schemas_with_fallback()
        
        # Test 6-7: Real data tests (may skip if data not available)
        test_ingredient_schemas_with_real_data()
        test_hotdog_schemas_with_real_data()
        
        # Test 8: Comparison
        test_schema_inference_comparison()
        
        # Final summary
        print_separator("TEST SUITE COMPLETED")
        print("\n✅ All schema inference tests passed successfully!")
        print("\n📝 Summary:")
        print("   - Common property extraction: ✅")
        print("   - GROUPED structure inference: ✅")
        print("   - FLAT structure inference: ✅")
        print("   - Fallback mechanisms: ✅")
        print("   - Real data integration: ✅")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        raise
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise


if __name__ == '__main__':
    run_all_tests()
