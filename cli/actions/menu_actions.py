"""
Actions for menu management (hot dogs).

These actions handle all menu-related operations:
- Listing hot dogs
- Checking inventory availability
- Adding new hot dogs (with validations)
- Deleting hot dogs (with confirmation)

Author: Rafael Correa
Date: November 16, 2025
"""

from cli.core import ActionResult, Views, Colors
from services import MenuService, IngredientService
from .helpers import (
    get_display_categories,
    normalize_category_input,
    get_category_class_name
)


# ──────────────────────────────────────────────────────
# LISTING ACTIONS
# ──────────────────────────────────────────────────────

def action_list_hotdogs(context: dict) -> ActionResult:
    """
    Lists all hot dogs in the menu.
    
    Args:
        context: Router context with handler
        
    Returns:
        ActionResult
    """
    handler = context['handler']
    
    Views.clear_screen()
    Views.print_header("Lista de Hot Dogs en el Menú")
    
    hotdogs = MenuService.list_all(handler)
    
    if not hotdogs:
        Views.print_warning("No hay hot dogs en el menú")
        Views.pause()
        return ActionResult.success()
    
    # Display table
    print(f"\n{Colors.bold(Colors.blue('Hot Dogs disponibles:'))}")
    print()
    
    headers = ['Nombre', 'Pan', 'Salchicha', 'Toppings', 'Salsas', 'Acompañante']
    rows = []
    
    for hd in sorted(hotdogs, key=lambda x: x.nombre):
        # Extract names from references
        pan_nombre = hd.pan['nombre'] if isinstance(hd.pan, dict) else hd.pan
        salchicha_nombre = hd.salchicha['nombre'] if isinstance(hd.salchicha, dict) else hd.salchicha
        
        # Toppings
        if hd.toppings:
            toppings_str = ', '.join([
                t['nombre'] if isinstance(t, dict) else t 
                for t in hd.toppings
            ])
        else:
            toppings_str = '-'
        
        # Salsas
        if hd.salsas:
            salsas_str = ', '.join([
                s['nombre'] if isinstance(s, dict) else s 
                for s in hd.salsas
            ])
        else:
            salsas_str = '-'
        
        # Acompañante
        if hd.acompanante:
            acomp_str = hd.acompanante['nombre'] if isinstance(hd.acompanante, dict) else hd.acompanante
        else:
            acomp_str = '-'
        
        rows.append([
            hd.nombre,
            pan_nombre,
            salchicha_nombre,
            toppings_str,
            salsas_str,
            acomp_str
        ])
    
    Views.display_table(headers, rows)
    
    print(f"\n{Colors.blue(f'Total: {len(hotdogs)} hot dogs')}")
    
    Views.pause()
    return ActionResult.success()


def action_check_hotdog_availability(context: dict) -> ActionResult:
    """
    Checks if there's sufficient inventory for a specific hot dog.
    
    Args:
        context: Router context with handler
        
    Returns:
        ActionResult
    """
    handler = context['handler']
    
    Views.clear_screen()
    Views.print_header("Verificar Disponibilidad de Hot Dog")
    
    # Get hot dog name
    nombre = Views.prompt("Nombre del hot dog: ")
    
    if not nombre.strip():
        Views.print_error("Nombre no puede estar vacío")
        Views.pause()
        return ActionResult.success()
    
    # Find hot dog
    hotdog = MenuService.get_by_name(handler, nombre)
    
    if not hotdog:
        Views.print_error(f"Hot dog '{nombre}' no encontrado")
        Views.pause()
        return ActionResult.success()
    
    # Check availability
    result = MenuService.check_availability(handler, hotdog.id)
    
    print(f"\n{Colors.bold(f'Hot Dog: {hotdog.nombre}')}")
    print()
    
    if result['disponible']:
        Views.print_success("✅ Hay inventario suficiente para este hot dog")
    else:
        Views.print_warning("⚠️  Inventario INSUFICIENTE")
        print("\nIngredientes faltantes:")
        
        for faltante in result['faltantes']:
            print(f"  • {faltante['ingrediente']} ({faltante['categoria']})")
            print(f"    Necesita: {faltante['necesita']}, Disponible: {faltante['disponible']}")
    
    Views.pause()
    return ActionResult.success()


# ──────────────────────────────────────────────────────
# ADD/DELETE ACTIONS
# ──────────────────────────────────────────────────────

