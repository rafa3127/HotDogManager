"""
Actions for ingredient management.

These actions handle all ingredient-related operations:
- Listing by category and type
- Adding new ingredients
- Deleting ingredients (with menu validation)
- Viewing inventory

Author: Rafael Correa
Date: November 16, 2025
"""

from cli.core import ActionResult, Views, Colors
from services import IngredientService
from .helpers import (
    get_display_categories,
    normalize_category_input,
    get_category_class_name,
    get_required_fields_for_category
)


# ──────────────────────────────────────────────────────
# LISTING ACTIONS
# ──────────────────────────────────────────────────────

def action_list_by_category(context: dict) -> ActionResult:
    """
    Lists all ingredients in a selected category.
    
    Args:
        context: Router context with handler
        
    Returns:
        ActionResult
    """
    handler = context['handler']
    
    Views.clear_screen()
    Views.print_header("Listar Ingredientes por Categoría")
    
    # Get available categories (with display names)
    display_categories = get_display_categories(handler)
    
    if not display_categories:
        Views.print_error("No hay categorías disponibles")
        Views.pause()
        return ActionResult.success()
    
    # Show categories
    print("\nCategorías disponibles:")
    for i, cat in enumerate(display_categories, 1):
        print(f"  {i}. {cat}")
    
    # Select category
    choice = Views.prompt("\nSeleccione categoría (número o nombre): ")
    
    # Parse choice
    display_name = None
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(display_categories):
            display_name = display_categories[idx]
        else:
            Views.print_error("Número inválido")
            Views.pause()
            return ActionResult.success()
    except ValueError:
        # Try to match by name
        normalized = normalize_category_input(choice)
        # Check if normalized matches any class name
        class_names = [get_category_class_name(cat) for cat in display_categories]
        if normalized in class_names:
            display_name = display_categories[class_names.index(normalized)]
        else:
            Views.print_error(f"Categoría '{choice}' no encontrada")
            Views.pause()
            return ActionResult.success()
    
    # Convert to class name for handler
    categoria = get_category_class_name(display_name)
    
    # Get ingredients
    ingredientes = IngredientService.list_by_category(handler, categoria)
    
    if not ingredientes:
        Views.print_warning(f"No hay ingredientes en la categoría '{display_name}'")
        Views.pause()
        return ActionResult.success()
    
    # Display table
    print(f"\n{Colors.bold(Colors.blue(f'Ingredientes en {display_name}:'))}")
    print()
    
    headers = ['ID', 'Nombre', 'Tipo', 'Stock']
    rows = []
    
    for ing in ingredientes:
        rows.append([
            ing.id[:8] + '...',  # Truncate ID
            ing.nombre,
            getattr(ing, 'tipo', 'N/A'),
            str(getattr(ing, 'stock', 'N/A'))
        ])
    
    Views.display_table(headers, rows)
    
    Views.pause()
    return ActionResult.success()


