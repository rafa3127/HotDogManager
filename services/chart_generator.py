"""
Visualization module using matplotlib for sales analytics.

Generates professional charts and graphs from sales data.

Author: Rafael Correa
Date: November 16, 2025
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from typing import Dict, List, Tuple
import os


class ChartGenerator:
    """
    Generates charts using matplotlib.
    
    All methods are static and save charts to files.
    """
    
    # Default chart style
    STYLE = 'seaborn-v0_8-darkgrid'
    FIGSIZE = (12, 6)
    DPI = 100
    
    @staticmethod
    def _setup_style():
        """Apply default style to charts."""
        try:
            plt.style.use(ChartGenerator.STYLE)
        except:
            # Fallback if style not available
            plt.style.use('default')
    
    @staticmethod
    def _ensure_output_dir(output_dir: str = 'charts'):
        """
        Ensure output directory exists.
        
        Args:
            output_dir: Directory to save charts (default: 'charts')
        """
        os.makedirs(output_dir, exist_ok=True)
    
    # ──────────────────────────────────────────────────────
    # TEMPORAL CHARTS (Line charts)
    # ──────────────────────────────────────────────────────
    
    @staticmethod
    def sales_over_time(
        sales_by_date: Dict[str, int],
        output_file: str = 'charts/ventas_por_dia.png',
        title: str = 'Ventas por Día'
    ) -> str:
        """
        Generate line chart showing sales over time.
        
        Args:
            sales_by_date: Dict mapping date (YYYY-MM-DD) to number of sales
            output_file: Path to save the chart
            title: Chart title
            
        Returns:
            Path to saved chart
        """
        ChartGenerator._setup_style()
        ChartGenerator._ensure_output_dir(os.path.dirname(output_file))
        
        if not sales_by_date:
            # Create empty chart with message
            fig, ax = plt.subplots(figsize=ChartGenerator.FIGSIZE, dpi=ChartGenerator.DPI)
            ax.text(0.5, 0.5, 'No hay datos para mostrar', 
                   ha='center', va='center', fontsize=16)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            plt.savefig(output_file, bbox_inches='tight')
            plt.close()
            return output_file
        
        # Parse dates and values
        dates = [datetime.strptime(date, '%Y-%m-%d') for date in sales_by_date.keys()]
        values = list(sales_by_date.values())
        
        # Create figure
        fig, ax = plt.subplots(figsize=ChartGenerator.FIGSIZE, dpi=ChartGenerator.DPI)
        
        # Plot line
        ax.plot(dates, values, marker='o', linewidth=2, markersize=8, color='#2E86AB')
        
        # Formatting
        ax.set_xlabel('Fecha', fontsize=12, fontweight='bold')
        ax.set_ylabel('Número de Ventas', fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.xticks(rotation=45, ha='right')
        
        # Grid
        ax.grid(True, alpha=0.3)
        
        # Add value labels on points
        for date, value in zip(dates, values):
            ax.annotate(str(value), (date, value), 
                       textcoords="offset points", xytext=(0,10), 
                       ha='center', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(output_file, bbox_inches='tight')
        plt.close()
        
        return output_file
    
    @staticmethod
    def hotdogs_over_time(
        hotdogs_by_date: Dict[str, int],
        output_file: str = 'charts/hotdogs_por_dia.png',
        title: str = 'Hot Dogs Vendidos por Día'
    ) -> str:
        """
        Generate line chart showing hot dogs sold over time.
        
        Args:
            hotdogs_by_date: Dict mapping date to total hot dogs sold
            output_file: Path to save the chart
            title: Chart title
            
        Returns:
            Path to saved chart
        """
        ChartGenerator._setup_style()
        ChartGenerator._ensure_output_dir(os.path.dirname(output_file))
        
        if not hotdogs_by_date:
            fig, ax = plt.subplots(figsize=ChartGenerator.FIGSIZE, dpi=ChartGenerator.DPI)
            ax.text(0.5, 0.5, 'No hay datos para mostrar', 
                   ha='center', va='center', fontsize=16)
            ax.axis('off')
            plt.savefig(output_file, bbox_inches='tight')
            plt.close()
            return output_file
        
        dates = [datetime.strptime(date, '%Y-%m-%d') for date in hotdogs_by_date.keys()]
        values = list(hotdogs_by_date.values())
        
        fig, ax = plt.subplots(figsize=ChartGenerator.FIGSIZE, dpi=ChartGenerator.DPI)
        
        ax.plot(dates, values, marker='s', linewidth=2, markersize=8, color='#A23B72')
        
        ax.set_xlabel('Fecha', fontsize=12, fontweight='bold')
        ax.set_ylabel('Hot Dogs Vendidos', fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.xticks(rotation=45, ha='right')
        
        ax.grid(True, alpha=0.3)
        
        for date, value in zip(dates, values):
            ax.annotate(str(value), (date, value), 
                       textcoords="offset points", xytext=(0,10), 
                       ha='center', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(output_file, bbox_inches='tight')
        plt.close()
        
        return output_file
    
    # ──────────────────────────────────────────────────────
    # RANKING CHARTS (Horizontal bar charts)
    # ──────────────────────────────────────────────────────
    
    @staticmethod
    def top_hotdogs(
        top_hotdogs: List[Tuple[str, int]],
        output_file: str = 'charts/top_hotdogs.png',
        title: str = 'Hot Dogs Más Vendidos'
    ) -> str:
        """
        Generate horizontal bar chart for top hot dogs.
        
        Args:
            top_hotdogs: List of (name, quantity) tuples
            output_file: Path to save the chart
            title: Chart title
            
        Returns:
            Path to saved chart
        """
        ChartGenerator._setup_style()
        ChartGenerator._ensure_output_dir(os.path.dirname(output_file))
        
        if not top_hotdogs:
            fig, ax = plt.subplots(figsize=ChartGenerator.FIGSIZE, dpi=ChartGenerator.DPI)
            ax.text(0.5, 0.5, 'No hay datos para mostrar', 
                   ha='center', va='center', fontsize=16)
            ax.axis('off')
            plt.savefig(output_file, bbox_inches='tight')
            plt.close()
            return output_file
        
        # Reverse order so highest is at top
        names = [name for name, _ in reversed(top_hotdogs)]
        quantities = [qty for _, qty in reversed(top_hotdogs)]
        
        fig, ax = plt.subplots(figsize=(10, max(6, len(names) * 0.5)), dpi=ChartGenerator.DPI)
        
        # Create bars with gradient colors
        colors = plt.cm.viridis([i/len(names) for i in range(len(names))])
        bars = ax.barh(names, quantities, color=colors, edgecolor='black', linewidth=0.5)
        
        ax.set_xlabel('Cantidad Vendida', fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
        # Add value labels on bars
        for i, (bar, qty) in enumerate(zip(bars, quantities)):
            ax.text(qty, bar.get_y() + bar.get_height()/2, f' {qty}', 
                   va='center', fontsize=10, fontweight='bold')
        
        ax.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        plt.savefig(output_file, bbox_inches='tight')
        plt.close()
        
        return output_file
    
    @staticmethod
    def ingredient_consumption(
        consumption: Dict[str, int],
        output_file: str = 'charts/ingredientes_consumidos.png',
        title: str = 'Ingredientes Más Consumidos',
        top_n: int = 15
    ) -> str:
        """
        Generate horizontal bar chart for ingredient consumption.
        
        Args:
            consumption: Dict mapping ingredient name to quantity consumed
            output_file: Path to save the chart
            title: Chart title
            top_n: Show only top N ingredients
            
        Returns:
            Path to saved chart
        """
        ChartGenerator._setup_style()
        ChartGenerator._ensure_output_dir(os.path.dirname(output_file))
        
        if not consumption:
            fig, ax = plt.subplots(figsize=ChartGenerator.FIGSIZE, dpi=ChartGenerator.DPI)
            ax.text(0.5, 0.5, 'No hay datos para mostrar', 
                   ha='center', va='center', fontsize=16)
            ax.axis('off')
            plt.savefig(output_file, bbox_inches='tight')
            plt.close()
            return output_file
        
        # Get top N
        items = list(consumption.items())[:top_n]
        
        # Reverse for display
        names = [name for name, _ in reversed(items)]
        quantities = [qty for _, qty in reversed(items)]
        
        fig, ax = plt.subplots(figsize=(12, max(6, len(names) * 0.4)), dpi=ChartGenerator.DPI)
        
        colors = plt.cm.plasma([i/len(names) for i in range(len(names))])
        bars = ax.barh(names, quantities, color=colors, edgecolor='black', linewidth=0.5)
        
        ax.set_xlabel('Cantidad Consumida', fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
        for bar, qty in zip(bars, quantities):
            ax.text(qty, bar.get_y() + bar.get_height()/2, f' {qty}', 
                   va='center', fontsize=9, fontweight='bold')
        
        ax.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        plt.savefig(output_file, bbox_inches='tight')
        plt.close()
        
        return output_file
    
    # ──────────────────────────────────────────────────────
    # DISTRIBUTION CHARTS (Histograms/Bar charts)
    # ──────────────────────────────────────────────────────
    
    @staticmethod
    def sales_by_hour(
        sales_by_hour: Dict[int, int],
        output_file: str = 'charts/ventas_por_hora.png',
        title: str = 'Distribución de Ventas por Hora del Día'
    ) -> str:
        """
        Generate bar chart showing sales distribution by hour.
        
        Args:
            sales_by_hour: Dict mapping hour (0-23) to number of sales
            output_file: Path to save the chart
            title: Chart title
            
        Returns:
            Path to saved chart
        """
        ChartGenerator._setup_style()
        ChartGenerator._ensure_output_dir(os.path.dirname(output_file))
        
        hours = list(range(24))
        values = [sales_by_hour.get(hour, 0) for hour in hours]
        
        fig, ax = plt.subplots(figsize=ChartGenerator.FIGSIZE, dpi=ChartGenerator.DPI)
        
        # Color bars based on value (gradient)
        max_val = max(values) if values else 1
        colors = [plt.cm.coolwarm(val/max_val) if max_val > 0 else 'gray' for val in values]
        
        bars = ax.bar(hours, values, color=colors, edgecolor='black', linewidth=0.5)
        
        ax.set_xlabel('Hora del Día', fontsize=12, fontweight='bold')
        ax.set_ylabel('Número de Ventas', fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
        ax.set_xticks(hours)
        ax.set_xticklabels([f'{h:02d}:00' for h in hours], rotation=45, ha='right')
        
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(output_file, bbox_inches='tight')
        plt.close()
        
        return output_file
    
    # ──────────────────────────────────────────────────────
    # COMPARATIVE CHARTS (Multiple lines)
    # ──────────────────────────────────────────────────────
    
    @staticmethod
    def compare_dates(
        comparison: Dict[str, Dict[str, int]],
        output_file: str = 'charts/comparacion_fechas.png',
        title: str = 'Comparación entre Fechas'
    ) -> str:
        """
        Generate grouped bar chart comparing multiple dates.
        
        Args:
            comparison: Dict mapping date to metrics dict
                       Example: {'2024-11-16': {'ventas': 15, 'hotdogs': 45}}
            output_file: Path to save the chart
            title: Chart title
            
        Returns:
            Path to saved chart
        """
        ChartGenerator._setup_style()
        ChartGenerator._ensure_output_dir(os.path.dirname(output_file))
        
        if not comparison:
            fig, ax = plt.subplots(figsize=ChartGenerator.FIGSIZE, dpi=ChartGenerator.DPI)
            ax.text(0.5, 0.5, 'No hay datos para mostrar', 
                   ha='center', va='center', fontsize=16)
            ax.axis('off')
            plt.savefig(output_file, bbox_inches='tight')
            plt.close()
            return output_file
        
        dates = list(comparison.keys())
        ventas_values = [comparison[date]['ventas'] for date in dates]
        hotdogs_values = [comparison[date]['hotdogs'] for date in dates]
        
        x = range(len(dates))
        width = 0.35
        
        fig, ax = plt.subplots(figsize=ChartGenerator.FIGSIZE, dpi=ChartGenerator.DPI)
        
        bars1 = ax.bar([i - width/2 for i in x], ventas_values, width, 
                       label='Ventas', color='#2E86AB', edgecolor='black', linewidth=0.5)
        bars2 = ax.bar([i + width/2 for i in x], hotdogs_values, width, 
                       label='Hot Dogs', color='#A23B72', edgecolor='black', linewidth=0.5)
        
        ax.set_xlabel('Fecha', fontsize=12, fontweight='bold')
        ax.set_ylabel('Cantidad', fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(dates, rotation=45, ha='right')
        ax.legend()
        
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}',
                       ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(output_file, bbox_inches='tight')
        plt.close()
        
        return output_file
