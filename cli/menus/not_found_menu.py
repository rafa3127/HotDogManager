"""
404 Not Found menu - Fallback for non-existent routes.

This menu is displayed when navigation is attempted to a menu that
doesn't exist. After 5 seconds, it automatically returns to the previous menu.

Author: Rafael Correa
Date: November 16, 2025
"""

import time
from cli.core import MenuDefinition, MenuOption, ActionResult, Views


def action_go_back(context: dict) -> ActionResult:
    """
    Goes back to previous menu immediately.
    
    Args:
        context: Router context
        
    Returns:
        ActionResult that navigates back
    """
    router = context.get('router')
    if router and router.go_back():
        return ActionResult.success()
    else:
        # If can't go back, navigate to main
        return ActionResult.success(navigate_to='main')


def action_wait_and_return(context: dict) -> ActionResult:
    """
    Waits 5 seconds and returns to previous menu.
    
    Args:
        context: Router context
        
    Returns:
        ActionResult that navigates back
    """
    Views.print_info("Volviendo al menú anterior en 5 segundos...")
    
    # Countdown
    for i in range(5, 0, -1):
        print(f"  {i}...", end='\r')
        time.sleep(1)
    
    print()  # New line after countdown
    
    # Navigate back using router
    router = context.get('router')
    if router and router.go_back():
        return ActionResult.success()
    else:
        # If can't go back, navigate to main
        return ActionResult.success(navigate_to='main')


def create_not_found_menu() -> MenuDefinition:
    """
    Creates the 404 Not Found menu.
    
    This menu is shown when navigation is attempted to a non-existent menu.
    It automatically returns to the previous menu after 5 seconds.
    
    Returns:
        MenuDefinition for the 404 page
    """
    return MenuDefinition(
        id='404',
        title='❌ PÁGINA NO ENCONTRADA',
        description='La opción seleccionada aún no ha sido implementada',
        options=[
            MenuOption(
                key='1',
                label='↩️  Volver a menú anterior',
                action=action_go_back
            ),
        ],
        parent_menu='main',  # Default parent is main
        auto_add_back=False,  # We handle back manually
        auto_add_exit=True,
        clear_screen=True
    )