def action_list_by_type(context: dict) -> ActionResult:
    """
    Lists all ingredients in a category filtered by type.
    
    Note: Salsa category is excluded as it uses 'base' and 'color' instead of 'tipo'.
    
    Args:
        context: Router context with handler
        
    Returns:
        ActionResult
    """
    handler = context['handler']
    
    Views.clear_screen()
    Views.print_header("Listar Ingredientes por Tipo")
    
    # Get categories (with display names) - exclude Salsa
    all_categories = get_display_categories(handler)
    display_categories = [cat for cat in all_categories if get_category_class_name(cat) != 'Salsa']
    
    if not display_categories:
        Views.print_error("No hay categorías disponibles")
        Views.pause()
        return ActionResult.success()
    
    print("\nCategorías disponibles (excluye Salsa):")
    for i, cat in enumerate(display_categories, 1):
        print(f"  {i}. {cat}")
    
    choice = Views.prompt("\nSeleccione categoría: ")
    
    display_name = None
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(display_categories):
            display_name = display_categories[idx]
        else:
            Views.print_error("Número inválido")
            Views.pause()
            return ActionResult.success()
    except ValueError:
        normalized = normalize_category_input(choice)
        class_names = [get_category_class_name(cat) for cat in display_categories]
        if normalized in class_names:
            display_name = display_categories[class_names.index(normalized)]
        else:
            Views.print_error(f"Categoría '{choice}' no encontrada")
            Views.pause()
            return ActionResult.success()
    
    categoria = get_category_class_name(display_name)
    
    # Get type
    tipo = Views.prompt("\nIngrese el tipo a buscar: ")
    
    if not tipo.strip():
        Views.print_error("Tipo no puede estar vacío")
        Views.pause()
        return ActionResult.success()
    
    # Get filtered ingredients
    ingredientes = IngredientService.list_by_type(handler, categoria, tipo)
    
    if not ingredientes:
        Views.print_warning(f"No hay ingredientes de tipo '{tipo}' en '{display_name}'")
        Views.pause()
        return ActionResult.success()
    
    # Display table
    print(f"\n{Colors.bold(Colors.blue(f'Ingredientes en {display_name} - Tipo: {tipo}'))}")
    print()
    
    headers = ['ID', 'Nombre', 'Tipo', 'Stock']
    rows = []
    
    for ing in ingredientes:
        rows.append([
            ing.id[:8] + '...',
            ing.nombre,
            getattr(ing, 'tipo', 'N/A'),
            str(getattr(ing, 'stock', 'N/A'))
        ])
    
    Views.display_table(headers, rows)
    
    Views.pause()
    return ActionResult.success()


# ──────────────────────────────────────────────────────
# INVENTORY ACTIONS
# ──────────────────────────────────────────────────────

def action_view_inventory(context: dict) -> ActionResult:
    """
    Shows full inventory with stock levels.
    
    Args:
        context: Router context with handler
        
    Returns:
        ActionResult
    """
    handler = context['handler']
    
    Views.clear_screen()
    Views.print_header("Inventario Completo")
    
    # Get display categories
    display_categories = get_display_categories(handler)
    
    for display_name in sorted(display_categories):
        categoria = get_category_class_name(display_name)
        ingredientes = IngredientService.list_by_category(handler, categoria)
        
        if ingredientes:
            print(f"\n{Colors.bold(Colors.blue(f'{display_name}:'))}")
            
            headers = ['Nombre', 'Tipo', 'Stock']
            rows = []
            
            for ing in sorted(ingredientes, key=lambda x: x.nombre):
                stock = getattr(ing, 'stock', 0)
                
                # Color code stock levels
                if stock == 0:
                    stock_display = Colors.red(f"{stock} ❌")
                elif stock < 10:
                    stock_display = Colors.yellow(f"{stock} ⚠️")
                else:
                    stock_display = Colors.green(f"{stock} ✓")
                
                rows.append([
                    ing.nombre,
                    getattr(ing, 'tipo', 'N/A'),
                    stock_display
                ])
            
            Views.display_table(headers, rows)
    
    Views.pause()
    return ActionResult.success()


def action_update_stock(context: dict) -> ActionResult:
    """
    Updates stock for a specific ingredient.
    
    Args:
        context: Router context with handler
        
    Returns:
        ActionResult
    """
    handler = context['handler']
    
    Views.clear_screen()
    Views.print_header("Actualizar Stock")
    
    # Get ingredient ID or name
    search = Views.prompt("Ingrese ID o nombre del ingrediente: ")
    
    if not search.strip():
        Views.print_error("Búsqueda no puede estar vacía")
        Views.pause()
        return ActionResult.success()
    
    # Try to find by ID first
    ingrediente = handler.ingredientes.get(search)
    
    # If not found by ID, try by name
    if not ingrediente:
        # Search by name in all categories
        display_categories = get_display_categories(handler)
        for display_name in display_categories:
            cat = get_category_class_name(display_name)
            found = handler.ingredientes.get_by_name(search, cat)
            if found:
                ingrediente = found
                break
    
    if not ingrediente:
        Views.print_error(f"Ingrediente '{search}' no encontrado")
        Views.pause()
        return ActionResult.success()
    
    # Show current stock
    current_stock = getattr(ingrediente, 'stock', 0)
    print(f"\nIngrediente: {Colors.bold(ingrediente.nombre)}")
    print(f"Stock actual: {Colors.blue(str(current_stock))}")
    
    # Get change amount
    change = Views.prompt_int(
        "\nCantidad a agregar (negativo para restar): ",
        default=0
    )
    
    if change == 0:
        Views.print_info("No se realizaron cambios")
        Views.pause()
        return ActionResult.success()
    
    # Update stock
    result = IngredientService.update_stock(handler, ingrediente.id, change)
    
    if result['exito']:
        Views.print_success(
            f"Stock actualizado: {result['stock_anterior']} → {result['stock_nuevo']}"
        )
        handler.commit()
    else:
        Views.print_error(result['error'])
    
    Views.pause()
    return ActionResult.success()


