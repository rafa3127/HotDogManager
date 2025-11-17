"""
Actions for sales management (ventas).

These actions handle sales-related operations:
- Registering individual sales (manual)
- Viewing sales history
- Sales statistics

Author: Rafael Correa
Date: November 16, 2025
"""

import random
import time
from datetime import datetime

from cli.core import ActionResult, Views, Colors
from services import VentaService, MenuService, IngredientService


# ──────────────────────────────────────────────────────
# MANUAL SALE REGISTRATION
# ──────────────────────────────────────────────────────

def action_register_sale(context: dict) -> ActionResult:
    """
    Registers a sale manually (interactive).
    
    User builds a sale step by step using the VentaBuilder pattern.
    
    Args:
        context: Router context with handler
        
    Returns:
        ActionResult
    """
    handler = context['handler']
    
    Views.clear_screen()
    Views.print_header("Registrar Venta")
    
    # Get available hot dogs
    hotdogs = MenuService.list_all(handler)
    
    if not hotdogs:
        Views.print_error("No hay hot dogs en el menú. Agrégalos primero.")
        Views.pause()
        return ActionResult.success()
    
    # Create builder
    builder = VentaService.create_draft()
    
    while True:
        Views.clear_screen()
        Views.print_header("Registrar Venta - Construyendo Orden")
        
        # Show current draft
        if builder.items:
            print(f"\n{Colors.bold('Items en la orden:')}")
            for i, item in enumerate(builder.items, 1):
                print(f"  {i}. {item['hotdog_nombre']} x {item['cantidad']}")
            print(f"\n{Colors.blue(f'Total items: {builder.get_total_items()}')}")
        else:
            print(f"\n{Colors.yellow('(Orden vacía)')}")
        
        # Menu options
        print(f"\n{Colors.bold('Opciones:')}")
        print("  1. Agregar hot dog")
        print("  2. Remover hot dog")
        print("  3. Ver preview (verificar inventario)")
        print("  4. Confirmar venta")
        print("  5. Cancelar")
        
        choice = Views.prompt("\nSeleccione opción: ")
        
        if choice == '1':
            # Add hot dog
            print(f"\n{Colors.bold('Hot dogs disponibles:')}")
            for i, hd in enumerate(hotdogs, 1):
                print(f"  {i}. {hd.nombre}")
            
            try:
                hd_idx = Views.prompt_int(f"Seleccione hot dog (1-{len(hotdogs)}): ", 
                                         min_val=1, max_val=len(hotdogs))
                cantidad = Views.prompt_int("Cantidad: ", min_val=1, default=1)
                
                selected_hd = hotdogs[hd_idx - 1]
                result = VentaService.add_item(handler, builder, selected_hd.id, cantidad)
                
                if result['exito']:
                    Views.print_success(f"Agregado: {result['item']['hotdog_nombre']} x {cantidad}")
                    if result.get('merged'):
                        Views.print_info("(Cantidad sumada a item existente)")
                else:
                    Views.print_error(result['error'])
            except (ValueError, IndexError):
                Views.print_error("Entrada inválida")
            
            Views.pause()
        
        elif choice == '2':
            # Remove hot dog
            if not builder.items:
                Views.print_warning("No hay items para remover")
                Views.pause()
                continue
            
            print(f"\n{Colors.bold('Items actuales:')}")
            for i, item in enumerate(builder.items, 1):
                print(f"  {i}. {item['hotdog_nombre']} x {item['cantidad']}")
            
            try:
                item_idx = Views.prompt_int(f"Seleccione item a remover (1-{len(builder.items)}): ",
                                           min_val=1, max_val=len(builder.items))
                
                item_to_remove = builder.items[item_idx - 1]
                result = VentaService.remove_item(builder, item_to_remove['hotdog_id'])
                
                if result['removed']:
                    Views.print_success(f"Removido: {item_to_remove['hotdog_nombre']}")
            except (ValueError, IndexError):
                Views.print_error("Entrada inválida")
            
            Views.pause()
        
        elif choice == '3':
            # Preview
            if not builder.items:
                Views.print_warning("Orden vacía, agrega items primero")
                Views.pause()
                continue
            
            preview = VentaService.preview_draft(handler, builder)
            
            print(f"\n{Colors.bold('Preview de la venta:')}")
            print(f"  Total items: {preview['total_items']}")
            
            if preview['disponible']:
                Views.print_success("✅ Hay inventario suficiente para toda la orden")
            else:
                Views.print_warning("⚠️  INVENTARIO INSUFICIENTE")
                print("\nHot dogs sin inventario:")
                for hd_nombre in preview['hotdogs_sin_inventario']:
                    print(f"  • {hd_nombre}")
            
            Views.pause()
        
        elif choice == '4':
            # Confirm sale
            if not builder.items:
                Views.print_warning("No puedes confirmar una orden vacía")
                Views.pause()
                continue
            
            # Final confirmation
            if not Views.confirm("\n¿Confirmar venta?"):
                continue
            
            result = VentaService.confirm_sale(handler, builder)
            
            if result['exito']:
                Views.print_success(f"✅ Venta registrada exitosamente!")
                
                if result.get('inventario_descontado'):
                    print(f"\n{Colors.bold('Inventario descontado:')}")
                    for ing_id, cantidad in result['inventario_descontado'].items():
                        ing = handler.ingredientes.get(ing_id)
                        if ing:
                            print(f"  • {ing.nombre}: -{cantidad}")
                
                handler.commit()
                Views.pause()
                break  # Exit loop after successful sale
            else:
                Views.print_error(result['error'])
                
                if result.get('advertencias'):
                    for adv in result['advertencias']:
                        Views.print_warning(adv)
                
                Views.pause()
        
        elif choice == '5':
            # Cancel
            if Views.confirm("¿Cancelar venta?", default=False):
                Views.print_info("Venta cancelada")
                Views.pause()
                break
        
        else:
            Views.print_warning("Opción inválida")
            Views.pause()
    
    return ActionResult.success()


