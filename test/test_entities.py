"""
Test script for entity creation system.

Tests the dynamic entity generation, schema inference, plugin injection,
and validation composition for ingredients and hotdogs.

Author: Rafael Correa
Date: November 13, 2025
"""

import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import create_ingredient_entities, create_hotdog_entities


def test_ingredient_entities_with_fallback():
    """Test ingredient entity creation with fallback schemas."""
    print("\n" + "="*60)
    print("TEST 1: Creating ingredient entities with fallback schemas")
    print("="*60)
    
    # Create entities without raw data (uses fallback)
    # NOW RETURNS A DICT!
    entities = create_ingredient_entities()
    
    # DEBUG: Ver qué claves están disponibles
    print("\n🔍 DEBUG - Available entity types:")
    for entity_type in entities.keys():
        print(f"  - '{entity_type}'")
    
    # Extract classes from dict
    Ingredient = entities['Ingredient']
    Pan = entities['Pan']
    Salchicha = entities['Salchicha']
    Toppings = entities['Toppings']  # Note: Capitalized!
    Salsa = entities['Salsa']
    
    # DEBUG: Intentar diferentes variaciones para Acompañante
    print("\n🔍 DEBUG - Trying to find Acompañante:")
    possible_keys = ['Acompanante', 'Acompañante', 'acompanante', 'acompañante']
    acompanante_key = None
    for key in possible_keys:
        if key in entities:
            print(f"  ✅ Found as '{key}'")
            acompanante_key = key
            break
        else:
            print(f"  ❌ Not found as '{key}'")
    
    if acompanante_key is None:
        raise KeyError(f"Could not find Acompañante variant. Available keys: {list(entities.keys())}")
    
    Acompanante = entities[acompanante_key]
    
    print("\n✅ Successfully created classes:")
    print(f"  - Ingredient: {Ingredient}")
    print(f"  - Pan: {Pan}")
    print(f"  - Salchicha: {Salchicha}")
    print(f"  - Toppings: {Toppings}")
    print(f"  - Salsa: {Salsa}")
    print(f"  - Acompanante (key='{acompanante_key}'): {Acompanante}")
    
    # Test inheritance
    print("\n📋 Testing inheritance:")
    print(f"  - Pan inherits from Ingredient: {issubclass(Pan, Ingredient)}")
    print(f"  - Salchicha inherits from Ingredient: {issubclass(Salchicha, Ingredient)}")
    
    return Ingredient, Pan, Salchicha, Toppings, Salsa, Acompanante


def test_pan_instantiation(Pan):
    """Test Pan entity instantiation."""
    print("\n" + "="*60)
    print("TEST 2: Pan instantiation")
    print("="*60)
    
    # Create a Pan instance
    # Note: Schema keys are normalized (no accents)
    pan = Pan(
        id='pan-001',
        entity_type='Pan',
        nombre='baguette',
        tipo='francés',
        tamano=10,  # normalized: tamaño -> tamano
        unidad='pulgadas'
    )
    
    print(f"✅ Created Pan instance: {pan}")
    
    # Test attribute access
    print(f"\n📋 Attributes:")
    print(f"  - nombre: {pan.nombre}")
    print(f"  - tipo: {pan.tipo}")
    print(f"  - tamano: {pan.tamano}")  # normalized
    print(f"  - unidad: {pan.unidad}")
    
    # Test to_dict
    print(f"\n📦 to_dict(): {pan.to_dict()}")
    
    return pan


