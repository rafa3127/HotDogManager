# 🌭 Hot Dog CCS - Sistema de Gestión

Sistema de gestión integral para cadena de hot dogs en Caracas. Permite administrar ingredientes, inventario, menú de productos, registrar ventas y generar reportes estadísticos con visualizaciones.

## 📖 Descripción

Hot Dog CCS es un sistema desarrollado en Python con arquitectura orientada a objetos que gestiona todos los aspectos operativos de una cadena de hot dogs:

- **Gestión de Ingredientes**: Administración completa del catálogo de ingredientes organizados por categorías (Pan, Salchicha, Toppings, Salsas, Acompañantes)
- **Control de Inventario**: Seguimiento en tiempo real del stock de cada ingrediente con alertas visuales
- **Menú Dinámico**: Creación y gestión de hot dogs con validaciones automáticas de compatibilidad
- **Ventas**: Registro individual de ventas con descuento automático de inventario
- **Simulación**: Simulación de días completos de ventas con clientes y órdenes aleatorias
- **Reportes y Estadísticas**: Generación de gráficos profesionales con matplotlib para análisis de ventas

El sistema carga datos iniciales desde GitHub y persiste cambios localmente, permitiendo fácil reset a estado inicial.

## 👥 Autor

- **Rafael Correa**

## 🔗 Repositorio

