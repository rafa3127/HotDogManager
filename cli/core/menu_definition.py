"""
MenuDefinition - Data structures for defining menus declaratively.

Provides MenuOption and MenuDefinition classes to define CLI menus
in a declarative way, separating menu structure from routing logic.

Author: Rafael Correa
Date: November 16, 2025
"""

from dataclasses import dataclass, field
from typing import Callable, List, Optional


@dataclass
class MenuOption:
    """
    Represents a single option in a menu.
    
    An option can either:
    - Execute an action (function)
    - Navigate to another menu directly
    - Both (execute action then navigate based on result)
    
    Attributes:
        key: User input to select this option (e.g., '1', 'a', 'add')
        label: Display text for this option
        action: Function to execute when selected (optional)
        navigate_to: Menu ID to navigate to (optional, alternative to action)
        requires_confirm: If True, Router asks for confirmation before executing
        
    Examples:
        # Action-based option
        MenuOption('1', 'Add ingredient', action=action_add_ingredient)
        
        # Direct navigation option
        MenuOption('2', 'Manage menu', navigate_to='menu_management')
        
        # Action with confirmation
        MenuOption('3', 'Delete all', action=action_delete_all, requires_confirm=True)
    
    Notes:
        - If both action and navigate_to are provided, action is executed first
        - Action can return ActionResult with its own navigate_to to override
        - key is case-insensitive when matching user input
    """
    
    key: str
    label: str
    action: Optional[Callable] = None
    navigate_to: Optional[str] = None
    requires_confirm: bool = False
    
    def __post_init__(self):
        """Validates that at least action or navigate_to is provided."""
        if self.action is None and self.navigate_to is None:
            raise ValueError(
                f"MenuOption '{self.label}' must have either action or navigate_to"
            )
    
    def has_action(self) -> bool:
        """Returns True if this option executes an action."""
        return self.action is not None
    
    def has_navigation(self) -> bool:
        """Returns True if this option has direct navigation."""
        return self.navigate_to is not None


@dataclass
class MenuDefinition:
    """
    Defines a complete menu with title, options, and navigation settings.
    
    A menu is a screen that displays a title, description, and list of
    numbered/lettered options that the user can select.
    
    Attributes:
        id: Unique identifier for this menu (used for navigation)
        title: Menu title displayed at the top
        description: Optional description/subtitle
        options: List of MenuOption objects
        parent_menu: ID of parent menu (for breadcrumbs and "back")
        auto_add_back: If True, automatically adds "Back" option
        auto_add_exit: If True, automatically adds "Exit" option
        clear_screen: If True, clears screen before displaying menu
        
    Examples:
        MenuDefinition(
            id='ingredients',
            title='📦 INGREDIENT MANAGEMENT',
            description='Manage the ingredient catalog',
            options=[
                MenuOption('1', 'List by category', action=action_list),
                MenuOption('2', 'Add ingredient', action=action_add),
                MenuOption('3', 'Delete ingredient', action=action_delete, requires_confirm=True),
            ],
            parent_menu='main',
            auto_add_back=True,
            auto_add_exit=True
        )
    
    Notes:
        - id must be unique across all menus in the Router
        - If auto_add_back=True and parent_menu is set, "0" key navigates back
        - If auto_add_exit=True, "exit" or "quit" terminates the app
        - Options are displayed in the order they appear in the list
    """
    
    id: str
    title: str
    description: str = ""
    options: List[MenuOption] = field(default_factory=list)
    parent_menu: Optional[str] = None
    auto_add_back: bool = True
    auto_add_exit: bool = True
    clear_screen: bool = True
    
    def __post_init__(self):
        """Validates menu definition."""
        if not self.id:
            raise ValueError("MenuDefinition must have an id")
        
        if not self.title:
            raise ValueError("MenuDefinition must have a title")
        
        if not self.options:
            raise ValueError(f"MenuDefinition '{self.id}' must have at least one option")
        
        # Check for duplicate keys
        keys = [opt.key.lower() for opt in self.options]
        if len(keys) != len(set(keys)):
            raise ValueError(f"MenuDefinition '{self.id}' has duplicate option keys")
    
    def get_option(self, key: str) -> Optional[MenuOption]:
        """
        Finds an option by key (case-insensitive).
        
        Args:
            key: User input to match against option keys
            
        Returns:
            MenuOption if found, None otherwise
        """
        key_lower = key.lower()
        for option in self.options:
            if option.key.lower() == key_lower:
                return option
        return None
    
    def has_parent(self) -> bool:
        """Returns True if this menu has a parent menu."""
        return self.parent_menu is not None
    
    def should_clear_screen(self) -> bool:
        """Returns True if screen should be cleared before displaying."""
        return self.clear_screen
