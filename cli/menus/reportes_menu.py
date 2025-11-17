"""
Menu definition for reporting and charts.

Author: Rafael Correa
Date: November 16, 2025
"""

from cli.core import MenuDefinition, MenuOption
from cli.actions import (
    action_generate_all_charts,
    action_sales_over_time_chart,
    action_top_hotdogs_chart,
    action_sales_by_hour_chart,
    action_compare_dates_chart,
    action_general_report,
)


def create_reportes_menu() -> MenuDefinition:
    """
    Creates the menu for reports and charts.
    
    Returns:
        MenuDefinition for reporting
    """
    return MenuDefinition(
        id='reportes',
        title='📊 REPORTES Y GRÁFICOS',
        description='Genera reportes estadísticos y gráficos con matplotlib',
        options=[
            MenuOption(
                key='1',
                label='📈 Generar todos los gráficos',
                action=action_generate_all_charts
            ),
            MenuOption(
                key='2',
                label='📉 Gráfico: Ventas por día',
                action=action_sales_over_time_chart
            ),
            MenuOption(
                key='3',
                label='🏆 Gráfico: Hot dogs más vendidos',
                action=action_top_hotdogs_chart
            ),
            MenuOption(
                key='4',
                label='🕐 Gráfico: Distribución por hora',
                action=action_sales_by_hour_chart
            ),
            MenuOption(
                key='5',
                label='📊 Gráfico: Comparar fechas',
                action=action_compare_dates_chart
            ),
            MenuOption(
                key='6',
                label='📄 Reporte general (texto)',
                action=action_general_report
            ),
        ],
        parent_menu='main',
        auto_add_back=True,
        auto_add_exit=True,
        clear_screen=True
    )