- **GitHub**: [https://github.com/rafa3127/HotDogManager](https://github.com/rafa3127/HotDogManager)

> **Nota**: Este proyecto se entrega en formato ZIP. El repositorio de GitHub contiene el código fuente completo con historial de commits y documentación adicional.

## 🎓 Información Académica

- **Institución**: Universidad Metropolitana
- **Materia**: Algoritmos y Programación (BPTSP05)
- **Trimestre**: 2526-1
- **Fecha de entrega**: 16 de noviembre de 2024

## 📁 Estructura del Proyecto

```
HotDogManager/
├── .env                          # Configuración (no versionado)
├── .env.example                  # Plantilla de configuración
├── .gitignore                    # Archivos ignorados por git
├── .python-version               # Versión de Python (3.10)
├── requirements.txt              # Dependencias del proyecto
├── config.py                     # Carga de variables de entorno
├── main.py                       # Punto de entrada principal
├── app.py                        # Setup y configuración de la aplicación
│
├── clients/                      # Sistema de datos
│   ├── external_sources/         # Clientes de fuentes externas
│   │   ├── external_source_client.py
│   │   └── github_client.py
│   ├── adapters/                 # Adapters para procesamiento de datos
│   │   ├── id_adapter.py
│   │   ├── key_normalization_adapter.py
│   │   ├── stock_initialization_adapter.py
│   │   └── ingredient_reference_adapter.py
│   ├── id_processors.py          # Generación de IDs determinísticos
│   └── data_source_client.py     # Orquestador de fuentes de datos
│
├── models/                       # Sistema de entidades
│   ├── core/                     # Core genérico (portable)
│   │   ├── base_entity.py
│   │   ├── method_registry.py
│   │   └── entity_factory.py
│   ├── schemas/                  # Inferencia de schemas
│   │   ├── ingredient_schemas.py
│   │   ├── hotdog_schemas.py
│   │   └── venta_schemas.py
│   ├── plugins/                  # Validadores y métodos
│   │   ├── ingredients/
│   │   ├── hotdogs/
│   │   └── ventas/
│   ├── entities/                 # Entity creators
│   │   ├── ingredients.py
│   │   ├── hotdogs.py
│   │   └── ventas.py
│   └── collections/              # Repository Pattern
│       ├── base_collection.py
│       ├── ingredient_collection.py
│       ├── hotdog_collection.py
│       └── venta_collection.py
│
├── handlers/                     # Unit of Work Pattern
│   └── data_handler.py
│
├── services/                     # Lógica de negocio
│   ├── ingredient_service.py
│   ├── menu_service.py
│   ├── venta_service.py
│   ├── reporting_service.py
│   └── chart_generator.py
│
├── cli/                          # Interfaz de usuario
│   ├── core/                     # Sistema CLI genérico
│   │   ├── colors.py
│   │   ├── action_result.py
│   │   ├── menu_definition.py
│   │   ├── views.py
│   │   └── router.py
│   ├── actions/                  # Actions por módulo
│   │   ├── ingredientes_actions.py
│   │   ├── menu_actions.py
│   │   ├── ventas_actions.py
│   │   └── reporting_actions.py
│   └── menus/                    # Definiciones de menús
│       ├── main_menu.py
│       ├── ingredientes_menu.py
│       ├── menu_hotdogs_menu.py
│       ├── ventas_menu.py
│       ├── reportes_menu.py
│       ├── debug_menu.py
│       └── not_found_menu.py
│
├── test/                         # Tests del sistema
│   ├── test_datasource.py
│   ├── test_entities.py
│   ├── test_collections.py
│   ├── test_ingredient_service.py
│   ├── test_menu_service.py
│   ├── test_venta_service.py
│   └── test_venta_infrastructure.py
│
├── data/                         # Datos locales (generado)
│   ├── ingredientes.json
│   ├── menu.json
│   └── ventas.json
│
├── charts/                       # Gráficos generados (generado)
│   ├── ventas_por_dia.png
│   ├── hotdogs_por_dia.png
│   ├── top_hotdogs.png
│   ├── ingredientes_consumidos.png
│   ├── ventas_por_hora.png
│   └── comparacion_fechas.png
│
├── DESARROLLO.md                 # Decisiones de diseño y desarrollo
├── README.md                     # Este archivo
├── MANUAL_USUARIO.md            # Manual de usuario del sistema
├── CLASS_DIAGRAM.md             # Diagramas de clases
└── LICENSE                       # Licencia del proyecto
```

## ⚙️ Instalación y Configuración

### Requisitos Previos

- **Python 3.10 o superior**
- **pip** (gestor de paquetes de Python)
- **Git** (para clonar el repositorio)

### Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone <url-del-repositorio>
   cd HotDogManager
   ```

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar variables de entorno:**
   
   Crear un archivo `.env` en la raíz del proyecto con la siguiente estructura:
   ```env
   GITHUB_OWNER=<owner_del_repositorio>
   GITHUB_REPO=<nombre_del_repositorio>
   GITHUB_BRANCH=<rama_a_usar>
   ```
   
   **Nota:** Puedes usar `.env.example` como plantilla.

## 🚀 Uso

### Inicio Rápido

Para ejecutar la aplicación:

```bash
python main.py
```

Esto iniciará el sistema de menús interactivo donde podrás acceder a todos los módulos.

### Resetear Datos

Si necesitas volver al estado inicial (recargar datos desde GitHub):

1. Ejecutar la aplicación
2. Ir al menú principal → Opción 9 (Debug)
3. Seleccionar opción 4 (Reset Data)
4. Confirmar el reseteo
5. Reiniciar la aplicación

**Nota:** Esto eliminará todos los datos locales (ventas, cambios de inventario, hot dogs agregados) y gráficos generados.

### Manual Completo

Para instrucciones detalladas de cada módulo, consultar:
- **[Manual de Usuario](MANUAL_USUARIO.md)** - Guía completa con ejemplos de uso

## 📊 Módulos Implementados

### 1. Gestión de Ingredientes ✅

Administra el catálogo completo de ingredientes organizados en categorías:

- Listar ingredientes por categoría
- Listar ingredientes por tipo específico
- Agregar nuevos ingredientes
- Eliminar ingredientes (con validación de dependencias)

### 2. Gestión de Inventario ✅

Control de stock en tiempo real:

- Visualizar inventario completo con código de colores
- Buscar existencia de ingrediente específico
- Actualizar stock de productos
- Verificar disponibilidad para hot dogs

### 3. Gestión del Menú ✅

Administración de hot dogs del menú:

- Ver lista completa de hot dogs
- Verificar disponibilidad de inventario
- Agregar hot dogs con validaciones:
  - Validación de tamaños (pan y salchicha)
  - Solo ingredientes registrados
  - Advertencia si no hay inventario
- Eliminar hot dogs (con confirmación)

### 4. Simulación de Ventas ✅

Simulación completa de días de ventas:

- Generación aleatoria de clientes (0-200)
- Hot dogs aleatorios por cliente (0-5)
- Descuento automático de inventario
- Reporte detallado:
  - Clientes que cambiaron de opinión
  - Clientes que no pudieron comprar
  - Hot dog más vendido
  - Ingredientes que causaron pérdidas
  - Total de acompañantes vendidos

### 5. Reportes y Estadísticas (Bono) ✅

Generación de gráficos profesionales con matplotlib:

- **Ventas por día** - Evolución temporal de ventas
- **Hot dogs vendidos por día** - Análisis de unidades vendidas
- **Top hot dogs** - Ranking de productos más populares
- **Consumo de ingredientes** - Ingredientes más utilizados
- **Distribución por hora** - Análisis de franjas horarias
- **Comparación entre fechas** - Análisis comparativo

Todos los gráficos se guardan en formato PNG en el directorio `charts/`.

## 📐 Documentación Técnica

### Arquitectura y Diseño

- **[Diagrama de Clases](CLASS_DIAGRAM.md)** - Arquitectura completa del sistema
- **[Decisiones de Diseño](DESARROLLO.md)** - Justificaciones técnicas y evolución del proyecto

### Manuales

- **[Manual de Usuario](MANUAL_USUARIO.md)** - Guía completa de uso del sistema

### Patrones de Diseño Implementados

El sistema implementa más de 25 patrones y principios de diseño orientado a objetos:

- **Repository Pattern** - Abstracción de acceso a datos
- **Unit of Work Pattern** - Transacciones coordinadas
- **Adapter Pattern** - Procesamiento de datos en cadena
- **Builder Pattern** - Construcción diferida de ventas
- **Router Pattern** - Sistema de navegación CLI
- **Service Layer Pattern** - Lógica de negocio desacoplada
- **Factory Pattern** - Generación dinámica de clases
- **Plugin Architecture** - Extensibilidad mediante plugins

## 📄 Licencia

Este proyecto está bajo la licencia especificada en el archivo [LICENSE](LICENSE.md).

---

**Desarrollado por Rafael Correa - Universidad Metropolitana - Trimestre 2526-1**
