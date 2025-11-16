"""
Hot Dog CCS - Main Entry Point

Sistema de gestión para cadena de hot dogs en Caracas.
Permite administrar ingredientes, inventario, menú, ventas y reportes.

Author: Rafael Correa
Date: November 16, 2025
"""

from app import initialize_application, run_cli


def main():
    """
    Main entry point of the application.
    
    Initializes the complete system (data sources, entities, handler)
    and runs the CLI interface.
    """
    try:
        # Initialize application (data sources + entities + handler)
        handler, entity_classes = initialize_application(force_external=False)
        
        # Run CLI (will be implemented when menus are ready)
        run_cli(handler, entity_classes)
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        
    except Exception as e:
        print(f"\n\n❌ Critical error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
