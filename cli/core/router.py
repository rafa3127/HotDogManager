"""
MenuRouter - Main orchestrator for CLI navigation and action execution.

The Router manages the entire CLI lifecycle:
- Menu registration and navigation
- User input handling
- Action execution
- Navigation stack (breadcrumbs, back navigation)
- Shared context between actions

Author: Rafael Correa
Date: November 16, 2025
"""

from typing import Dict, Optional, List, Any
from .menu_definition import MenuDefinition, MenuOption
from .action_result import ActionResult
from .views import Views
from .colors import Colors
import time


class MenuRouter:
    """
    Orchestrates CLI menu navigation and action execution.
    
    The Router is the central component that:
    - Stores all registered menus
    - Manages navigation stack (for back/breadcrumbs)
    - Executes actions with shared context
    - Handles automatic options (back, exit)
    - Runs the main event loop
    
    Usage:
        router = MenuRouter()
        router.context['handler'] = data_handler
        
        router.register_menu(main_menu)
        router.register_menu(ingredients_menu)
        
        router.navigate_to('main')
        router.run()
    
    Attributes:
        menus: Dictionary of registered menus {menu_id: MenuDefinition}
        current_menu: Currently active menu ID
        navigation_stack: Stack of menu IDs for back navigation
        context: Shared dictionary available to all actions
        running: Whether the main loop is active
    """
    
    def __init__(self):
        """Initializes an empty router."""
        self.menus: Dict[str, MenuDefinition] = {}
        self.current_menu: Optional[str] = None
        self.navigation_stack: List[str] = []
        self.context: Dict[str, Any] = {}
        self.running: bool = False
    
    # ──────────────────────────────────────────────────────
    # Menu Registration
    # ──────────────────────────────────────────────────────
    
    def register_menu(self, menu: MenuDefinition):
        """
        Registers a menu in the router.
        
        Args:
            menu: MenuDefinition to register
            
        Raises:
            ValueError: If menu ID already exists
        """
        if menu.id in self.menus:
            raise ValueError(f"Menu '{menu.id}' is already registered")
        
        self.menus[menu.id] = menu
    
    def get_menu(self, menu_id: str) -> Optional[MenuDefinition]:
        """
        Gets a registered menu by ID.
        
        Args:
            menu_id: Menu identifier
            
        Returns:
            MenuDefinition if found, None otherwise
        """
        return self.menus.get(menu_id)
    
    # ──────────────────────────────────────────────────────
    # Navigation
    # ──────────────────────────────────────────────────────
    
    def navigate_to(self, menu_id: str, add_to_stack: bool = True):
        """
        Navigates to a specific menu.
        
        If menu doesn't exist, navigates to 404 page instead.
        
        Args:
            menu_id: Menu to navigate to
            add_to_stack: If True, adds current menu to navigation stack
        """
        # If menu doesn't exist, go to 404 page
        if menu_id not in self.menus:
            # Only navigate to 404 if it exists and we're not already there
            if '404' in self.menus and menu_id != '404':
                Views.print_warning(f"Menu '{menu_id}' not found. Redirecting to 404 page...")
                
                time.sleep(3)
                # Add current menu to stack before going to 404
                if add_to_stack and self.current_menu:
                    self.navigation_stack.append(self.current_menu)
                self.current_menu = '404'
                return
            else:
                # 404 doesn't exist, raise error (shouldn't happen in production)
                raise ValueError(f"Menu '{menu_id}' not found and no 404 page available")
        
        # Add current menu to stack (for back navigation)
        if add_to_stack and self.current_menu:
            self.navigation_stack.append(self.current_menu)
        
        self.current_menu = menu_id
    
    def go_back(self) -> bool:
        """
        Goes back to previous menu in navigation stack.
        
        Returns:
            True if went back successfully, False if stack is empty
        """
        if not self.navigation_stack:
            return False
        
        previous_menu = self.navigation_stack.pop()
        self.current_menu = previous_menu
        return True
    
    def go_to_parent(self) -> bool:
        """
        Goes to parent menu (from MenuDefinition.parent_menu).
        
        Returns:
            True if went to parent, False if current menu has no parent
        """
        if not self.current_menu:
            return False
        
        menu = self.menus[self.current_menu]
        if not menu.has_parent():
            return False
        
        self.navigate_to(menu.parent_menu, add_to_stack=False)
        return True
    
    # ──────────────────────────────────────────────────────
    # Menu Display
    # ──────────────────────────────────────────────────────
    
    def display_menu(self, menu: MenuDefinition):
        """
        Displays a menu with all its options.
        
        Args:
            menu: Menu to display
        """
        # Clear screen if menu requests it
        if menu.should_clear_screen():
            Views.clear_screen()
        
        # Display header
        Views.print_header(menu.title, menu.description)
        
        # Display options
        for option in menu.options:
            print(f"  {Colors.cyan(option.key)}. {option.label}")
        
        # Display automatic options
        if menu.auto_add_back and menu.has_parent():
            print(f"  {Colors.gray('0. Back')}")
        
        if menu.auto_add_exit:
            print(f"  {Colors.gray('exit. Exit application')}")
        
        print()  # Empty line after menu
    
    # ──────────────────────────────────────────────────────
    # User Input
    # ──────────────────────────────────────────────────────
    
    def get_user_choice(self, menu: MenuDefinition) -> Optional[str]:
        """
        Gets and validates user input for menu selection.
        
        Args:
            menu: Current menu
            
        Returns:
            Valid option key, or None for special commands (back, exit)
        """
        user_input = input(Colors.bold("Select option: ")).strip().lower()
        
        # Handle exit
        if user_input in ['exit', 'quit', 'q']:
            return 'exit'
        
        # Handle back
        if user_input == '0' and menu.auto_add_back and menu.has_parent():
            return 'back'
        
        # Validate against menu options
        option = menu.get_option(user_input)
        if option:
            return user_input
        
        # Invalid option
        Views.print_error("Invalid option. Please try again.")
        Views.pause()
        return None
    
    # ──────────────────────────────────────────────────────
    # Action Execution
    # ──────────────────────────────────────────────────────
    
    def execute_option(self, menu: MenuDefinition, option: MenuOption) -> ActionResult:
        """
        Executes a menu option (action or navigation).
        
        Args:
            menu: Current menu
            option: Selected option
            
        Returns:
            ActionResult from the action, or success result for navigation
        """
        # Handle confirmation if required
        if option.requires_confirm:
            if not Views.confirm(f"Are you sure you want to '{option.label}'?"):
                Views.print_warning("Operation cancelled")
                Views.pause()
                return ActionResult.success()
        
        # Execute action if present
        if option.has_action():
            # Add router to context (so actions can navigate)
            self.context['router'] = self
            
            try:
                result = option.action(self.context)
                
                # Display result message if present
                if result.message:
                    if result.success:
                        Views.print_success(result.message)
                    else:
                        Views.print_error(result.message)
                
                return result
                
            except Exception as e:
                Views.print_error(f"Error executing action: {e}")
                import traceback
                traceback.print_exc()
                Views.pause()
                return ActionResult.error(str(e))
        
        # Direct navigation (no action)
        elif option.has_navigation():
            return ActionResult.success(navigate_to=option.navigate_to)
        
        # Should never happen (MenuOption validates this)
        return ActionResult.success()
    
    # ──────────────────────────────────────────────────────
    # Main Event Loop
    # ──────────────────────────────────────────────────────
    
    def run(self):
        """
        Starts the main CLI event loop.
        
        This is the entry point for the CLI application.
        Continues running until:
        - User selects exit
        - An action returns ActionResult.exit()
        - KeyboardInterrupt (Ctrl+C)
        
        Raises:
            RuntimeError: If no menus are registered or current_menu is not set
        """
        if not self.menus:
            raise RuntimeError("No menus registered. Call register_menu() first.")
        
        if not self.current_menu:
            raise RuntimeError("No current menu. Call navigate_to() first.")
        
        self.running = True
        
        try:
            while self.running:
                # Get current menu
                menu = self.menus[self.current_menu]
                
                # Display menu
                self.display_menu(menu)
                
                # Get user choice
                choice = self.get_user_choice(menu)
                
                if choice is None:
                    # Invalid input, loop continues
                    continue
                
                # Handle exit
                if choice == 'exit':
                    if Views.confirm("Exit application?", default=False):
                        Views.print_info("Goodbye! 👋")
                        self.running = False
                    continue
                
                # Handle back
                if choice == 'back':
                    self.go_to_parent()
                    continue
                
                # Execute option
                option = menu.get_option(choice)
                result = self.execute_option(menu, option)
                
                # Handle result
                if result.should_exit():
                    Views.print_info(result.message or "Goodbye! 👋")
                    self.running = False
                
                elif result.should_navigate():
                    self.navigate_to(result.navigate_to)
        
        except KeyboardInterrupt:
            print("\n")
            Views.print_warning("Interrupted by user")
            Views.print_info("Goodbye! 👋")
        
        except Exception as e:
            Views.print_error(f"Critical error: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    # ──────────────────────────────────────────────────────
    # Utilities
    # ──────────────────────────────────────────────────────
    
    def stop(self):
        """Stops the main event loop."""
        self.running = False
    
    def get_breadcrumbs(self) -> List[str]:
        """
        Returns the navigation path (breadcrumbs).
        
        Returns:
            List of menu IDs from root to current
        """
        breadcrumbs = self.navigation_stack.copy()
        if self.current_menu:
            breadcrumbs.append(self.current_menu)
        return breadcrumbs
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"MenuRouter("
            f"menus={len(self.menus)}, "
            f"current='{self.current_menu}', "
            f"stack={self.navigation_stack})"
        )
