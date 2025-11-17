"""
Actions package.

Exports all action functions for the CLI.

Author: Rafael Correa
Date: November 16, 2025
"""

from .ingredientes_actions import (
    action_list_by_category,
    action_list_by_type,
    action_view_inventory,
    action_update_stock,
    action_add_ingredient,
    action_delete_ingredient,
)

from .menu_actions import (
    action_list_hotdogs,
    action_check_hotdog_availability,
    action_add_hotdog,
    action_delete_hotdog,
)

from .ventas_actions import (
    action_register_sale,
    action_view_sales,
    action_view_sales_by_date,
    action_sales_statistics,
    action_simulate_day,
)

from .reporting_actions import (
    action_generate_all_charts,
    action_sales_over_time_chart,
    action_top_hotdogs_chart,
    action_sales_by_hour_chart,
    action_compare_dates_chart,
    action_general_report,
)

__all__ = [
    # Ingredientes
    'action_list_by_category',
    'action_list_by_type',
    'action_view_inventory',
    'action_update_stock',
    'action_add_ingredient',
    'action_delete_ingredient',
    
    # Menu (Hot Dogs)
    'action_list_hotdogs',
    'action_check_hotdog_availability',
    'action_add_hotdog',
    'action_delete_hotdog',
    
    # Ventas
    'action_register_sale',
    'action_view_sales',
    'action_view_sales_by_date',
    'action_sales_statistics',
    'action_simulate_day',
    
    # Reporting
    'action_generate_all_charts',
    'action_sales_over_time_chart',
    'action_top_hotdogs_chart',
    'action_sales_by_hour_chart',
    'action_compare_dates_chart',
    'action_general_report',
]
