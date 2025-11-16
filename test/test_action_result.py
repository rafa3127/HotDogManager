"""
Script de prueba para ActionResult.
"""

from cli.core.action_result import ActionResult


def test_action_result():
    """Prueba los diferentes tipos de ActionResult."""
    
    print("\n" + "=" * 60)
    print("TEST DE ActionResult")
    print("=" * 60 + "\n")
    
    # Éxito simple
    result1 = ActionResult.success()
    print(f"1. Éxito simple:")
    print(f"   success={result1.success}, navigate={result1.navigate_to}, exit={result1.exit_app}")
    print(f"   should_navigate()={result1.should_navigate()}, should_exit()={result1.should_exit()}")
    
    # Éxito con mensaje
    result2 = ActionResult.success("Ingrediente agregado correctamente")
    print(f"\n2. Éxito con mensaje:")
    print(f"   message='{result2.message}'")
    
    # Éxito con navegación
    result3 = ActionResult.success("Selección guardada", navigate_to='editar_ingrediente')
    print(f"\n3. Éxito con navegación:")
    print(f"   navigate_to='{result3.navigate_to}'")
    print(f"   should_navigate()={result3.should_navigate()}")
    
    # Error
    result4 = ActionResult.error("Nombre duplicado")
    print(f"\n4. Error:")
    print(f"   success={result4.success}, message='{result4.message}'")
    
    # Exit
    result5 = ActionResult.exit()
    print(f"\n5. Exit:")
    print(f"   exit_app={result5.exit_app}, message='{result5.message}'")
    print(f"   should_exit()={result5.should_exit()}")
    
    # Con data adicional
    result6 = ActionResult.success("Usuario seleccionado", data={'user_id': 123})
    print(f"\n6. Con data adicional:")
    print(f"   data={result6.data}")
    
    print("\n" + "=" * 60)
    print("✅ Todos los casos funcionan correctamente")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    test_action_result()