# ──────────────────────────────────────────────────────
# ADD/DELETE ACTIONS
# ──────────────────────────────────────────────────────

def action_add_ingredient(context: dict) -> ActionResult:
    """
    Adds a new ingredient to the catalog.
    
    Args:
        context: Router context with handler
        
    Returns:
        ActionResult
    """
    handler = context['handler']
    
    Views.clear_screen()
    Views.print_header("Agregar Ingrediente")
    
    # Get display categories (with proper names)
    display_categories = get_display_categories(handler)
    
    print("\nCategorías disponibles:")
    for i, cat in enumerate(display_categories, 1):
        print(f"  {i}. {cat}")
    
    choice = Views.prompt("\nSeleccione categoría: ")
    
    # Parse choice
    display_name = None
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(display_categories):
            display_name = display_categories[idx]
        else:
            Views.print_error("Número inválido")
            Views.pause()
            return ActionResult.success()
    except ValueError:
        # Try to match by name
        normalized = normalize_category_input(choice)
        class_names = [get_category_class_name(cat) for cat in display_categories]
        if normalized in class_names:
            display_name = display_categories[class_names.index(normalized)]
        else:
            Views.print_error(f"Categoría '{choice}' no encontrada")
            Views.pause()
            return ActionResult.success()
    
    # Convert display name to class name
    categoria = get_category_class_name(display_name)
    
    # Get ingredient details
    print(f"\n{Colors.bold('Datos del nuevo ingrediente:')}")
    
    nombre = Views.prompt("Nombre: ")
    if not nombre.strip():
        Views.print_error("Nombre no puede estar vacío")
        Views.pause()
        return ActionResult.success()
    
    stock = Views.prompt_int("Stock inicial: ", min_val=0, default=0)
    
    # Build kwargs starting with stock (common to all)
    kwargs = {'stock': stock}
    
    # Get required fields for this category
    required_fields = get_required_fields_for_category(categoria)
    
    # Salsa: base and color
    if 'base' in required_fields:
        base = Views.prompt("Base: ")
        color = Views.prompt("Color: ")
        kwargs['base'] = base
        kwargs['color'] = color
    
    # Pan, Salchicha, Acompanante: tamano and unidad
    elif 'tamano' in required_fields:
        # These categories also have 'tipo'
        tipo = Views.prompt("Tipo: ")
        tamano = Views.prompt_int("Tamaño: ", min_val=1, default=6)
        unidad = Views.prompt("Unidad (ej: pulgadas, gramos, mililitros): ", default="pulgadas")
        kwargs['tipo'] = tipo
        kwargs['tamano'] = tamano
        kwargs['unidad'] = unidad
    
    # Toppings: tipo and presentacion
    elif 'presentacion' in required_fields:
        tipo = Views.prompt("Tipo: ")
        presentacion = Views.prompt("Presentación: ")
        kwargs['tipo'] = tipo
        kwargs['presentacion'] = presentacion
    
    # Fallback: just tipo (shouldn't happen with current categories)
    else:
        tipo = Views.prompt("Tipo: ")
        kwargs['tipo'] = tipo
    
    # Confirm
    print(f"\n{Colors.bold('Resumen:')}")
    print(f"  Categoría: {display_name}")  # Show display name to user
    print(f"  Nombre: {nombre}")
    print(f"  Stock: {stock}")
    
    # Show only the fields that were actually collected
    for k, v in kwargs.items():
        if k != 'stock':  # Skip stock (already shown)
            print(f"  {k.capitalize()}: {v}")
    
    if not Views.confirm("\n¿Guardar ingrediente?"):
        Views.print_warning("Operación cancelada")
        Views.pause()
        return ActionResult.success()
    
    # Add ingredient
    result = IngredientService.add_ingredient(
        handler,
        categoria=categoria,
        nombre=nombre,
        **kwargs
    )
    
    if result['exito']:
        Views.print_success(f"Ingrediente '{nombre}' agregado exitosamente")
        handler.commit()
    else:
        Views.print_error(result['error'])
    
    Views.pause()
    return ActionResult.success()