# ──────────────────────────────────────────────────────
# VIEW SALES HISTORY
# ──────────────────────────────────────────────────────

def action_view_sales(context: dict) -> ActionResult:
    """
    Shows all registered sales.
    
    Args:
        context: Router context with handler
        
    Returns:
        ActionResult
    """
    handler = context['handler']
    
    Views.clear_screen()
    Views.print_header("Historial de Ventas")
    
    ventas = handler.ventas.get_all()
    
    if not ventas:
        Views.print_warning("No hay ventas registradas")
        Views.pause()
        return ActionResult.success()
    
    # Sort by date (newest first)
    ventas_sorted = sorted(ventas, key=lambda v: v.fecha, reverse=True)
    
    print(f"\n{Colors.bold(Colors.blue(f'Total de ventas: {len(ventas)}'))}")
    print()
    
    for venta in ventas_sorted:
        print(f"{Colors.bold('─' * 60)}")
        print(f"{Colors.bold('Fecha:')} {venta.fecha}")
        print(f"{Colors.bold('ID:')} {venta.id}")
        print(f"{Colors.bold('Items:')}")
        
        for item in venta.items:
            print(f"  • {item['hotdog_nombre']} x {item['cantidad']}")
        
        total_items = sum(item['cantidad'] for item in venta.items)
        print(f"{Colors.blue(f'Total: {total_items} hot dogs')}")
        print()
    
    Views.pause()
    return ActionResult.success()


# ──────────────────────────────────────────────────────
# SIMULATION
# ──────────────────────────────────────────────────────

