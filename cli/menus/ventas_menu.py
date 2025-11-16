"""
Menu definition for sales management (ventas).

Author: Rafael Correa
Date: November 16, 2025
"""

from cli.core import MenuDefinition, MenuOption
from cli.actions import (
    action_register_sale,
    action_view_sales,
    action_view_sales_by_date,
    action_sales_statistics,
)


def create_ventas_menu() -> MenuDefinition:
    """
    Creates the menu for sales management.
    
    Returns:
        MenuDefinition for sales management
    """
    return MenuDefinition(
        id='ventas',
        title='💰 GESTIÓN DE VENTAS',
        description='Registra y consulta ventas',
        options=[
            MenuOption(
                key='1',
                label='Registrar venta',
                action=action_register_sale
            ),
            MenuOption(
                key='2',
                label='Ver todas las ventas',
                action=action_view_sales
            ),
            MenuOption(
                key='3',
                label='Ver ventas por fecha',
                action=action_view_sales_by_date
            ),
            MenuOption(
                key='4',
                label='Estadísticas de ventas',
                action=action_sales_statistics
            ),
        ],
        parent_menu='main',
        auto_add_back=True,
        auto_add_exit=True,
        clear_screen=True
    )
