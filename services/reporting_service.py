"""
Reporting service for sales analytics and statistics.

This service generates statistical data ready for visualization
with matplotlib or other reporting tools.

Author: Rafael Correa
Date: November 16, 2025
"""

from typing import Dict, List, Tuple
from datetime import datetime
from collections import Counter


class ReportingService:
    """
    Service for generating sales reports and statistics.
    
    All methods are static and receive the handler as parameter.
    """
    
    # ──────────────────────────────────────────────────────
    # SALES OVER TIME
    # ──────────────────────────────────────────────────────
    
    @staticmethod
    def get_sales_by_date(handler) -> Dict[str, int]:
        """
        Get total sales grouped by date.
        
        Args:
            handler: DataHandler instance
            
        Returns:
            Dict mapping date (YYYY-MM-DD) to number of sales
            Example: {'2024-11-16': 15, '2024-11-17': 23}
        """
        ventas = handler.ventas.get_all()
        
        sales_by_date = {}
        
        for venta in ventas:
            # Extract date from datetime (YYYY-MM-DDTHH:MM:SS -> YYYY-MM-DD)
            fecha = venta.fecha.split('T')[0]
            
            sales_by_date[fecha] = sales_by_date.get(fecha, 0) + 1
        
        # Sort by date
        return dict(sorted(sales_by_date.items()))
    
    @staticmethod
    def get_hotdogs_sold_by_date(handler) -> Dict[str, int]:
        """
        Get total hot dogs sold grouped by date.
        
        Args:
            handler: DataHandler instance
            
        Returns:
            Dict mapping date to total hot dogs sold
            Example: {'2024-11-16': 45, '2024-11-17': 67}
        """
        ventas = handler.ventas.get_all()
        
        hotdogs_by_date = {}
        
        for venta in ventas:
            fecha = venta.fecha.split('T')[0]
            
            # Sum quantities of all items in this sale
            total_items = sum(item['cantidad'] for item in venta.items)
            
            hotdogs_by_date[fecha] = hotdogs_by_date.get(fecha, 0) + total_items
        
        # Sort by date
        return dict(sorted(hotdogs_by_date.items()))
    
    # ──────────────────────────────────────────────────────
    # TOP PRODUCTS
    # ──────────────────────────────────────────────────────
    
    @staticmethod
    def get_top_hotdogs(handler, limit: int = 10) -> List[Tuple[str, int]]:
        """
        Get top N most sold hot dogs.
        
        Args:
            handler: DataHandler instance
            limit: Maximum number of results (default: 10)
            
        Returns:
            List of tuples (hotdog_name, quantity_sold) sorted by quantity DESC
            Example: [('simple', 125), ('combo', 98), ...]
        """
        ventas = handler.ventas.get_all()
        
        hotdog_counts = {}
        
        for venta in ventas:
            for item in venta.items:
                hotdog_nombre = item['hotdog_nombre']
                cantidad = item['cantidad']
                hotdog_counts[hotdog_nombre] = hotdog_counts.get(hotdog_nombre, 0) + cantidad
        
        # Sort by quantity (descending) and limit
        sorted_hotdogs = sorted(hotdog_counts.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_hotdogs[:limit]
    
    @staticmethod
    def get_ingredient_consumption(handler) -> Dict[str, int]:
        """
        Calculate total consumption of each ingredient.
        
        Goes through all sales and counts how many times each ingredient
        was used (considering quantities).
        
        Args:
            handler: DataHandler instance
            
        Returns:
            Dict mapping ingredient_name to total quantity consumed
            Example: {'pan simple': 150, 'salchicha weiner': 120, ...}
        """
        ventas = handler.ventas.get_all()
        
        ingredient_consumption = {}
        
        for venta in ventas:
            for item in venta.items:
                # Get the hot dog
                hotdog = handler.menu.get(item['hotdog_id'])
                
                if not hotdog:
                    continue
                
                cantidad_vendida = item['cantidad']
                
                # Count pan
                if hasattr(hotdog, 'pan') and hotdog.pan:
                    pan_nombre = hotdog.pan.get('nombre') if isinstance(hotdog.pan, dict) else hotdog.pan
                    key = f"Pan: {pan_nombre}"
                    ingredient_consumption[key] = ingredient_consumption.get(key, 0) + cantidad_vendida
                
                # Count salchicha
                if hasattr(hotdog, 'salchicha') and hotdog.salchicha:
                    salchicha_nombre = hotdog.salchicha.get('nombre') if isinstance(hotdog.salchicha, dict) else hotdog.salchicha
                    key = f"Salchicha: {salchicha_nombre}"
                    ingredient_consumption[key] = ingredient_consumption.get(key, 0) + cantidad_vendida
                
                # Count toppings
                if hasattr(hotdog, 'toppings') and hotdog.toppings:
                    for topping in hotdog.toppings:
                        topping_nombre = topping.get('nombre') if isinstance(topping, dict) else topping
                        key = f"Topping: {topping_nombre}"
                        ingredient_consumption[key] = ingredient_consumption.get(key, 0) + cantidad_vendida
                
                # Count salsas
                if hasattr(hotdog, 'salsas') and hotdog.salsas:
                    for salsa in hotdog.salsas:
                        salsa_nombre = salsa.get('nombre') if isinstance(salsa, dict) else salsa
                        key = f"Salsa: {salsa_nombre}"
                        ingredient_consumption[key] = ingredient_consumption.get(key, 0) + cantidad_vendida
                
                # Count acompañante
                if hasattr(hotdog, 'acompanante') and hotdog.acompanante:
                    acomp_nombre = hotdog.acompanante.get('nombre') if isinstance(hotdog.acompanante, dict) else hotdog.acompanante
                    key = f"Acompañante: {acomp_nombre}"
                    ingredient_consumption[key] = ingredient_consumption.get(key, 0) + cantidad_vendida
        
        # Sort by consumption (descending)
        return dict(sorted(ingredient_consumption.items(), key=lambda x: x[1], reverse=True))
    
    # ──────────────────────────────────────────────────────
    # TIME-BASED ANALYSIS
    # ──────────────────────────────────────────────────────
    
    @staticmethod
    def get_sales_by_hour(handler) -> Dict[int, int]:
        """
        Get sales distribution by hour of day.
        
        Args:
            handler: DataHandler instance
            
        Returns:
            Dict mapping hour (0-23) to number of sales
            Example: {8: 5, 9: 12, 10: 15, ...}
        """
        ventas = handler.ventas.get_all()
        
        sales_by_hour = {hour: 0 for hour in range(24)}  # Initialize all hours
        
        for venta in ventas:
            # Extract hour from datetime (YYYY-MM-DDTHH:MM:SS)
            try:
                datetime_str = venta.fecha
                if 'T' in datetime_str:
                    time_part = datetime_str.split('T')[1]
                    hour = int(time_part.split(':')[0])
                    sales_by_hour[hour] = sales_by_hour.get(hour, 0) + 1
            except (ValueError, IndexError):
                # Skip malformed dates
                continue
        
        return sales_by_hour
    
    @staticmethod
    def get_sales_by_time_range(handler, start_hour: int, end_hour: int) -> int:
        """
        Get total sales in a specific time range.
        
        Args:
            handler: DataHandler instance
            start_hour: Start hour (inclusive, 0-23)
            end_hour: End hour (inclusive, 0-23)
            
        Returns:
            Total number of sales in that time range
        """
        sales_by_hour = ReportingService.get_sales_by_hour(handler)
        
        total = 0
        for hour in range(start_hour, end_hour + 1):
            total += sales_by_hour.get(hour, 0)
        
        return total
    
    # ──────────────────────────────────────────────────────
    # COMPARATIVE ANALYSIS
    # ──────────────────────────────────────────────────────
    
    @staticmethod
    def compare_dates(handler, dates: List[str]) -> Dict[str, Dict[str, int]]:
        """
        Compare sales metrics across multiple dates.
        
        Args:
            handler: DataHandler instance
            dates: List of dates to compare (YYYY-MM-DD format)
            
        Returns:
            Dict mapping each date to its metrics
            Example: {
                '2024-11-16': {'ventas': 15, 'hotdogs': 45, 'promedio': 3.0},
                '2024-11-17': {'ventas': 20, 'hotdogs': 67, 'promedio': 3.35}
            }
        """
        comparison = {}
        
        for fecha in dates:
            # Filter sales for this date
            ventas_del_dia = handler.ventas.get_by_date(fecha)
            
            if not ventas_del_dia:
                comparison[fecha] = {
                    'ventas': 0,
                    'hotdogs': 0,
                    'promedio': 0.0
                }
                continue
            
            total_ventas = len(ventas_del_dia)
            total_hotdogs = sum(
                sum(item['cantidad'] for item in venta.items)
                for venta in ventas_del_dia
            )
            promedio = total_hotdogs / total_ventas if total_ventas > 0 else 0.0
            
            comparison[fecha] = {
                'ventas': total_ventas,
                'hotdogs': total_hotdogs,
                'promedio': round(promedio, 2)
            }
        
        return comparison
    
    # ──────────────────────────────────────────────────────
    # SUMMARY STATISTICS
    # ──────────────────────────────────────────────────────
    
    @staticmethod
    def get_general_stats(handler) -> Dict[str, any]:
        """
        Get general statistics across all sales.
        
        Args:
            handler: DataHandler instance
            
        Returns:
            Dict with general statistics
        """
        ventas = handler.ventas.get_all()
        
        if not ventas:
            return {
                'total_ventas': 0,
                'total_hotdogs': 0,
                'promedio_por_venta': 0.0,
                'dias_con_ventas': 0,
                'venta_mas_grande': 0,
                'venta_mas_pequeña': 0,
            }
        
        total_ventas = len(ventas)
        total_hotdogs = sum(
            sum(item['cantidad'] for item in venta.items)
            for venta in ventas
        )
        
        # Items per sale
        items_por_venta = [
            sum(item['cantidad'] for item in venta.items)
            for venta in ventas
        ]
        
        # Unique dates
        fechas_unicas = set(venta.fecha.split('T')[0] for venta in ventas)
        
        return {
            'total_ventas': total_ventas,
            'total_hotdogs': total_hotdogs,
            'promedio_por_venta': round(total_hotdogs / total_ventas, 2),
            'dias_con_ventas': len(fechas_unicas),
            'venta_mas_grande': max(items_por_venta),
            'venta_mas_pequeña': min(items_por_venta),
        }
    
    @staticmethod
    def get_date_range(handler) -> Tuple[str, str]:
        """
        Get the date range of all sales.
        
        Args:
            handler: DataHandler instance
            
        Returns:
            Tuple of (earliest_date, latest_date) in YYYY-MM-DD format
        """
        ventas = handler.ventas.get_all()
        
        if not ventas:
            return (None, None)
        
        fechas = [venta.fecha.split('T')[0] for venta in ventas]
        
        return (min(fechas), max(fechas))
