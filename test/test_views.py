"""
Test script for Views utilities.

This is an interactive test - run it to see how the Views work in practice.

Author: Rafael Correa
Date: November 16, 2025
"""

from cli.core.views import Views


def test_screen_management():
    """Test screen management utilities."""
    Views.print_header("TEST: Screen Management")
    
    print("This text will be cleared in 2 seconds...")
    import time
    time.sleep(2)
    
    Views.clear_screen()
    Views.print_success("Screen cleared!")
    Views.pause()


def test_headers_and_separators():
    """Test headers and separators."""
    Views.clear_screen()
    Views.print_header("TEST: Headers and Separators")
    
    Views.print_header("🌭 MAIN TITLE", "This is a subtitle")
    
    Views.print_separator()
    print("Content between separators")
    Views.print_separator(width=40, char="=")
    
    Views.pause()


def test_messages():
    """Test different message types."""
    Views.clear_screen()
    Views.print_header("TEST: Messages")
    
    Views.print_success("This is a success message")
    Views.print_error("This is an error message")
    Views.print_warning("This is a warning message")
    Views.print_info("This is an info message")
    
    Views.pause()


def test_basic_prompts():
    """Test basic text input."""
    Views.clear_screen()
    Views.print_header("TEST: Basic Prompts", "Interactive test - please provide inputs")
    
    # Simple prompt
    name = Views.prompt("Enter your name: ")
    Views.print_success(f"Hello, {name}!")
    
    # Prompt with default
    city = Views.prompt("Enter city: ", default="Caracas")
    Views.print_info(f"City: {city}")
    
    # Prompt with choices
    category = Views.prompt(
        "Select category: ",
        choices=['Pan', 'Salchicha', 'Topping']
    )
    Views.print_success(f"Selected: {category}")
    
    Views.pause()


def test_integer_prompts():
    """Test integer input with validation."""
    Views.clear_screen()
    Views.print_header("TEST: Integer Prompts")
    
    # Simple integer
    age = Views.prompt_int("Enter age: ", min_val=0, max_val=120)
    Views.print_info(f"Age: {age}")
    
    # Integer with default
    quantity = Views.prompt_int("Enter quantity: ", min_val=1, default=1)
    Views.print_success(f"Quantity: {quantity}")
    
    Views.pause()


def test_confirmations():
    """Test confirmation dialogs."""
    Views.clear_screen()
    Views.print_header("TEST: Confirmations")
    
    # Default = No
    result1 = Views.confirm("Delete this item?", default=False)
    if result1:
        Views.print_warning("Item deleted")
    else:
        Views.print_info("Deletion cancelled")
    
    # Default = Yes
    result2 = Views.confirm("Continue?", default=True)
    if result2:
        Views.print_success("Continuing...")
    else:
        Views.print_info("Stopped")
    
    Views.pause()


def test_tables():
    """Test table display."""
    Views.clear_screen()
    Views.print_header("TEST: Tables")
    
    # Sample data
    headers = ['ID', 'Name', 'Category', 'Stock']
    rows = [
        ['1', 'Pan simple', 'Pan', '100'],
        ['2', 'Pan integral', 'Pan', '45'],
        ['3', 'Salchicha weiner', 'Salchicha', '0'],
        ['4', 'Topping cebolla', 'Topping', '200'],
    ]
    
    Views.display_table(headers, rows)
    
    # Empty table
    print("\nEmpty table:")
    Views.display_table(['Col1', 'Col2'], [])
    
    Views.pause()


def main():
    """Run all tests."""
    print("This is an interactive test suite for Views utilities.")
    print("You'll be prompted to provide inputs for testing.\n")
    
    if not Views.confirm("Run tests?", default=True):
        print("Cancelled")
        return
    
    test_screen_management()
    test_headers_and_separators()
    test_messages()
    test_basic_prompts()
    test_integer_prompts()
    test_confirmations()
    test_tables()
    
    Views.clear_screen()
    Views.print_header("✅ ALL TESTS COMPLETED")
    Views.print_success("All Views utilities work correctly!")


if __name__ == "__main__":
    main()