def action_delete_ingredient(context: dict) -> ActionResult:
    """
    Deletes an ingredient from the catalog.
    
    Validates if ingredient is used in menu and asks for confirmation.
    
    Args:
        context: Router context with handler
        
    Returns:
        ActionResult
    """
    handler = context['handler']
    
    Views.clear_screen()
    Views.print_header("Eliminar Ingrediente")
    
    # Get ingredient ID or name
    search = Views.prompt("Ingrese ID o nombre del ingrediente: ")
    
    if not search.strip():
        Views.print_error("Búsqueda no puede estar vacía")
        Views.pause()
        return ActionResult.success()
    
    # Try to find by ID first
    ingrediente = handler.ingredientes.get(search)
    
    # If not found by ID, try by name
    if not ingrediente:
        display_categories = get_display_categories(handler)
        for display_name in display_categories:
            cat = get_category_class_name(display_name)
            found = handler.ingredientes.get_by_name(search, cat)
            if found:
                ingrediente = found
                break
    
    if not ingrediente:
        Views.print_error(f"Ingrediente '{search}' no encontrado")
        Views.pause()
        return ActionResult.success()
    
    # Show ingredient info
    print(f"\n{Colors.bold('Ingrediente a eliminar:')}")
    print(f"  Nombre: {ingrediente.nombre}")
    print(f"  Tipo: {getattr(ingrediente, 'tipo', 'N/A')}")
    print(f"  Categoría: {ingrediente.entity_type}")
    
    # First call without confirmation (to check if menu items affected)
    result = IngredientService.delete_ingredient(
        handler,
        ingrediente_id=ingrediente.id,
        confirmar_eliminar_hotdogs=False
    )
    
    # If requires confirmation (menu items affected)
    if result.get('requiere_confirmacion'):
        hotdogs_afectados = result['hotdogs_afectados']
        
        Views.print_warning(
            f"\n⚠️  Este ingrediente es usado por {len(hotdogs_afectados)} hot dog(s):"
        )
        for hd_id in hotdogs_afectados:
            hd = handler.menu.get(hd_id)
            if hd:
                print(f"  - {hd.nombre}")
        
        print("\n❌ Si eliminas este ingrediente, también se eliminarán estos hot dogs.")
        
        if not Views.confirm("\n¿Estás seguro de continuar?", default=False):
            Views.print_info("Operación cancelada")
            Views.pause()
            return ActionResult.success()
        
        # Confirm deletion with menu items
        result = IngredientService.delete_ingredient(
            handler,
            ingrediente_id=ingrediente.id,
            confirmar_eliminar_hotdogs=True
        )
    
    # Check for other errors (not confirmation-related)
    elif not result['exito']:
        Views.print_error(result['error'])
        Views.pause()
        return ActionResult.success()
    
    # Process result
    if result['exito']:
        Views.print_success(f"Ingrediente '{result['ingrediente_eliminado'].nombre}' eliminado")
        
        if result.get('hotdogs_eliminados'):
            Views.print_warning(
                f"También se eliminaron {len(result['hotdogs_eliminados'])} hot dog(s)"
            )
        
        handler.commit()
    else:
        Views.print_error(result['error'])
    
    Views.pause()
    return ActionResult.success()