def test_pan_validation(Pan):
    """Test Pan validation (base + specific)."""
    print("\n" + "="*60)
    print("TEST 3: Pan validation")
    print("="*60)
    
    # Valid pan
    print("📋 Testing valid Pan:")
    valid_pan = Pan(
        id='pan-002',
        entity_type='Pan',
        nombre='integral',
        tipo='trigo',
        tamano=8,  # normalized
        unidad='pulgadas'
    )
    
    try:
        valid_pan.validate()
        print("  ✅ Validation passed")
    except ValueError as e:
        print(f"  ❌ Validation failed: {e}")
    
    # Invalid pan - missing nombre (base validation should catch)
    print("\n📋 Testing Pan without nombre (should fail base validation):")
    try:
        invalid_pan = Pan(
            id='pan-003',
            entity_type='Pan',
            nombre='',  # Empty nombre
            tipo='blanco',
            tamano=6,  # normalized
            unidad='pulgadas'
        )
        invalid_pan.validate()
        print("  ❌ Validation should have failed!")
    except ValueError as e:
        print(f"  ✅ Validation failed as expected: {e}")
    
    # Invalid pan - negative tamano (specific validation should catch)
    print("\n📋 Testing Pan with negative tamano (should fail specific validation):")
    try:
        invalid_pan2 = Pan(
            id='pan-004',
            entity_type='Pan',
            nombre='test',
            tipo='blanco',
            tamano=-5,  # Negative, normalized
            unidad='pulgadas'
        )
        invalid_pan2.validate()
        print("  ❌ Validation should have failed!")
    except ValueError as e:
        print(f"  ✅ Validation failed as expected: {e}")


def test_salchicha_matches_size(Salchicha, Pan):
    """Test Salchicha matches_size method with Pan."""
    print("\n" + "="*60)
    print("TEST 4: Salchicha matches_size with Pan")
    print("="*60)
    
    # Create salchicha and pan with matching sizes
    salchicha = Salchicha(
        id='salchicha-001',
        entity_type='Salchicha',
        nombre='chorizo',
        tipo='español',
        tamano=10,  # normalized
        unidad='pulgadas'
    )
    
    pan_matching = Pan(
        id='pan-005',
        entity_type='Pan',
        nombre='largo',
        tipo='blanco',
        tamano=10,  # normalized
        unidad='pulgadas'
    )
    
    pan_different = Pan(
        id='pan-006',
        entity_type='Pan',
        nombre='corto',
        tipo='blanco',
        tamano=6,  # normalized
        unidad='pulgadas'
    )
    
    print(f"✅ Created Salchicha (tamano=10): {salchicha.nombre}")
    print(f"✅ Created Pan matching (tamano=10): {pan_matching.nombre}")
    print(f"✅ Created Pan different (tamano=6): {pan_different.nombre}")
    
    # Test matches_size
    print(f"\n🔧 Testing matches_size method:")
    print(f"  - salchicha.matches_size(pan_matching): {salchicha.matches_size(pan_matching)}")  # Should be True
    print(f"  - salchicha.matches_size(pan_different): {salchicha.matches_size(pan_different)}")  # Should be False
    
    # Test validation
    print(f"\n📋 Testing validation:")
    try:
        salchicha.validate()
        print("  ✅ Salchicha validation passed")
    except ValueError as e:
        print(f"  ❌ Validation failed: {e}")


def test_simple_ingredients(Toppings, Salsa, Acompanante):
    """Test simpler ingredient types (Toppings, Salsa, Acompanante)."""
    print("\n" + "="*60)
    print("TEST 5: Simple ingredients (Toppings, Salsa, Acompanante)")
    print("="*60)
    
    # Toppings (capitalized and plural!)
    # Note: Toppings has 'tipo' and 'presentacion' properties
    topping = Toppings(
        id='topping-001',
        entity_type='Toppings',
        nombre='cebolla',
        tipo='vegetales',
        presentacion='picada'  # Required property!
    )
    print(f"✅ Created Toppings: {topping}")
    topping.validate()
    print("  ✅ Toppings validation passed")
    
    # Salsa
    # Note: Salsa has 'base' and 'color' properties (from fallback)
    salsa = Salsa(
        id='salsa-001',
        entity_type='Salsa',
        nombre='ketchup',
        base='tomate',
        color='rojo'
    )
    print(f"\n✅ Created Salsa: {salsa}")
    salsa.validate()
    print("  ✅ Salsa validation passed")
    
    # Acompanante (normalized: no ñ in class name)
    # Note: Acompanante has 'tipo', 'tamano', 'unidad' properties (from fallback)
    acompanante = Acompanante(
        id='acomp-001',
        entity_type='Acompanante',  # Note: normalized, no ñ
        nombre='Papas',
        tipo='fritas',
        tamano=100,  # normalized
        unidad='gramos'
    )
    print(f"\n✅ Created Acompanante: {acompanante}")
    acompanante.validate()
    print("  ✅ Acompanante validation passed")