def action_add_hotdog(context: dict) -> ActionResult:
    """
    Adds a new hot dog to the menu with full validation.
    
    Validations:
    - Nombre único
    - Ingredientes existen
    - Tamaños coinciden (pan y salchicha) - advertencia
    - Inventario disponible - advertencia
    
    Args:
        context: Router context with handler
        
    Returns:
        ActionResult
    """
    handler = context['handler']
    
    Views.clear_screen()
    Views.print_header("Agregar Hot Dog al Menú")
    
    # ─── 1. NOMBRE ───
    nombre = Views.prompt("Nombre del hot dog: ")
    if not nombre.strip():
        Views.print_error("Nombre no puede estar vacío")
        Views.pause()
        return ActionResult.success()
    
    # ─── 2. SELECCIONAR PAN ───
    print(f"\n{Colors.bold('Seleccionar Pan:')}")
    panes = IngredientService.list_by_category(handler, 'Pan')
    
    if not panes:
        Views.print_error("No hay panes disponibles. Agrégalos primero en Gestión de Ingredientes.")
        Views.pause()
        return ActionResult.success()
    
    for i, pan in enumerate(panes, 1):
        stock = getattr(pan, 'stock', 0)
        stock_display = Colors.green(f"Stock: {stock}") if stock > 0 else Colors.red(f"Stock: {stock}")
        print(f"  {i}. {pan.nombre} ({pan.tipo}, {pan.tamano} {pan.unidad}) - {stock_display}")
    
    pan_idx = Views.prompt_int(f"Seleccione pan (1-{len(panes)}): ", min_val=1, max_val=len(panes))
    pan_seleccionado = panes[pan_idx - 1]
    
    # ─── 3. SELECCIONAR SALCHICHA ───
    print(f"\n{Colors.bold('Seleccionar Salchicha:')}")
    salchichas = IngredientService.list_by_category(handler, 'Salchicha')
    
    if not salchichas:
        Views.print_error("No hay salchichas disponibles. Agrégalas primero en Gestión de Ingredientes.")
        Views.pause()
        return ActionResult.success()
    
    for i, salchicha in enumerate(salchichas, 1):
        stock = getattr(salchicha, 'stock', 0)
        stock_display = Colors.green(f"Stock: {stock}") if stock > 0 else Colors.red(f"Stock: {stock}")
        print(f"  {i}. {salchicha.nombre} ({salchicha.tipo}, {salchicha.tamano} {salchicha.unidad}) - {stock_display}")
    
    salchicha_idx = Views.prompt_int(f"Seleccione salchicha (1-{len(salchichas)}): ", min_val=1, max_val=len(salchichas))
    salchicha_seleccionada = salchichas[salchicha_idx - 1]
    
    # ─── 4. SELECCIONAR TOPPINGS (OPCIONAL) ───
    print(f"\n{Colors.bold('Seleccionar Toppings (opcional):')}")
    toppings_disponibles = IngredientService.list_by_category(handler, 'Toppings')
    
    topping_ids = []
    if toppings_disponibles:
        for i, topping in enumerate(toppings_disponibles, 1):
            stock = getattr(topping, 'stock', 0)
            stock_display = Colors.green(f"Stock: {stock}") if stock > 0 else Colors.red(f"Stock: {stock}")
            print(f"  {i}. {topping.nombre} ({topping.tipo}) - {stock_display}")
        
        topping_input = Views.prompt("Ingrese números separados por coma (ej: 1,3,5) o Enter para omitir: ")
        
        if topping_input.strip():
            try:
                indices = [int(x.strip()) for x in topping_input.split(',')]
                for idx in indices:
                    if 1 <= idx <= len(toppings_disponibles):
                        topping_ids.append(toppings_disponibles[idx - 1].id)
                    else:
                        Views.print_warning(f"Índice {idx} fuera de rango, ignorado")
            except ValueError:
                Views.print_warning("Formato inválido, sin toppings")
                topping_ids = []
    
    # ─── 5. SELECCIONAR SALSAS (OPCIONAL) ───
    print(f"\n{Colors.bold('Seleccionar Salsas (opcional):')}")
    salsas_disponibles = IngredientService.list_by_category(handler, 'Salsa')
    
    salsa_ids = []
    if salsas_disponibles:
        for i, salsa in enumerate(salsas_disponibles, 1):
            stock = getattr(salsa, 'stock', 0)
            stock_display = Colors.green(f"Stock: {stock}") if stock > 0 else Colors.red(f"Stock: {stock}")
            print(f"  {i}. {salsa.nombre} - {stock_display}")
        
        salsa_input = Views.prompt("Ingrese números separados por coma (ej: 1,2) o Enter para omitir: ")
        
        if salsa_input.strip():
            try:
                indices = [int(x.strip()) for x in salsa_input.split(',')]
                for idx in indices:
                    if 1 <= idx <= len(salsas_disponibles):
                        salsa_ids.append(salsas_disponibles[idx - 1].id)
                    else:
                        Views.print_warning(f"Índice {idx} fuera de rango, ignorado")
            except ValueError:
                Views.print_warning("Formato inválido, sin salsas")
                salsa_ids = []
    
    # ─── 6. SELECCIONAR ACOMPAÑANTE (OPCIONAL) ───
    print(f"\n{Colors.bold('Seleccionar Acompañante (opcional):')}")
    acompanantes_disponibles = IngredientService.list_by_category(handler, 'Acompañante')
    
    acompanante_id = None
    if acompanantes_disponibles:
        print("  0. Sin acompañante")
        for i, acomp in enumerate(acompanantes_disponibles, 1):
            stock = getattr(acomp, 'stock', 0)
            stock_display = Colors.green(f"Stock: {stock}") if stock > 0 else Colors.red(f"Stock: {stock}")
            print(f"  {i}. {acomp.nombre} ({acomp.tipo}) - {stock_display}")
        
        acomp_idx = Views.prompt_int(f"Seleccione acompañante (0-{len(acompanantes_disponibles)}): ", 
                                     min_val=0, max_val=len(acompanantes_disponibles), default=0)
        
        if acomp_idx > 0:
            acompanante_id = acompanantes_disponibles[acomp_idx - 1].id
    
    # ─── 7. RESUMEN ───
    print(f"\n{Colors.bold('Resumen del hot dog:')}")
    print(f"  Nombre: {nombre}")
    print(f"  Pan: {pan_seleccionado.nombre}")
    print(f"  Salchicha: {salchicha_seleccionada.nombre}")
    
    if topping_ids:
        topping_nombres = [handler.ingredientes.get(tid).nombre for tid in topping_ids]
        print(f"  Toppings: {', '.join(topping_nombres)}")
    else:
        print(f"  Toppings: Ninguno")
    
    if salsa_ids:
        salsa_nombres = [handler.ingredientes.get(sid).nombre for sid in salsa_ids]
        print(f"  Salsas: {', '.join(salsa_nombres)}")
    else:
        print(f"  Salsas: Ninguna")
    
    if acompanante_id:
        acomp = handler.ingredientes.get(acompanante_id)
        print(f"  Acompañante: {acomp.nombre}")
    else:
        print(f"  Acompañante: Ninguno")
    
    if not Views.confirm("\n¿Guardar hot dog?"):
        Views.print_warning("Operación cancelada")
        Views.pause()
        return ActionResult.success()
    
    # ─── 8. AGREGAR HOT DOG ───
    result = MenuService.add_hotdog(
        handler,
        nombre=nombre,
        pan_id=pan_seleccionado.id,
        salchicha_id=salchicha_seleccionada.id,
        topping_ids=topping_ids if topping_ids else None,
        salsa_ids=salsa_ids if salsa_ids else None,
        acompanante_id=acompanante_id
    )
    
    if result['exito']:
        Views.print_success(f"Hot dog '{nombre}' agregado exitosamente")
        
        # Mostrar advertencias si las hay
        if result.get('advertencias'):
            print()
            for adv in result['advertencias']:
                Views.print_warning(adv)
        
        handler.commit()
    else:
        Views.print_error(result['error'])
    
    Views.pause()
    return ActionResult.success()


