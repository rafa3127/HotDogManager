# DESARROLLO.md - Hot Dog CCS 🌭

## Descripción del Proyecto

Sistema de gestión integral para una cadena de hot dogs en Caracas. Permite administrar ingredientes, controlar inventario, gestionar el menú de productos, simular días de ventas con clientes aleatorios y generar reportes estadísticos visuales. El sistema carga datos iniciales desde un repositorio de GitHub y persiste los cambios localmente sin modificar el origen remoto.

**Tecnologías**: Python 3.x con POO, requests para API calls, matplotlib para visualización de datos.

**Arquitectura**: Sistema en capas con separación clara entre datos (collections + handler), lógica de negocio (services) y presentación (CLI con routing).

---

## Plan de Desarrollo

Este documento contiene el plan de trabajo técnico, checklist de tareas y registro de decisiones de diseño tomadas durante el desarrollo.

---

## Fase 1: Infraestructura de Datos

### Objetivos
Construir la base del sistema de persistencia y acceso a datos con abstracción completa de fuentes externas y sistema de plugins genérico para cualquier tipo de entidad del dominio.

### Tareas
- [x] Clase abstracta para clientes de fuentes externas (`ExternalSourceClient`)
- [x] Cliente de GitHub que implementa la interfaz abstracta
- [x] Cliente de fuente de datos (`DataSourceClient`) que:
  - [x] Acepta múltiples fuentes externas (una por colección)
  - [x] Maneja fallback automático a archivos locales
  - [x] Almacena datos en memoria para acceso rápido
  - [x] Persiste cambios en archivos JSON locales
- [x] Sistema de configuración con variables de entorno (`.env`)
- [ ] Sistema genérico de entidades con Plugin Architecture:
  - [x] Core genérico reutilizable para cualquier dominio
  - [x] Clase base `Entity` (independiente del dominio)
  - [x] `MethodRegistry` (registro centralizado de métodos/validadores)
  - [x] `EntityFactory` (generador de clases dinámicas)
  - [ ] Schemas por tipo de entidad (Ingredientes, HotDogs, Ventas)
  - [ ] Plugins por entidad específica
  - [ ] Exportar entidades generadas
- [ ] Sistema de colecciones genérico con operaciones CRUD
- [ ] Colecciones especializadas por tipo de dato
- [ ] Handler central que orqueste todas las colecciones
- [ ] Testing manual del flujo completo

---

## Fase 2: Servicios de Negocio

### Objetivos
Implementar la lógica de orquestación entre colecciones y las validaciones de negocio específicas.

### Tareas
- [ ] Servicio de gestión de ingredientes (listar, agregar, eliminar con cascada)
- [ ] Servicio de gestión de inventario (visualizar, buscar, actualizar)
- [ ] Servicio de gestión de menú (listar, agregar con validaciones, eliminar)
- [ ] Servicio de procesamiento de ventas
- [ ] Utilidades de formateo y validación

---

## Fase 3: CLI con Sistema de Routing

### Objetivos
Construir la interfaz de usuario con un sistema de routing que abstraiga la navegación entre menús.

### Tareas
- [ ] Sistema core de routing (router, rutas, opciones)
- [ ] Tipos de rutas especializadas (estándar, con tablas)
- [ ] Validadores de input de usuario
- [ ] Implementación de CLI principal
- [ ] Configuración de todas las rutas del sistema

---

## Fase 4: Simulador de Ventas

### Objetivos
Implementar la lógica de simulación de un día de ventas con valores aleatorios.

### Tareas
- [ ] Servicio de simulación con generación de clientes y órdenes aleatorias
- [ ] Validación de inventario y procesamiento de ventas
- [ ] Cálculo de métricas del día (clientes perdidos, más vendido, etc.)

---

## Fase 5: Gráficos y Estadísticas

### Objetivos
Visualizar métricas acumuladas de múltiples días simulados usando matplotlib.

### Tareas
- [ ] Servicio de generación de gráficos con matplotlib
- [ ] Integración con CLI

---

## Fase 6: Documentación y Testing

