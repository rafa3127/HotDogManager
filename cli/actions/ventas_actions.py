"""
Actions for sales management (ventas).

These actions handle sales-related operations:
- Registering individual sales (manual)
- Viewing sales history
- Sales statistics

Author: Rafael Correa
Date: November 16, 2025
"""

from cli.core import ActionResult, Views, Colors
from services import VentaService, MenuService


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


def action_view_sales_by_date(context: dict) -> ActionResult:
    """
    Shows sales filtered by date.
    
    Args:
        context: Router context with handler
        
    Returns:
        ActionResult
    """
    handler = context['handler']
    
    Views.clear_screen()
    Views.print_header("Ventas por Fecha")
    
    fecha = Views.prompt("Ingrese fecha (YYYY-MM-DD) o parte (ej: 2024-11): ")
    
    if not fecha.strip():
        Views.print_error("Fecha no puede estar vacía")
        Views.pause()
        return ActionResult.success()
    
    # Filter sales by date
    ventas_filtradas = handler.ventas.get_by_date(fecha)
    
    if not ventas_filtradas:
        Views.print_warning(f"No hay ventas para la fecha '{fecha}'")
        Views.pause()
        return ActionResult.success()
    
    print(f"\n{Colors.bold(Colors.blue(f'Ventas encontradas: {len(ventas_filtradas)}'))}")
    print()
    
    for venta in ventas_filtradas:
        print(f"{Colors.bold('─' * 60)}")
        print(f"{Colors.bold('Fecha:')} {venta.fecha}")
        print(f"{Colors.bold('Items:')}")
        
        for item in venta.items:
            print(f"  • {item['hotdog_nombre']} x {item['cantidad']}")
        
        total_items = sum(item['cantidad'] for item in venta.items)
        print(f"{Colors.blue(f'Total: {total_items} hot dogs')}")
        print()
    
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