def action_simulate_day(context: dict) -> ActionResult:
    """
    Simulates a full day of sales according to requirements.
    
    Process:
    - Random number of customers (0-200)
    - Each customer buys 0-5 random hot dogs
    - Verify inventory before each sale
    - Show progress bar
    - Generate final report with statistics
    
    Args:
        context: Router context with handler
        
    Returns:
        ActionResult
    """
    handler = context['handler']
    
    Views.clear_screen()
    Views.print_header("Simular Día de Ventas")
    
    # Get available hot dogs
    hotdogs = MenuService.list_all(handler)
    
    if not hotdogs:
        Views.print_error("No hay hot dogs en el menú. No se puede simular.")
        Views.pause()
        return ActionResult.success()
    
    # Warning
    print(f"\n{Colors.yellow('⚠️  Esta simulación generará ventas aleatorias y descontará inventario.')}")
    print(f"{Colors.yellow('Asegúrate de tener suficiente stock antes de continuar.')}")
    
    if not Views.confirm("\n¿Continuar con la simulación?", default=False):
        Views.print_info("Simulación cancelada")
        Views.pause()
        return ActionResult.success()
    
    # Ask for simulation date
    fecha_input = Views.prompt("Fecha de simulación (YYYY-MM-DD) o Enter para hoy: ")
    
    if fecha_input.strip():
        try:
            # Validate format
            datetime.strptime(fecha_input, '%Y-%m-%d')
            fecha_base = fecha_input
        except ValueError:
            Views.print_error("Formato de fecha inválido. Usando fecha actual.")
            fecha_base = datetime.now().strftime('%Y-%m-%d')
    else:
        fecha_base = datetime.now().strftime('%Y-%m-%d')
    
    # ──────────────────────────────────────────────────────
    # SIMULATION PARAMETERS
    # ──────────────────────────────────────────────────────
    
    num_clientes = random.randint(0, 200)
    
    print(f"\n{Colors.bold(f'🎲 Simulando día {fecha_base} con {num_clientes} clientes...')}")
    print()
    
    # Statistics tracking
    stats = {
        'clientes_cambio_opinion': 0,
        'clientes_no_pudieron_comprar': 0,
        'clientes_compraron': 0,
        'total_hotdogs_vendidos': 0,
        'hotdogs_vendidos_por_tipo': {},  # {hotdog_nombre: cantidad}
        'hotdogs_causaron_marcha': set(),  # Hot dogs que causaron marcha
        'ingredientes_causaron_marcha': set(),  # Ingredientes faltantes
        'total_acompanantes': 0,
    }
    
    # ──────────────────────────────────────────────────────
    # SIMULATE EACH CUSTOMER
    # ──────────────────────────────────────────────────────
    
    for i in range(num_clientes):
        # Progress bar
        _show_progress(i, num_clientes)
        
        # Random number of hot dogs per customer (0-5)
        num_hotdogs = random.randint(0, 5)
        
        if num_hotdogs == 0:
            # Customer changed mind
            stats['clientes_cambio_opinion'] += 1
            continue
        
        # Create sale builder
        builder = VentaService.create_draft()
        
        # Select random hot dogs
        for _ in range(num_hotdogs):
            random_hotdog = random.choice(hotdogs)
            VentaService.add_item(handler, builder, random_hotdog.id, cantidad=1)
        
        # Check if sale can be completed
        preview = VentaService.preview_draft(handler, builder)
        
        if not preview['disponible']:
            # Customer couldn't buy
            stats['clientes_no_pudieron_comprar'] += 1
            
            # Track which hot dogs caused the customer to leave
            for hd_nombre in preview['hotdogs_sin_inventario']:
                stats['hotdogs_causaron_marcha'].add(hd_nombre)
            
            # Track which ingredients caused the customer to leave
            for faltante in preview['faltantes']:
                stats['ingredientes_causaron_marcha'].add(
                    f"{faltante['ingrediente']} ({faltante['categoria']})"
                )
            
            continue
        
        # Customer can buy - confirm sale
        # Generate timestamp for this sale (spread throughout the day)
        hora = random.randint(8, 22)  # 8am - 10pm
        minuto = random.randint(0, 59)
        fecha_venta = f"{fecha_base}T{hora:02d}:{minuto:02d}:00"
        
        result = VentaService.confirm_sale(handler, builder, fecha=fecha_venta)
        
        if result['exito']:
            stats['clientes_compraron'] += 1
            
            # Count hot dogs sold
            for item in builder.items:
                hotdog_nombre = item['hotdog_nombre']
                cantidad = item['cantidad']
                stats['total_hotdogs_vendidos'] += cantidad
                stats['hotdogs_vendidos_por_tipo'][hotdog_nombre] = \
                    stats['hotdogs_vendidos_por_tipo'].get(hotdog_nombre, 0) + cantidad
            
            # Count acompañantes (including those in combos)
            venta = result['venta']
            for item in venta.items:
                hotdog = handler.menu.get(item['hotdog_id'])
                if hotdog and hasattr(hotdog, 'acompanante') and hotdog.acompanante:
                    stats['total_acompanantes'] += item['cantidad']
        
        # Delay for visual effect (slower for better UX)
        time.sleep(0.1)
    
    # Final progress
    _show_progress(num_clientes, num_clientes)
    print()  # New line after progress bar
    
    # Commit all sales
    handler.commit()
    
    # ──────────────────────────────────────────────────────
    # FINAL REPORT
    # ──────────────────────────────────────────────────────
    
    print(f"\n{Colors.bold('═' * 60)}")
    print(f"{Colors.bold(Colors.blue('REPORTE DEL DÍA'))}")
    print(f"{Colors.bold('═' * 60)}")
    
    print(f"\n{Colors.bold('Clientes:')}")
    print(f"  Total de clientes: {num_clientes}")
    print(f"  Cambiaron de opinión: {stats['clientes_cambio_opinion']} ({_percentage(stats['clientes_cambio_opinion'], num_clientes)}%)")
    print(f"  No pudieron comprar: {stats['clientes_no_pudieron_comprar']} ({_percentage(stats['clientes_no_pudieron_comprar'], num_clientes)}%)")
    print(f"  Compraron exitosamente: {stats['clientes_compraron']} ({_percentage(stats['clientes_compraron'], num_clientes)}%)")
    
    if stats['clientes_compraron'] > 0:
        promedio = stats['total_hotdogs_vendidos'] / stats['clientes_compraron']
        print(f"\n{Colors.bold('Hot Dogs:')}")
        print(f"  Total vendidos: {stats['total_hotdogs_vendidos']}")
        print(f"  Promedio por cliente: {promedio:.2f}")
        
        # Most sold hot dog
        if stats['hotdogs_vendidos_por_tipo']:
            mas_vendido = max(stats['hotdogs_vendidos_por_tipo'].items(), key=lambda x: x[1])
            print(f"  Más vendido: {Colors.green(mas_vendido[0])} ({mas_vendido[1]} unidades)")
    
    if stats['hotdogs_causaron_marcha']:
        print(f"\n{Colors.bold(Colors.yellow('Hot Dogs que causaron que clientes se marcharan:'))}")
        for hd_nombre in sorted(stats['hotdogs_causaron_marcha']):
            print(f"  • {hd_nombre}")
    
    if stats['ingredientes_causaron_marcha']:
        print(f"\n{Colors.bold(Colors.yellow('Ingredientes faltantes que causaron pérdidas:'))}")
        for ing in sorted(stats['ingredientes_causaron_marcha']):
            print(f"  • {ing}")
    
    print(f"\n{Colors.bold('Acompañantes:')}")
    print(f"  Total vendidos (incluyendo combos): {stats['total_acompanantes']}")
    
    print(f"\n{Colors.bold('═' * 60)}")
    
    Views.print_success(f"✅ Simulación completada: {stats['clientes_compraron']} ventas registradas")
    
    Views.pause()
    return ActionResult.success()