### Objetivos
Completar documentación, probar

### Tareas
- [ ] Documentación de código (docstrings, comentarios)
- [ ] Documentación del proyecto (README, manual)

---

## Decisiones de Diseño y Notas

### Arquitectura General
- **UUID como identificadores**: se usará UUID v4 para todos los IDs en lugar de nombres o IDs secuenciales para evitar colisiones y facilitar el mapeo inicial desde GitHub.
- **Mapeo nombre→ID solo en carga inicial**: Las referencias por nombre del JSON de GitHub se convierten a IDs una sola vez. Después todo trabaja con IDs.
- **Separación de concerns**: Tres capas bien definidas (Data, Business, Presentation) para facilitar testing y mantenimiento.

### Persistencia
- **GitHub como source of truth inicial**: Al hacer reset, siempre se parte de los datos de GitHub.
- **Archivos locales para cambios**: Todos los cambios del usuario se guardan solo localmente, nunca se suben a GitHub.
- **Fallback automático**: Si GitHub falla, el sistema carga automáticamente desde archivos locales.

### CLI
- **Sistema de routing**: Implementamos un router similar a frameworks web para abstraer la navegación entre menús.
- **Validación de inputs**: Todas las entradas del usuario se validan con try-catch para nunca crashear el programa.
- **Confirmaciones para acciones destructivas**: Eliminar ingredientes, eliminar hot dogs con inventario, reset de datos.

---


## Notas de Desarrollo - Fase 1

### Abstracción de Fuentes Externas
**Implementación:** Creada una arquitectura pluggable donde cada fuente de datos externa (GitHub, MongoDB, BigQuery, etc.) implementa la interfaz `ExternalSourceClient` con un método `fetch_data(identifier, **kwargs)`. Esto permite:
- Cambiar la fuente de datos sin modificar el código del cliente
- Usar diferentes fuentes para diferentes colecciones (ej: ingredientes de GitHub, ventas de MongoDB)
- Extensibilidad: agregar nuevas fuentes solo requiere implementar la interfaz

**Estructura:**
```
ExternalSourceClient (Abstract)
    ├── GitHubClient
    ├── MongoClient (Si se quisiera extender)
    └── CualquierFuenteExternaClient (Si se quisiera extender)
```

### DataSourceClient
**Decisión:** El `DataSourceClient` acepta un diccionario `{nombre_colección: external_client}` en su método `initialize()`. Esto permite máxima flexibilidad:
```python
data_source.initialize({
    'ingredientes': github_client,
    'menu': github_client,
    'ventas': mongo_client  # Diferente fuente
})
```

**Flujo de datos:**
1. Intenta cargar desde archivos locales (cache)
2. Si no existe o se fuerza con `force_external=True`, descarga de fuente externa
3. Guarda automáticamente en local como fallback
4. Todo queda en memoria (`_data_store`) para acceso rápido
5. Método `save()` actualiza memoria + persiste en archivo local

**TODO:** Cuando se implementen Collections, refactorizar para que cada Collection encapsule su fuente externa en lugar de pasar diccionarios de strings.

### Configuración con Environment Variables
**Implementación:** Usamos `python-dotenv` para manejar configuración sensible:
- `.env` → valores reales (ignorado por git)
- `.env.example` → plantilla versionada
- `config.py` → carga y expone las variables

**Ventajas:**
- No commitear credenciales
- Fácil cambiar configuración entre ambientes (dev/prod)
- Valores por defecto en `config.py` como fallback

### Sistema Genérico de Entidades con Plugin Architecture

**Decisión:** Implementamos un sistema completamente genérico de entidades reutilizable para cualquier dominio (Hot Dogs, tienda de mascotas, biblioteca, etc.) usando Plugin Architecture con Registry Pattern.

**Arquitectura de 3 Capas:**

1. **Core (genérico y reutilizable)**:
   - `Entity`: Clase base ultra-genérica con solo id y entity_type
   - `MethodRegistry`: Sistema centralizado de registro de métodos/validadores
   - `EntityFactory`: Generador de clases dinámicas con inyección de métodos

