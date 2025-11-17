"""
Actions for reporting and charts (matplotlib).

These actions generate visual reports and statistics.

Author: Rafael Correa
Date: November 16, 2025
"""

import os
from cli.core import ActionResult, Views, Colors
from services import ReportingService, ChartGenerator


# ──────────────────────────────────────────────────────
# GENERATE CHARTS
# ──────────────────────────────────────────────────────

def action_generate_all_charts(context: dict) -> ActionResult:
    """
    Generate all available charts at once.
    
    Args:
        context: Router context with handler
        
    Returns:
        ActionResult
    """
    handler = context['handler']
    
    Views.clear_screen()
    Views.print_header("Generar Todos los Gráficos")
    
    ventas = handler.ventas.get_all()
    
    if not ventas:
        Views.print_warning("No hay ventas registradas. Simula un día primero.")
        Views.pause()
        return ActionResult.success()
    
    print(f"\n{Colors.bold('Generando gráficos...')}\n")
    
    charts_generated = []
    
    try:
        # 1. Sales over time
        print("  📈 Ventas por día...")
        sales_by_date = ReportingService.get_sales_by_date(handler)
        chart1 = ChartGenerator.sales_over_time(sales_by_date)
        charts_generated.append(chart1)
        
        # 2. Hot dogs over time
        print("  📈 Hot dogs vendidos por día...")
        hotdogs_by_date = ReportingService.get_hotdogs_sold_by_date(handler)
        chart2 = ChartGenerator.hotdogs_over_time(hotdogs_by_date)
        charts_generated.append(chart2)
        
        # 3. Top hot dogs
        print("  🏆 Hot dogs más vendidos...")
        top_hotdogs = ReportingService.get_top_hotdogs(handler, limit=10)
        chart3 = ChartGenerator.top_hotdogs(top_hotdogs)
        charts_generated.append(chart3)
        
        # 4. Ingredient consumption
        print("  🥫 Ingredientes consumidos...")
        consumption = ReportingService.get_ingredient_consumption(handler)
        chart4 = ChartGenerator.ingredient_consumption(consumption, top_n=15)
        charts_generated.append(chart4)
        
        # 5. Sales by hour
        print("  🕐 Distribución por hora...")
        sales_by_hour = ReportingService.get_sales_by_hour(handler)
        chart5 = ChartGenerator.sales_by_hour(sales_by_hour)
        charts_generated.append(chart5)
        
        print()
        Views.print_success(f"✅ {len(charts_generated)} gráficos generados exitosamente!")
        print(f"\n{Colors.bold('Archivos guardados:')}")
        for chart in charts_generated:
            print(f"  📊 {chart}")
        
        print(f"\n{Colors.info('💡 Abre los archivos con tu visor de imágenes preferido.')}")
        
    except Exception as e:
        Views.print_error(f"Error generando gráficos: {e}")
        import traceback
        traceback.print_exc()
    
    Views.pause()
    return ActionResult.success()


def action_sales_over_time_chart(context: dict) -> ActionResult:
    """
    Generate sales over time chart.
    
    Args:
        context: Router context with handler
        
    Returns:
        ActionResult
    """
    handler = context['handler']
    
    Views.clear_screen()
    Views.print_header("Gráfico: Ventas por Día")
    
    print(f"\n{Colors.bold('Generando gráfico...')}")
    
    try:
        sales_by_date = ReportingService.get_sales_by_date(handler)
        
        if not sales_by_date:
            Views.print_warning("No hay datos suficientes para generar el gráfico.")
            Views.pause()
            return ActionResult.success()
        
        chart_path = ChartGenerator.sales_over_time(sales_by_date)
        
        Views.print_success(f"✅ Gráfico generado: {chart_path}")
        
    except Exception as e:
        Views.print_error(f"Error: {e}")
    
    Views.pause()
    return ActionResult.success()


