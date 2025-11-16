"""
Script de prueba para el sistema de colores.
"""

from cli.core.colors import Colors


def test_colors():
    """Prueba todos los colores disponibles."""
    
    print("\n" + "=" * 60)
    print("TEST DE COLORES")
    print("=" * 60 + "\n")
    
    # Colores básicos
    print("Colores básicos:")
    print(f"  {Colors.red('Rojo')}")
    print(f"  {Colors.green('Verde')}")
    print(f"  {Colors.yellow('Amarillo')}")
    print(f"  {Colors.blue('Azul')}")
    print(f"  {Colors.magenta('Magenta')}")
    print(f"  {Colors.cyan('Cyan')}")
    print(f"  {Colors.gray('Gris')}")
    print(f"  {Colors.white('Blanco')}")
    
    # Estilos
    print("\nEstilos:")
    print(f"  {Colors.bold('Negrita')}")
    print(f"  {Colors.underline('Subrayado')}")
    
    # Combinaciones
    print("\nCombinaciones:")
    print(f"  {Colors.bold(Colors.red('Rojo + Negrita'))}")
    print(f"  {Colors.bold(Colors.green('Verde + Negrita'))}")
    print(f"  {Colors.underline(Colors.blue('Azul + Subrayado'))}")
    
    # Semánticas
    print("\nFormatos semánticos:")
    print(f"  {Colors.success('✅ Operación exitosa')}")
    print(f"  {Colors.error('❌ Error crítico')}")
    print(f"  {Colors.warning('⚠️  Advertencia importante')}")
    print(f"  {Colors.info('ℹ️  Información adicional')}")
    print(f"  {Colors.header('📋 Título de Sección')}")
    
    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    test_colors()