def test_hotdog_entities():
    """Test HotDog entity creation and functionality."""
    print("\n" + "="*60)
    print("TEST 6: HotDog entity")
    print("="*60)
    
    # Create HotDog class with fallback
    # NOW RETURNS A DICT!
    entities = create_hotdog_entities()
    HotDog = entities['HotDog']
    print(f"✅ Created HotDog class: {HotDog}")
    
    # Create instance
    # Note: Keys are normalized (no accents, lowercase)
    hotdog = HotDog(
        id='hotdog-001',
        entity_type='HotDog',
        nombre='simple',
        pan='simple',  # normalized: Pan -> pan
        salchicha='weiner',  # normalized: Salchicha -> salchicha
        toppings=[],
        salsas=[],
        acompanante=None  # normalized: Acompañante -> acompanante
    )
    
    print(f"\n✅ Created HotDog instance: {hotdog}")
    
    # Test methods
    print(f"\n🔧 Testing methods:")
    print(f"  - has_toppings(): {hotdog.has_toppings()}")  # Should be False
    print(f"  - has_salsas(): {hotdog.has_salsas()}")  # Should be False
    print(f"  - is_combo(): {hotdog.is_combo()}")  # Should be False
    
    # Test with toppings and combo
    hotdog_combo = HotDog(
        id='hotdog-002',
        entity_type='HotDog',
        nombre='especial',
        pan='integral',  # normalized
        salchicha='chorizo',  # normalized
        toppings=['cebolla', 'tomate'],
        salsas=['ketchup', 'mostaza'],
        acompanante='Papas'  # normalized
    )
    
    print(f"\n✅ Created HotDog combo: {hotdog_combo}")
    print(f"  - has_toppings(): {hotdog_combo.has_toppings()}")  # Should be True
    print(f"  - has_salsas(): {hotdog_combo.has_salsas()}")  # Should be True
    print(f"  - is_combo(): {hotdog_combo.is_combo()}")  # Should be True
    
    # Test validation
    print(f"\n📋 Testing validation:")
    try:
        hotdog.validate()
        print("  ✅ HotDog validation passed")
    except ValueError as e:
        print(f"  ❌ Validation failed: {e}")
    
    # Test invalid hotdog
    print(f"\n📋 Testing invalid HotDog (empty nombre):")
    try:
        invalid_hotdog = HotDog(
            id='hotdog-003',
            entity_type='HotDog',
            nombre='',
            pan='simple',  # normalized
            salchicha='weiner',  # normalized
            toppings=[],
            salsas=[],
            acompanante=None  # normalized
        )
        invalid_hotdog.validate()
        print("  ❌ Validation should have failed!")
    except ValueError as e:
        print(f"  ✅ Validation failed as expected: {e}")


def run_all_tests():
    """Run all entity tests."""
    print("\n" + "🎯" * 30)
    print("TESTING ENTITY CREATION SYSTEM")
    print("🎯" * 30)
    
    try:
        # Test ingredients
        Ingredient, Pan, Salchicha, Toppings, Salsa, Acompanante = test_ingredient_entities_with_fallback()
        test_pan_instantiation(Pan)
        test_pan_validation(Pan)
        test_salchicha_matches_size(Salchicha, Pan)
        test_simple_ingredients(Toppings, Salsa, Acompanante)
        
        # Test hotdogs
        test_hotdog_entities()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        
    except Exception as e:
        print("\n" + "="*60)
        print(f"❌ TEST FAILED: {e}")
        print("="*60)
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_all_tests()