def action_top_hotdogs_chart(context: dict) -> ActionResult:
    """
    Generate top hot dogs chart.
    
    Args:
        context: Router context with handler
        
    Returns:
        ActionResult
    """
    handler = context['handler']
    
    Views.clear_screen()
    Views.print_header("Gráfico: Hot Dogs Más Vendidos")
    
    limit = Views.prompt_int("Cantidad de hot dogs a mostrar (default: 10): ", 
                            min_val=1, max_val=50, default=10)
    
    print(f"\n{Colors.bold('Generando gráfico...')}")
    
    try:
        top_hotdogs = ReportingService.get_top_hotdogs(handler, limit=limit)
        
        if not top_hotdogs:
            Views.print_warning("No hay datos suficientes para generar el gráfico.")
            Views.pause()
            return ActionResult.success()
        
        chart_path = ChartGenerator.top_hotdogs(top_hotdogs)
        
        Views.print_success(f"✅ Gráfico generado: {chart_path}")
        
    except Exception as e:
        Views.print_error(f"Error: {e}")
    
    Views.pause()
    return ActionResult.success()


def action_sales_by_hour_chart(context: dict) -> ActionResult:
    """
    Generate sales distribution by hour chart.
    
    Args:
        context: Router context with handler
        
    Returns:
        ActionResult
    """
    handler = context['handler']
    
    Views.clear_screen()
    Views.print_header("Gráfico: Distribución por Hora")
    
    print(f"\n{Colors.bold('Generando gráfico...')}")
    
    try:
        sales_by_hour = ReportingService.get_sales_by_hour(handler)
        
        chart_path = ChartGenerator.sales_by_hour(sales_by_hour)
        
        Views.print_success(f"✅ Gráfico generado: {chart_path}")
        
    except Exception as e:
        Views.print_error(f"Error: {e}")
    
    Views.pause()
    return ActionResult.success()