2. **Domain (específico del proyecto)**:
   - `Schemas`: Definen qué propiedades tiene cada tipo de entidad
   - `Plugins`: Registran métodos y validadores específicos de cada entidad

3. **Generated (output del sistema)**:
   - Clases concretas generadas (Pan, HotDog)

**Flujo de ejecución:**
1. Al importar plugins, se ejecutan los registros en `MethodRegistry`
2. Al importar entities, el factory:
   - Lee los schemas
   - Genera clases con `make_dataclass()`
   - Inyecta métodos y validadores del registry usando `setattr()`
3. Las clases generadas se exportan desde `models/__init__.py`
4. El resto del sistema usa estas clases sin saber que fueron generadas

**Estructura de directorios:**
```
models/
├── core/                       # ← Genérico, portable a otros proyectos
│   ├── base_entity.py         
│   ├── method_registry.py     
│   └── entity_factory.py      
├── schemas/                    # ← Específico del dominio
│   ├── ingredient_schemas.py
│   ├── hotdog_schemas.py
│   └── sale_schemas.py
├── plugins/                    # ← Específico del dominio
│   ├── ingredients/
│   ├── hotdogs/
│   └── sales/
├── entities/                   # ← Generado, exportable
│   ├── ingredients.py
│   ├── hotdogs.py
└── __init__.py
```

**Ventajas:**

*Para el proyecto actual:*
- Reutilizamos la misma infraestructura para ingredientes, hot dogs, ventas, inventario
- Menos código
- Consistencia: todas las entidades funcionan igual

*Para reutilización futura:*
- El core (Entity, MethodRegistry, EntityFactory) es 100% portable
- Cambiar de dominio = cambiar schemas y plugins solamente
- Ejemplo: Tienda de mascotas solo requiere crear `pet_schemas.py` y `pet_plugins/`

*Para evaluación académica:*
- Demuestra arquitectura de software avanzada
- Máxima separación de concerns
- Extensibilidad sin modificar código existente (Open/Closed Principle)

**Trade-offs:**
- Mayor complejidad inicial
- Curva de aprendizaje más pronunciada para entender el sistema
- Debugging requiere entender la inyección dinámica

**Conceptos de POO y Patrones aplicados:**
- **Registry Pattern**: MethodRegistry centraliza registro de funcionalidad
- **Plugin Architecture**: Extensibilidad mediante plugins desacoplados
- **Factory Pattern**: EntityFactory genera clases bajo demanda
- **Metaprogramming**: Creación y modificación de clases en runtime
- **Reflection**: Inspección y modificación dinámica (`setattr`, `getattr`)
- **Dynamic Method Injection**: Agregar métodos después de crear clase
- **Dataclasses**: Generación automática de métodos especiales
- **Inversion of Control**: El registry controla qué funcionalidad tiene cada clase
- **Open/Closed Principle**: Abierto a extensión (nuevos plugins), cerrado a modificación (core no cambia)
- **Separation of Concerns**: Core, schemas y plugins están completamente desacoplados
- **Single Responsibility**: Cada componente tiene una única responsabilidad
- **Dependency Injection**: Factory recibe dependencies (schemas, registry)

**Reutilización del código:**
El módulo `models/core/` completo puede extraerse y usarse en:
- Sistema de biblioteca (Book, Author, Loan)
- Tienda de mascotas (Pet, Owner, Appointment)
- Sistema de inventario genérico
- CRM (Customer, Lead, Opportunity)
- Cualquier dominio que necesite entidades dinámicas

**Justificación académica:** 
Este diseño va más allá de herencia básica y demuestra:
1. Comprensión profunda de POO avanzada
2. Conocimiento de patrones de diseño profesionales
3. Capacidad de abstraer y generalizar soluciones
4. Pensamiento arquitectónico para sistemas escalables y mantenibles
5. Aplicación de principios SOLID

El sistema es funcionalmente idéntico a usar clases normales, pero arquitectónicamente superior para extensibilidad y mantenimiento a largo plazo.




**Última actualización**: [NOV 12, 2025] - [Rafael Correa]