def _show_progress(current: int, total: int, bar_length: int = 40):
    """
    Shows a progress bar.
    
    Args:
        current: Current progress
        total: Total to complete
        bar_length: Length of the bar in characters
    """
    if total == 0:
        return
    
    percent = current / total
    filled = int(bar_length * percent)
    bar = '█' * filled + '░' * (bar_length - filled)
    
    print(f'\r{Colors.blue(f"Progreso: [{bar}] {current}/{total} ({percent*100:.1f}%)")}', end='', flush=True)


def _percentage(part: int, total: int) -> float:
    """
    Calculates percentage.
    
    Args:
        part: Part value
        total: Total value
        
    Returns:
        Percentage (0-100)
    """
    if total == 0:
        return 0.0
    return round((part / total) * 100, 1)


def action_view_sales_by_date(context: dict) -> ActionResult:
    """
    Shows sales filtered by date or date range.
    
    Supports:
    - Single date: "2024-11-16" (shows only that day)
    - Partial date: "2024-11" (shows entire month)
    - Date range: "2024-11-01" to "2024-11-30" (shows range)
    
    Args:
        context: Router context with handler
        
    Returns:
        ActionResult
    """
    handler = context['handler']
    
    Views.clear_screen()
    Views.print_header("Ventas por Fecha / Rango")
    
    print(f"\n{Colors.bold('Opciones:')}")
    print("  • Fecha única: YYYY-MM-DD (ej: 2024-11-16)")
    print("  • Parcial: YYYY-MM (ej: 2024-11 para todo noviembre)")
    print("  • Rango: Ingresa fecha inicio y fecha fin")
    print()
    
    fecha_inicio = Views.prompt("Fecha inicio (YYYY-MM-DD): ")
    
    if not fecha_inicio.strip():
        Views.print_error("Fecha no puede estar vacía")
        Views.pause()
        return ActionResult.success()
    
    # Ask for end date (optional)
    fecha_fin = Views.prompt("Fecha fin (Enter para solo fecha inicio): ")
    
    # Filter sales
    if fecha_fin.strip():
        # Date range
        try:
            # Validate formats
            datetime.strptime(fecha_inicio, '%Y-%m-%d')
            datetime.strptime(fecha_fin, '%Y-%m-%d')
            
            ventas_filtradas = handler.ventas.get_by_date_range(fecha_inicio, fecha_fin)
            header_text = f"Ventas desde {fecha_inicio} hasta {fecha_fin}"
        except ValueError:
            Views.print_error("Formato de fecha inválido. Use YYYY-MM-DD")
            Views.pause()
            return ActionResult.success()
    else:
        # Single date or partial
        ventas_filtradas = handler.ventas.get_by_date(fecha_inicio)
        header_text = f"Ventas para '{fecha_inicio}'"
    
    if not ventas_filtradas:
        Views.print_warning(f"No hay ventas para el criterio especificado")
        Views.pause()
        return ActionResult.success()
    
    # Sort by date (newest first)
    ventas_sorted = sorted(ventas_filtradas, key=lambda v: v.fecha, reverse=True)
    
    print(f"\n{Colors.bold(Colors.blue(header_text))}")
    print(f"{Colors.bold(Colors.blue(f'Ventas encontradas: {len(ventas_sorted)}'))}")
    print()
    
    # Calculate totals
    total_items_general = 0
    
    for venta in ventas_sorted:
        print(f"{Colors.bold('─' * 60)}")
        print(f"{Colors.bold('Fecha:')} {venta.fecha}")
        print(f"{Colors.bold('Items:')}")
        
        for item in venta.items:
            print(f"  • {item['hotdog_nombre']} x {item['cantidad']}")
        
        total_items = sum(item['cantidad'] for item in venta.items)
        total_items_general += total_items
        print(f"{Colors.blue(f'Total: {total_items} hot dogs')}")
        print()
    
    # Summary
    print(f"{Colors.bold('═' * 60)}")
    print(f"{Colors.bold('RESUMEN:')}")
    print(f"  Total de ventas: {len(ventas_sorted)}")
    print(f"  Total de hot dogs vendidos: {total_items_general}")
    if len(ventas_sorted) > 0:
        print(f"  Promedio por venta: {total_items_general / len(ventas_sorted):.2f}")
    print(f"{Colors.bold('═' * 60)}")
    
    Views.pause()
    return ActionResult.success()