def action_compare_dates_chart(context: dict) -> ActionResult:
    """
    Generate comparison chart between dates.
    
    Args:
        context: Router context with handler
        
    Returns:
        ActionResult
    """
    handler = context['handler']
    
    Views.clear_screen()
    Views.print_header("Gráfico: Comparar Fechas")
    
    # Get available dates
    date_range = ReportingService.get_date_range(handler)
    
    if not date_range[0]:
        Views.print_warning("No hay ventas registradas.")
        Views.pause()
        return ActionResult.success()
    
    print(f"\n{Colors.info(f'Fechas disponibles: {date_range[0]} a {date_range[1]}')}")
    
    # Show sales by date for reference
    sales_by_date = ReportingService.get_sales_by_date(handler)
    print(f"\n{Colors.bold('Días con ventas:')}")
    for fecha, num_ventas in list(sales_by_date.items())[:10]:  # Show first 10
        print(f"  • {fecha}: {num_ventas} ventas")
    if len(sales_by_date) > 10:
        print(f"  ... y {len(sales_by_date) - 10} días más")
    
    print(f"\n{Colors.bold('Opciones:')}")
    print("  1. Comparar fechas específicas (ej: 2024-11-01, 2024-11-02, 2024-11-15)")
    print("  2. Comparar rango de fechas (ej: todos los días entre 2024-11-01 y 2024-11-05)")
    print()
    
    opcion = Views.prompt("Selecciona opción (1 o 2): ")
    
    dates = []
    
    if opcion == '1':
        # Specific dates
        print(f"\n{Colors.bold('Ingresa las fechas a comparar, separados por comas (formato YYYY-MM-DD):')}")
        print(f"{Colors.yellow('Ejemplo: 2024-11-16, 2024-11-17, 2024-11-18')}")
        dates_input = Views.prompt("Fechas separadas por comas: ")
        
        if not dates_input.strip():
            Views.print_warning("No ingresaste fechas.")
            Views.pause()
            return ActionResult.success()
        
        # Parse dates
        dates = [d.strip() for d in dates_input.split(',')]
        
    elif opcion == '2':
        # Date range
        print(f"\n{Colors.bold('Ingresa el rango de fechas:')}")
        fecha_inicio = Views.prompt("Fecha inicio (YYYY-MM-DD): ")
        fecha_fin = Views.prompt("Fecha fin (YYYY-MM-DD): ")
        
        if not fecha_inicio.strip() or not fecha_fin.strip():
            Views.print_warning("Debes ingresar ambas fechas.")
            Views.pause()
            return ActionResult.success()
        
        # Generate all dates in range
        try:
            from datetime import datetime, timedelta
            start = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            end = datetime.strptime(fecha_fin, '%Y-%m-%d')
            
            current = start
            while current <= end:
                dates.append(current.strftime('%Y-%m-%d'))
                current += timedelta(days=1)
            
            print(f"\n{Colors.info(f'Se compararán {len(dates)} días')}")
            
        except ValueError:
            Views.print_error("Formato de fecha inválido. Use YYYY-MM-DD")
            Views.pause()
            return ActionResult.success()
    else:
        Views.print_warning("Opción inválida.")
        Views.pause()
        return ActionResult.success()
    
    print(f"\n{Colors.bold('Generando gráfico...')}")
    
    try:
        comparison = ReportingService.compare_dates(handler, dates)
        
        chart_path = ChartGenerator.compare_dates(comparison)
        
        Views.print_success(f"✅ Gráfico generado: {chart_path}")
        
        # Show summary
        print(f"\n{Colors.bold('Resumen:')}")
        for fecha, metrics in comparison.items():
            print(f"  {fecha}: {metrics['ventas']} ventas, {metrics['hotdogs']} hot dogs")
        
    except Exception as e:
        Views.print_error(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    Views.pause()
    return ActionResult.success()


# ──────────────────────────────────────────────────────
# TEXT REPORTS
# ──────────────────────────────────────────────────────

def action_general_report(context: dict) -> ActionResult:
    """
    Show general statistics report (text-based).
    
    Args:
        context: Router context with handler
        
    Returns:
        ActionResult
    """
    handler = context['handler']
    
    Views.clear_screen()
    Views.print_header("Reporte General de Estadísticas")
    
    ventas = handler.ventas.get_all()
    
    if not ventas:
        Views.print_warning("No hay ventas registradas.")
        Views.pause()
        return ActionResult.success()
    
    # Get stats
    stats = ReportingService.get_general_stats(handler)
    date_range = ReportingService.get_date_range(handler)
    top_hotdogs = ReportingService.get_top_hotdogs(handler, limit=5)
    
    # Print report
    print(f"\n{Colors.bold('═' * 60)}")
    print(f"{Colors.bold(Colors.blue('ESTADÍSTICAS GENERALES'))}")
    print(f"{Colors.bold('═' * 60)}")
    
    print(f"\n{Colors.bold('Período:')}")
    print(f"  Desde: {date_range[0]}")
    print(f"  Hasta: {date_range[1]}")
    print(f"  Días con ventas: {stats['dias_con_ventas']}")
    
    print(f"\n{Colors.bold('Ventas:')}")
    print(f"  Total de ventas: {stats['total_ventas']}")
    print(f"  Total de hot dogs: {stats['total_hotdogs']}")
    print(f"  Promedio por venta: {stats['promedio_por_venta']}")
    
    print(f"\n{Colors.bold('Tamaño de ventas:')}")
    print(f"  Venta más grande: {stats['venta_mas_grande']} hot dogs")
    print(f"  Venta más pequeña: {stats['venta_mas_pequeña']} hot dogs")
    
    print(f"\n{Colors.bold('Top 5 Hot Dogs:')}")
    for i, (nombre, cantidad) in enumerate(top_hotdogs, 1):
        print(f"  {i}. {nombre}: {Colors.green(str(cantidad))} unidades")
    
    # Time-based analysis
    morning_sales = ReportingService.get_sales_by_time_range(handler, 6, 12)
    afternoon_sales = ReportingService.get_sales_by_time_range(handler, 13, 18)
    night_sales = ReportingService.get_sales_by_time_range(handler, 19, 23)
    
    print(f"\n{Colors.bold('Ventas por franja horaria:')}")
    print(f"  Mañana (6am-12pm): {morning_sales}")
    print(f"  Tarde (1pm-6pm): {afternoon_sales}")
    print(f"  Noche (7pm-11pm): {night_sales}")
    
    print(f"\n{Colors.bold('═' * 60)}")
    
    Views.pause()
    return ActionResult.success()