def action_delete_hotdog(context: dict) -> ActionResult:
    """
    Deletes a hot dog from the menu.
    
    Validates inventory:
    - If inventory available → requires confirmation
    - If no inventory → deletes directly
    
    Args:
        context: Router context with handler
        
    Returns:
        ActionResult
    """
    handler = context['handler']
    
    Views.clear_screen()
    Views.print_header("Eliminar Hot Dog del Menú")
    
    # Get hot dog name
    nombre = Views.prompt("Nombre del hot dog a eliminar: ")
    
    if not nombre.strip():
        Views.print_error("Nombre no puede estar vacío")
        Views.pause()
        return ActionResult.success()
    
    # Find hot dog
    hotdog = MenuService.get_by_name(handler, nombre)
    
    if not hotdog:
        Views.print_error(f"Hot dog '{nombre}' no encontrado")
        Views.pause()
        return ActionResult.success()
    
    # Show hot dog info
    print(f"\n{Colors.bold('Hot Dog a eliminar:')}")
    print(f"  Nombre: {hotdog.nombre}")
    
    pan_nombre = hotdog.pan['nombre'] if isinstance(hotdog.pan, dict) else hotdog.pan
    salchicha_nombre = hotdog.salchicha['nombre'] if isinstance(hotdog.salchicha, dict) else hotdog.salchicha
    
    print(f"  Pan: {pan_nombre}")
    print(f"  Salchicha: {salchicha_nombre}")
    
    # First call without confirmation (to check inventory)
    result = MenuService.delete_hotdog(handler, hotdog.id, confirmar_con_inventario=False)
    
    # If requires confirmation (has inventory)
    if result.get('requiere_confirmacion'):
        Views.print_warning(result['advertencia'])
        
        if not Views.confirm("\n¿Estás seguro de continuar?", default=False):
            Views.print_info("Operación cancelada")
            Views.pause()
            return ActionResult.success()
        
        # Confirm deletion
        result = MenuService.delete_hotdog(handler, hotdog.id, confirmar_con_inventario=True)
    
    # Check for other errors (not confirmation-related)
    elif not result['exito']:
        Views.print_error(result['error'])
        Views.pause()
        return ActionResult.success()
    
    # Process result
    if result['exito']:
        Views.print_success(f"Hot dog '{result['hotdog_eliminado'].nombre}' eliminado exitosamente")
        handler.commit()
    else:
        Views.print_error(result['error'])
    
    Views.pause()
    return ActionResult.success()
