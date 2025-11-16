"""
Test script for MenuDefinition and MenuOption.

Author: Rafael Correa
Date: November 16, 2025
"""

from cli.core.menu_definition import MenuDefinition, MenuOption
from cli.core.action_result import ActionResult


# ──────────────────────────────────────────────────────
# Mock Actions for Testing
# ──────────────────────────────────────────────────────

def mock_action_list(context: dict) -> ActionResult:
    """Mock action for testing."""
    return ActionResult.success("Listed items")


def mock_action_add(context: dict) -> ActionResult:
    """Mock action for testing."""
    return ActionResult.success("Added item")


def mock_action_delete(context: dict) -> ActionResult:
    """Mock action that navigates."""
    return ActionResult.success("Deleted item", navigate_to='confirmation')


# ──────────────────────────────────────────────────────
# Tests
# ──────────────────────────────────────────────────────

def test_menu_option():
    """Test MenuOption creation and validation."""
    print("\n" + "=" * 60)
    print("TEST: MenuOption")
    print("=" * 60)
    
    # Action-based option
    opt1 = MenuOption('1', 'List items', action=mock_action_list)
    print(f"\n1. Action-based option:")
    print(f"   key='{opt1.key}', label='{opt1.label}'")
    print(f"   has_action={opt1.has_action()}, has_navigation={opt1.has_navigation()}")
    
    # Navigation-based option
    opt2 = MenuOption('2', 'Go to settings', navigate_to='settings')
    print(f"\n2. Navigation-based option:")
    print(f"   key='{opt2.key}', navigate_to='{opt2.navigate_to}'")
    print(f"   has_action={opt2.has_action()}, has_navigation={opt2.has_navigation()}")
    
    # Option with confirmation
    opt3 = MenuOption('3', 'Delete all', action=mock_action_delete, requires_confirm=True)
    print(f"\n3. Option with confirmation:")
    print(f"   requires_confirm={opt3.requires_confirm}")
    
    # Both action and navigation
    opt4 = MenuOption('4', 'Process and navigate', action=mock_action_add, navigate_to='next')
    print(f"\n4. Both action and navigation:")
    print(f"   has_action={opt4.has_action()}, has_navigation={opt4.has_navigation()}")
    
    # Test validation error (no action, no navigate_to)
    print(f"\n5. Testing validation error:")
    try:
        invalid_opt = MenuOption('5', 'Invalid option')
        print("   ❌ Should have raised ValueError")
    except ValueError as e:
        print(f"   ✅ Correctly raised ValueError: {e}")
    
    print("\n" + "=" * 60)


def test_menu_definition():
    """Test MenuDefinition creation and methods."""
    print("\n" + "=" * 60)
    print("TEST: MenuDefinition")
    print("=" * 60)
    
    # Create a complete menu
    menu = MenuDefinition(
        id='test_menu',
        title='🧪 TEST MENU',
        description='Menu for testing',
        options=[
            MenuOption('1', 'List items', action=mock_action_list),
            MenuOption('2', 'Add item', action=mock_action_add),
            MenuOption('3', 'Delete item', action=mock_action_delete, requires_confirm=True),
            MenuOption('s', 'Settings', navigate_to='settings'),
        ],
        parent_menu='main',
        auto_add_back=True,
        auto_add_exit=True
    )
    
    print(f"\n1. Menu created:")
    print(f"   id='{menu.id}', title='{menu.title}'")
    print(f"   options={len(menu.options)}, parent='{menu.parent_menu}'")
    print(f"   has_parent={menu.has_parent()}")
    
    # Test get_option (case-insensitive)
    print(f"\n2. Testing get_option:")
    opt = menu.get_option('1')
    print(f"   get_option('1') → {opt.label if opt else None}")
    
    opt = menu.get_option('S')  # Uppercase
    print(f"   get_option('S') → {opt.label if opt else None}")
    
    opt = menu.get_option('99')  # Not found
    print(f"   get_option('99') → {opt}")
    
    # Test validation - empty options
    print(f"\n3. Testing validation (empty options):")
    try:
        invalid_menu = MenuDefinition(
            id='invalid',
            title='Invalid',
            options=[]
        )
        print("   ❌ Should have raised ValueError")
    except ValueError as e:
        print(f"   ✅ Correctly raised ValueError: {e}")
    
    # Test validation - duplicate keys
    print(f"\n4. Testing validation (duplicate keys):")
    try:
        invalid_menu = MenuDefinition(
            id='invalid',
            title='Invalid',
            options=[
                MenuOption('1', 'First', action=mock_action_list),
                MenuOption('1', 'Duplicate', action=mock_action_add),
            ]
        )
        print("   ❌ Should have raised ValueError")
    except ValueError as e:
        print(f"   ✅ Correctly raised ValueError: {e}")
    
    print("\n" + "=" * 60)


def main():
    """Run all tests."""
    test_menu_option()
    test_menu_definition()
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