# ──────────────────────────────────────────────────────
# STATISTICS
# ──────────────────────────────────────────────────────

def action_sales_statistics(context: dict) -> ActionResult:
    """
    Shows general sales statistics.
    
    Args:
        context: Router context with handler
        
    Returns:
        ActionResult
    """
    handler = context['handler']
    
    Views.clear_screen()
    Views.print_header("Estadísticas de Ventas")
    
    ventas = handler.ventas.get_all()
    
    if not ventas:
        Views.print_warning("No hay ventas registradas")
        Views.pause()
        return ActionResult.success()
    
    # Calculate statistics
    stats = handler.ventas.get_stats()
    
    print(f"\n{Colors.bold('Estadísticas Generales:')}")
    print(f"  Total de ventas: {stats['total']}")
    print(f"  Total de items vendidos: {stats['total_items']}")
    print(f"  Promedio de items por venta: {stats['promedio_items_por_venta']:.2f}")
    
    # Hot dog más vendido
    print(f"\n{Colors.bold('Hot Dogs Más Vendidos:')}")
    
    hotdog_counts = {}
    for venta in ventas:
        for item in venta.items:
            hotdog_nombre = item['hotdog_nombre']
            cantidad = item['cantidad']
            hotdog_counts[hotdog_nombre] = hotdog_counts.get(hotdog_nombre, 0) + cantidad
    
    if hotdog_counts:
        # Sort by quantity (descending)
        sorted_hotdogs = sorted(hotdog_counts.items(), key=lambda x: x[1], reverse=True)
        
        for i, (nombre, cantidad) in enumerate(sorted_hotdogs[:5], 1):  # Top 5
            print(f"  {i}. {nombre}: {cantidad} unidades")
    else:
        print("  (Sin datos)")
    
    Views.pause()
    return ActionResult.success()
