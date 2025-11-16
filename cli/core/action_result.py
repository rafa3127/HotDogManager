"""
ActionResult - Data structure for action execution results.

Allows actions to communicate with the Router about what to do next:
- Continue in current menu
- Navigate to another menu
- Exit the application

Author: Rafael Correa
Date: November 16, 2025
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ActionResult:
    """
    Result of an action execution.
    
    The Router uses this object to decide what to do after executing
    an action (return to menu, navigate to another, exit, etc.)
    
    Attributes:
        success: Whether the action completed successfully
        message: Optional message (error, success, info)
        navigate_to: Menu ID to navigate to (None = return to current menu)
        exit_app: If True, the Router terminates the application
        data: Additional data the action wants to return
    
    Examples:
        # Simple success (returns to menu)
        return ActionResult.success()
        
        # Success with message
        return ActionResult.success("Ingredient added")
        
        # Success and navigate to another menu
        return ActionResult.success(navigate_to='edit_ingredient')
        
        # Error
        return ActionResult.error("Duplicate name")
        
        # Exit application
        return ActionResult.exit()
    """
    
    success: bool
    message: str = ""
    navigate_to: Optional[str] = None
    exit_app: bool = False
    data: Optional[dict] = None
    
    # ──────────────────────────────────────────────────────
    # Factory Methods (convenient constructors)
    # ──────────────────────────────────────────────────────
    
    @classmethod
    def success(
        cls,
        message: str = "",
        navigate_to: Optional[str] = None,
        data: Optional[dict] = None
    ) -> 'ActionResult':
        """
        Creates a successful result.
        
        Args:
            message: Optional success message
            navigate_to: Menu to navigate to afterwards
            data: Additional data
        
        Returns:
            ActionResult with success=True
        """
        return cls(
            success=True,
            message=message,
            navigate_to=navigate_to,
            data=data
        )
    
    @classmethod
    def error(
        cls,
        message: str,
        data: Optional[dict] = None
    ) -> 'ActionResult':
        """
        Creates an error result.
        
        Args:
            message: Error message (required)
            data: Additional error data
        
        Returns:
            ActionResult with success=False
        """
        return cls(
            success=False,
            message=message,
            data=data
        )
    
    @classmethod
    def exit(cls, message: str = "Goodbye!") -> 'ActionResult':
        """
        Creates a result that terminates the application.
        
        Args:
            message: Farewell message
        
        Returns:
            ActionResult with exit_app=True
        """
        return cls(
            success=True,
            message=message,
            exit_app=True
        )
    
    # ──────────────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────────────
    
    def should_navigate(self) -> bool:
        """Returns True if navigation to another menu is needed."""
        return self.navigate_to is not None
    
    def should_exit(self) -> bool:
        """Returns True if application should exit."""
        return self.exit_app
