"""
Views - I/O utilities for consistent CLI presentation.

Provides helper methods for user input, output formatting, tables,
and screen management with consistent styling and colors.

Author: Rafael Correa
Date: November 16, 2025
"""

import os
from typing import List, Optional, Any
from .colors import Colors


class Views:
    """
    Utilities for input/output with consistent formatting.
    
    All methods are static - no need to instantiate.
    Handles user prompts, validation, tables, and visual formatting.
    
    Usage:
        Views.clear_screen()
        Views.print_header("Main Menu")
        name = Views.prompt("Enter name: ")
        age = Views.prompt_int("Enter age: ", min_val=0, max_val=120)
        confirmed = Views.confirm("Continue?")
    """
    
    # ──────────────────────────────────────────────────────
    # Screen Management
    # ──────────────────────────────────────────────────────
    
    @staticmethod
    def clear_screen():
        """Clears the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    # ──────────────────────────────────────────────────────
    # Headers and Separators
    # ──────────────────────────────────────────────────────
    
    @staticmethod
    def print_header(title: str, subtitle: str = "", width: int = 60):
        """
        Prints a formatted header with title and optional subtitle.
        
        Args:
            title: Main title text
            subtitle: Optional subtitle text
            width: Width of the header box
            
        Example:
            Views.print_header("🌭 MAIN MENU", "Hot Dog Management System")
        """
        print("\n" + Colors.bold("=" * width))
        print(Colors.bold(f"  {title}"))
        if subtitle:
            print(Colors.blue(f"  {subtitle}"))
        print(Colors.bold("=" * width) + "\n")
    
    @staticmethod
    def print_separator(width: int = 60, char: str = "─"):
        """
        Prints a horizontal separator line.
        
        Args:
            width: Width of the separator
            char: Character to use for the line
        """
        print(char * width)
    
    # ──────────────────────────────────────────────────────
    # Messages (Success, Error, Warning, Info)
    # ──────────────────────────────────────────────────────
    
    @staticmethod
    def print_success(message: str):
        """Prints a success message in green."""
        print(Colors.green(f"✅ {message}"))
    
    @staticmethod
    def print_error(message: str):
        """Prints an error message in red."""
        print(Colors.red(f"❌ {message}"))
    
    @staticmethod
    def print_warning(message: str):
        """Prints a warning message in yellow."""
        print(Colors.yellow(f"⚠️  {message}"))
    
    @staticmethod
    def print_info(message: str):
        """Prints an info message in cyan."""
        print(Colors.info(f"ℹ️  {message}"))
    
    # ──────────────────────────────────────────────────────
    # User Input - Basic
    # ──────────────────────────────────────────────────────
    
    @staticmethod
    def prompt(
        message: str,
        choices: Optional[List[str]] = None,
        default: Optional[str] = None
    ) -> str:
        """
        Prompts user for text input with optional validation.
        
        Args:
            message: Prompt message to display
            choices: Optional list of valid choices (case-insensitive)
            default: Default value if user presses Enter
            
        Returns:
            User's input (validated if choices provided)
            
        Example:
            category = Views.prompt("Category: ", choices=['Pan', 'Salchicha'])
            name = Views.prompt("Name: ", default="simple")
        """
        while True:
            # Show default in prompt if provided
            prompt_text = message
            if default:
                prompt_text = f"{message}[{default}] "
            
            user_input = input(prompt_text).strip()
            
            # Use default if empty
            if not user_input and default:
                return default
            
            # Validate against choices if provided
            if choices:
                if user_input.lower() in [choice.lower() for choice in choices]:
                    # Return the choice with original case
                    for choice in choices:
                        if choice.lower() == user_input.lower():
                            return choice
                else:
                    Views.print_error(f"Invalid choice. Options: {', '.join(choices)}")
                    continue
            
            # No validation needed or validation passed
            if user_input:
                return user_input
            else:
                Views.print_error("Input cannot be empty")
    
    @staticmethod
    def prompt_int(
        message: str,
        min_val: Optional[int] = None,
        max_val: Optional[int] = None,
        default: Optional[int] = None
    ) -> int:
        """
        Prompts user for integer input with optional range validation.
        
        Args:
            message: Prompt message to display
            min_val: Minimum allowed value (inclusive)
            max_val: Maximum allowed value (inclusive)
            default: Default value if user presses Enter
            
        Returns:
            User's input as integer (validated if min/max provided)
            
        Example:
            age = Views.prompt_int("Age: ", min_val=0, max_val=120)
            quantity = Views.prompt_int("Quantity: ", min_val=1, default=1)
        """
        while True:
            # Show default and range in prompt
            prompt_text = message
            if default is not None:
                prompt_text = f"{message}[{default}] "
            
            user_input = input(prompt_text).strip()
            
            # Use default if empty
            if not user_input and default is not None:
                return default
            
            # Try to convert to int
            try:
                value = int(user_input)
            except ValueError:
                Views.print_error("Please enter a valid number")
                continue
            
            # Validate range
            if min_val is not None and value < min_val:
                Views.print_error(f"Value must be at least {min_val}")
                continue
            
            if max_val is not None and value > max_val:
                Views.print_error(f"Value must be at most {max_val}")
                continue
            
            return value
    
    @staticmethod
    def confirm(message: str, default: bool = False) -> bool:
        """
        Asks user for yes/no confirmation.
        
        Args:
            message: Confirmation question
            default: Default value if user presses Enter
            
        Returns:
            True if user confirms, False otherwise
            
        Example:
            if Views.confirm("Delete this item?"):
                delete_item()
        """
        default_text = "Y/n" if default else "y/N"
        prompt_text = f"{message} ({default_text}): "
        
        while True:
            user_input = input(prompt_text).strip().lower()
            
            if not user_input:
                return default
            
            if user_input in ['y', 'yes', 's', 'si', 'sí']:
                return True
            elif user_input in ['n', 'no']:
                return False
            else:
                Views.print_error("Please answer 'y' or 'n'")
    
    # ──────────────────────────────────────────────────────
    # Tables
    # ──────────────────────────────────────────────────────
    
    @staticmethod
    def display_table(
        headers: List[str],
        rows: List[List[Any]],
        col_widths: Optional[List[int]] = None
    ):
        """
        Displays a formatted table with headers and rows.
        
        Args:
            headers: Column headers
            rows: List of rows (each row is a list of values)
            col_widths: Optional custom column widths (auto-calculated if None)
            
        Example:
            Views.display_table(
                headers=['ID', 'Name', 'Stock'],
                rows=[
                    ['1', 'Pan simple', '100'],
                    ['2', 'Salchicha', '75'],
                ]
            )
        """
        if not rows:
            Views.print_warning("No data to display")
            return
        
        # Auto-calculate column widths if not provided
        if col_widths is None:
            col_widths = []
            for i, header in enumerate(headers):
                max_width = len(str(header))
                for row in rows:
                    if i < len(row):
                        max_width = max(max_width, len(str(row[i])))
                col_widths.append(max_width + 2)  # Add padding
        
        # Print header
        header_row = "  ".join(
            Colors.bold(str(header).ljust(width))
            for header, width in zip(headers, col_widths)
        )
        print(header_row)
        
        # Print separator
        separator = "  ".join("─" * width for width in col_widths)
        print(separator)
        
        # Print rows
        for row in rows:
            row_str = "  ".join(
                str(row[i] if i < len(row) else "").ljust(width)
                for i, width in enumerate(col_widths)
            )
            print(row_str)
    
    # ──────────────────────────────────────────────────────
    # Pause
    # ──────────────────────────────────────────────────────
    
    @staticmethod
    def pause(message: str = "Press Enter to continue..."):
        """
        Pauses execution until user presses Enter.
        
        Args:
            message: Message to display while waiting
        """
        input(f"\n{Colors.gray(message)}")
