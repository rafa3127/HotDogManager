# DESARROLLO.md - Hot Dog CCS 🌭

## Descripción del Proyecto

Sistema de gestión integral para una cadena de hot dogs en Caracas. Permite administrar ingredientes, controlar inventario, gestionar el menú de productos, simular días de ventas con clientes aleatorios y generar reportes estadísticos visuales. El sistema carga datos iniciales desde un repositorio de GitHub y persiste los cambios localmente sin modificar el origen remoto.

**Tecnologías**: Python 3.x con POO, requests para API calls, matplotlib para visualización de datos.

**Arquitectura**: Sistema en capas con separación clara entre datos (collections + handler), lógica de negocio (services) y presentación (CLI con routing).

---

## Plan de Desarrollo

Este documento contiene el plan de trabajo técnico, checklist de tareas y registro de decisiones de diseño tomadas durante el desarrollo.

---

## Fase 1: Infraestructura de Datos ✅ COMPLETADA

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
- [x] Sistema genérico de entidades con Plugin Architecture:
  - [x] Core genérico reutilizable para cualquier dominio
  - [x] Clase base `Entity` (independiente del dominio)
  - [x] `MethodRegistry` con soporte de validadores múltiples composables
  - [x] `EntityFactory` con wrapper automático para herencia de validación
  - [x] Schemas con inferencia dinámica desde datos
  - [x] Plugins completos: 6 ingredientes + 1 hotdog
  - [x] Funciones de creación de entidades exportadas
  - [x] Tests exhaustivos del sistema completo
- [ ] Sistema de colecciones genérico con operaciones CRUD
- [ ] Colecciones especializadas por tipo de dato
- [ ] Handler central que orqueste todas las colecciones

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
Completar documentación, probar en laboratorio y preparar defensa.

### Tareas
- [ ] Documentación de código (docstrings, comentarios)
- [ ] Documentación del proyecto (README, manual)
- [ ] Testing en laboratorio
- [ ] Ensayo de defensa

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

---

## Sistema Genérico de Entidades con Plugin Architecture

### Visión General

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
   - Clases concretas generadas (Pan, HotDog, VentaRegistro, etc.)

---

### Decisiones Arquitectónicas Detalladas

#### 1. Validadores Múltiples Composables

**Decisión:** Modificar `MethodRegistry` para soportar múltiples validadores por tipo que se componen automáticamente.

**Implementación:**
- `_validators` cambió de `Dict[str, Callable]` a `Dict[str, List[Callable]]`
- `register_validator()` agrega validadores a una lista en vez de sobrescribir
- `get_validator()` retorna un `composed_validator` que ejecuta todos en secuencia
- Cada validador puede lanzar `ValueError` independientemente

**Ventajas:**
- Validadores modulares (un concern por función)
- Fácil agregar/quitar validaciones sin tocar otros validadores
- DRY - no hay código duplicado de validación

**Ejemplo:**
```python
# Pan tiene 2 validadores específicos que se suman
MethodRegistry.register_validator('Pan', validate_pan_tamaño)
MethodRegistry.register_validator('Pan', validate_pan_unidad)
# Se ejecutan ambos automáticamente
```

**Fecha:** NOV 13, 2025

---

#### 2. Herencia Automática de Validadores (Wrapper en Factory)

**Decisión:** El factory inyecta un wrapper que automáticamente llama `base_class.validate()` antes de ejecutar validadores específicos.

**Implementación:**
```python
def wrapped_validator(self) -> bool:
    # Automáticamente llama validación de clase padre
    if hasattr(base_class, 'validate') and base_class != Entity:
        base_class.validate(self)
    
    # Luego ejecuta validadores específicos
    return validator(self)
```

**Ventajas:**
- NO necesitas `super().validate()` explícito en plugins
- Validación jerárquica automática (base → específico)
- Plugins más limpios y simples

**Ejemplo de flujo:**
```python
# pan.validate() ejecuta automáticamente:
# 1. Ingredient.validate() (automático via wrapper)
#    → validate_ingredient_nombre()
# 2. Pan validators (composed)
#    → validate_pan_tamaño()
#    → validate_pan_unidad()
```

**Fecha:** NOV 13, 2025

---

#### 3. Schemas con Inferencia Dinámica desde Datos

**Decisión:** Schemas se infieren automáticamente desde raw data en lugar de hardcodear.

**Implementación:**
- `infer_schemas_from_data(raw_data)`: Lee estructura de JSON y extrae propiedades
- `find_common_properties(schemas)`: Detecta propiedades compartidas entre categorías
- `get_ingredient_schemas(raw_data=None)`: Retorna `(specific_schemas, common_props)` con inferencia o fallback

**Ventajas:**
- 100% data-driven - se adapta a cambios en GitHub automáticamente
- No hardcodeas estructura - funciona con datos futuros
- Fallback garantiza que funciona sin conexión

**Trade-offs:**
- Asume que primer item tiene todas las propiedades
- No valida tipos (todo es `Any`)
- Requiere datos bien formados

**Estructuras soportadas:**
- **Grouped** (ingredientes): `[{Categoria: "Pan", Opciones: [{props}]}]`
- **Flat** (menu): `[{props directos}]`

**Fecha:** NOV 13, 2025

---

#### 4. Clases Base Intermedias con Propiedades Comunes

**Decisión:** Crear clase base `Ingredient` que contiene propiedades comunes (nombre) y todas las categorías heredan de ella.

**Implementación:**
- `create_base_class('Ingredient', common_props)`: Crea clase intermedia
- Todas las categorías específicas heredan: `Pan(Ingredient)`, `Salchicha(Ingredient)`, etc.
- Factory detecta e inyecta validador de `Ingredient` también

**Ventajas:**
- DRY - propiedades comunes solo se definen una vez
- Herencia POO real: `issubclass(Pan, Ingredient)` es True
- Validación jerárquica natural

**Jerarquía resultante:**
```
Entity (core genérico)
  ↑
Ingredient (base con 'nombre')
  ↑
Pan (específico: tipo, tamaño, unidad)
```

**Fecha:** NOV 13, 2025

---

#### 5. Funciones de Creación con Parámetros (No Import-Time)

**Decisión:** Entities son funciones que reciben `raw_data` como parámetro en vez de crear clases al importar el módulo.

**Implementación:**
```python
def create_ingredient_entities(raw_data=None):
    # Importa plugins DENTRO de función (evita circulares)
    import models.plugins.ingredients
    
    # Infiere schemas
    schemas, common = get_ingredient_schemas(raw_data)
    
    # Crea clases
    Ingredient = create_base_class('Ingredient', common)
    entities = create_entities_from_schemas(schemas, base_class=Ingredient)
    
    return Ingredient, Pan, Salchicha, Topping, Salsa, Acompañante
```

**Ventajas:**
- Independiente de DataSource - solo recibe data
- Evita imports circulares (plugins dentro de función)
- Testeable con mock data
- Lazy - clases se crean cuando quieras
- Control centralizado en app.py

**Uso en app.py:**
```python
raw_data = data_source.get('ingredientes')
Ingredient, Pan, Salchicha, ... = create_ingredient_entities(raw_data)
```

**Fecha:** NOV 13, 2025

---

#### 6. Imports de Plugins Dentro de Funciones

**Decisión:** Importar plugins dentro de `create_X_entities()` en vez de top-level imports.

**Problema que resuelve:** Imports circulares
- `models/__init__.py` importa `entities/ingredients.py`
- Si `entities/ingredients.py` importa `plugins/ingredients/__init__.py` al top-level
- Y `plugins` necesita algo de `models`
- → Circular import!

**Solución:**
```python
def create_ingredient_entities(raw_data=None):
    import models.plugins.ingredients  # ← Dentro de función
    # ...
```

**Ventajas:**
- Rompe el ciclo de imports
- Plugins se registran justo antes de crear clases
- Funciona sin problemas

**Fecha:** NOV 13, 2025

---

#### 7. Un Schema por Tipo de Colección (No Generalizar)

**Decisión:** Cada tipo de colección tiene su propio módulo de schema con lógica específica.

**Implementación:**
- `ingredient_schemas.py`: Lógica para estructura agrupada
- `hotdog_schemas.py`: Lógica para estructura flat
- Cada uno con su función `get_X_schemas(raw_data=None)`

**Alternativa rechazada:** Crear un "universal schema inferrer" genérico

**Por qué NO generalizar:**
- Solo 3 estructuras diferentes (ingredientes, hotdogs, ventas)
- Cada una tiene lógica única de inferencia
- Over-engineering crear abstracción para 3 casos
- Simplicidad > abstracción excesiva

**Ventajas:**
- Simple y explícito
- Cada módulo es independiente
- Fácil de entender y mantener
- Lógica específica por estructura

**Fecha:** NOV 13, 2025

---

#### 8. Validadores Sin Registrar Base para Cada Hijo

**Decisión:** El validador base (`Ingredient`) NO se registra explícitamente para cada tipo hijo - solo se registra para 'Ingredient'.

**Implementación:**
- `ingredient_base_plugin.py` registra solo para tipo `'Ingredient'`
- `pan_plugin.py` registra solo para tipo `'Pan'`
- Factory automáticamente compone: Ingredient.validate() + Pan validators

**Alternativa rechazada:** Registrar base para todos los hijos
```python
# ❌ NO hacemos esto:
for entity_type in ['Pan', 'Salchicha', ...]:
    MethodRegistry.register_validator(entity_type, validate_ingredient_nombre)
```

**Por qué:**
- Herencia POO maneja la composición naturalmente
- Wrapper del factory llama `base_class.validate()` automáticamente
- Menos código, más limpio
- Más mantenible

**Fecha:** NOV 13, 2025

---

#### 9. Plugins con Métodos Específicos del Dominio

**Decisión:** Plugins no solo validan, también registran métodos de negocio útiles.

**Métodos implementados:**
- **Pan**: `is_long()`, `is_small()`
- **Salchicha**: `is_long()`, `is_small()`, `matches_size(other)`
- **HotDog**: `has_toppings()`, `has_salsas()`, `is_combo()`

**Ventajas:**
- Métodos encapsulados en las entidades que los necesitan
- Reutilizables en toda la aplicación
- Facilitan lógica de negocio
- Autodocumentados en las clases

**Ejemplo de uso:**
```python
if salchicha.matches_size(pan):
    print("✅ Compatible")
else:
    print("⚠️ Advertencia: tamaños diferentes")
```

**Fecha:** NOV 13, 2025

---

#### 10. Testing Exhaustivo del Sistema Completo

**Decisión:** Crear test completo que verifica toda la cadena end-to-end.

**Test creado:** `test/test_entities.py` con 6 test cases:
1. Creación con fallback schemas
2. Instanciación y métodos inyectados
3. Validación jerárquica (base + específica)
4. Métodos con parámetros (matches_size)
5. Ingredientes simples (Topping, Salsa, Acompañante)
6. HotDog completo

**Cobertura:**
- ✅ Inferencia de schemas
- ✅ Creación de clases base e hijas
- ✅ Inyección de métodos
- ✅ Composición de validadores
- ✅ Herencia automática de validación
- ✅ Casos inválidos que deben fallar

**Ventajas:**
- Garantiza que toda la arquitectura funciona end-to-end
- Detecta problemas de integración temprano
- Documenta cómo usar el sistema
- Confidence para refactorings futuros

**Fecha:** NOV 13, 2025

---

### Estructura Final del Sistema

**Flujo completo de generación:**
1. `create_ingredient_entities()` recibe raw_data opcional
2. Importa plugins dentro de función (evita imports circulares)
3. Infiere schemas o usa fallback
4. Crea clase base Ingredient con propiedades comunes
5. Crea clases específicas (Pan, Salchicha, etc.) heredando de Ingredient
6. Factory automáticamente inyecta métodos y validadores desde registry
7. Factory automáticamente wrappea validadores para llamar base_class.validate()
8. Retorna clases listas para usar

**Estructura de archivos:**
```
models/
├── core/                          # Genérico, portable
│   ├── base_entity.py
│   ├── method_registry.py
│   └── entity_factory.py
├── schemas/                       # Específico del dominio
│   ├── ingredient_schemas.py
│   └── hotdog_schemas.py
├── plugins/                       # Específico del dominio
│   ├── ingredients/
│   │   ├── __init__.py
│   │   ├── ingredient_base_plugin.py
│   │   ├── pan_plugin.py
│   │   ├── salchicha_plugin.py
│   │   ├── topping_plugin.py
│   │   ├── salsa_plugin.py
│   │   └── acompañante_plugin.py
│   └── hotdogs/
│       ├── __init__.py
│       └── hotdog_plugin.py
├── entities/                      # Funciones de creación
│   ├── ingredients.py
│   └── hotdogs.py
└── __init__.py                    # Exporta funciones
```

---

### Conceptos de POO Avanzados Aplicados

1. **Registry Pattern** - MethodRegistry centraliza funcionalidad
2. **Plugin Architecture** - Extensibilidad mediante plugins desacoplados
3. **Factory Pattern** - EntityFactory genera clases dinámicamente
4. **Metaprogramming** - `make_dataclass()`, `setattr()` para crear/modificar clases en runtime
5. **Composition over Inheritance** - Validadores se componen funcionalmente
6. **Template Method Pattern** - Validación base + hooks específicos
7. **Inversion of Control** - Registry controla qué métodos tienen las clases
8. **Open/Closed Principle** - Abierto a extensión (nuevos plugins), cerrado a modificación
9. **Single Responsibility** - Cada componente una responsabilidad única
10. **Dependency Injection** - Factory recibe schemas y base_class como parámetros
11. **Strategy Pattern** - Diferentes schemas para diferentes estructuras de datos
12. **Lazy Initialization** - Clases se crean bajo demanda, no al importar

---

### Ventajas del Sistema

**Para el proyecto actual:**
- Reutilizamos la misma infraestructura para ingredientes, hot dogs, ventas
- Menos código total (~185 líneas vs ~215 con mixins tradicionales)
- Consistencia: todas las entidades funcionan igual
- Validación robusta y modular

**Para reutilización futura:**
- El core es 100% portable a otros proyectos
- Cambiar de dominio = cambiar solo schemas y plugins
- Ejemplos: Tienda de mascotas, biblioteca, CRM, inventario genérico

**Para evaluación académica:**
- Demuestra arquitectura de software avanzada
- Máxima separación de concerns
- Extensibilidad sin modificar código existente
- Aplicación práctica de principios SOLID
- Metaprogramming y técnicas avanzadas de Python

---

### Trade-offs y Limitaciones

**Desventajas:**
- Mayor complejidad inicial (~90 líneas de infraestructura)
- Métodos inyectados no aparecen en autocompletado del IDE
- Curva de aprendizaje más pronunciada
- Debugging requiere entender inyección dinámica
- Sin validación de tipos estáticos (todo es `Any`)

**Cuándo NO usar este sistema:**
- Proyectos pequeños con pocas entidades (< 5)
- Equipos sin experiencia en metaprogramming
- Cuando se requiere type safety estricto
- Prototipado rápido donde la arquitectura no importa

---

### Reutilización del Código

El módulo `models/core/` completo puede extraerse y usarse en:
- Sistema de biblioteca (Book, Author, Loan)
- Tienda de mascotas (Pet, Owner, Appointment)
- Sistema de inventario genérico
- CRM (Customer, Lead, Opportunity)
- Gestión de proyectos (Project, Task, User)
- Cualquier dominio que necesite entidades dinámicas

**Pasos para reutilizar:**
1. Copiar `models/core/` completo
2. Crear nuevos schemas para tu dominio
3. Crear nuevos plugins con validadores y métodos
4. Crear funciones de creación de entidades
5. ¡Listo!

---


---

## Sistema de IDs con Adapter Pattern

### Visión General

**Decisión:** Implementamos un sistema de IDs estables que garantiza que toda la data tenga identificadores únicos y consistentes, independientemente de la fuente externa (GitHub, MongoDB, etc.).

**Problema que resuelve:**
- Las fuentes externas (GitHub) no tienen IDs
- Necesitamos IDs únicos para referencias entre entidades
- Los IDs deben ser estables entre reloads (mismo item = mismo ID)
- Referencias no deben romperse al hacer reset desde GitHub

---

### Decisiones Arquitectónicas Detalladas

#### 1. IDs Determinísticos con Hash

**Decisión:** Usar hash MD5 de `category:nombre` para generar IDs estables en lugar de UUIDs aleatorios.

**Implementación:**
```python
def generate_stable_id(natural_key: str, category: str = "") -> str:
    seed = f"{category}:{natural_key}"
    hash_digest = hashlib.md5(seed.encode('utf-8')).hexdigest()
    return f"{hash_digest[:8]}-{hash_digest[8:12]}-..."  # Formato UUID
```

**Ventajas:**
- Mismo input → siempre mismo output (determinístico)
- Pan "simple" siempre tiene el mismo ID, incluso después de reset
- Referencias entre entidades nunca se rompen
- No necesitamos registry persistente

**Alternativas rechazadas:**
- UUID aleatorio: IDs cambiarían en cada reload → referencias rotas
- Registry persistente: Complejidad innecesaria para este caso
- IDs secuenciales: No funcionan con múltiples fuentes

**Fecha:** NOV 14, 2025

---

#### 2. Adapter Pattern para Agregar IDs

**Decisión:** Usar Adapter Pattern en lugar de que GitHubClient o DataSourceClient manejen IDs directamente.

**Arquitectura:**
```
GitHub (sin IDs)
  ↓
GitHubClient (transporte puro, sin lógica de dominio)
  ↓
IDAdapter (wrapper que agrega IDs)
  ↓
DataSourceClient (recibe data con IDs garantizados)
```

**Implementación:**
```python
# GitHubClient permanece simple
github = GitHubClient(owner, repo, branch)

# IDAdapter envuelve y agrega funcionalidad
ingredientes_source = IDAdapter(
    external_source=github,
    id_processor=process_grouped_structure_ids
)

# DataSource recibe source que SIEMPRE tiene IDs
data_source.initialize({'ingredientes': ingredientes_source})
```

**Por qué NO en GitHubClient:**
- GitHubClient quedaría acoplado a estructura de dominio
- Violaría Single Responsibility Principle
- No sería reutilizable para otros proyectos
- Tendría que conocer estructura GROUPED vs FLAT

**Por qué NO en DataSourceClient:**
- DataSource debe ser agnóstico del dominio
- Extensibilidad: cada nueva collection requeriría modificar DataSource
- Testing más difícil

**Ventajas del Adapter:**
- Composition over inheritance
- GitHubClient reutilizable y simple
- Mismo github client para diferentes estructuras
- Fácil agregar nuevas fuentes (MongoDB, APIs, etc.)
- Testeable con mocks simples

**Fecha:** NOV 14, 2025

---

#### 3. ID Processors por Estructura de Datos

**Decisión:** Crear processors específicos para cada tipo de estructura (GROUPED, FLAT) en lugar de un processor universal.

**Implementación:**
- `process_grouped_structure_ids()`: Para ingredientes con estructura `[{Categoria, Opciones: [...]}]`
- `process_flat_structure_ids()`: Para menu con estructura `[{item}, {item}, ...]`

**Por qué NO un processor universal:**
- Solo 2-3 estructuras diferentes en el proyecto
- Cada una tiene lógica única de traversal
- Over-engineering crear abstracción para pocos casos
- Simplicidad > generalización excesiva

**Signatura de processors:**
```python
def process_X_structure_ids(
    raw_data: Any,
    **config
) -> Tuple[Any, bool]:
    """
    Returns:
        (processed_data, modified): modified=True si se agregaron IDs
    """
```

**Fecha:** NOV 14, 2025

---

#### 4. Contrato de External Sources

**Decisión:** Documentar que External Sources DEBEN devolver data con IDs, pero no forzarlos a implementarlo ellos mismos.

**Contrato:**
> "Todo ExternalSourceClient que se pase a DataSourceClient DEBE devolver data con IDs"

**Implementación del contrato:**
- Sources crudos (GitHubClient): NO tienen IDs → se wrappean con IDAdapter
- Sources nativos con IDs: Pasan directo sin adapter
- DataSourceClient asume que SIEMPRE recibe data con IDs

**Ventajas:**
- Contrato claro y explícito
- Flexibilidad: sources con IDs nativos skip el adapter
- Separación de responsabilidades clara

**Fecha:** NOV 14, 2025

---

#### 5. Unicidad de Nombres por Categoría

**Decisión:** Prohibir nombres duplicados dentro de la misma categoría.

**Razón:**
- IDs estables se basan en `category:nombre`
- Dos items con mismo nombre en misma categoría → colisión de IDs
- No tiene sentido de negocio (¿para qué dos panes "simple"?)

**Validación:**
- Se implementará en Collection.add() (Fase 1 pendiente)
- Error: "Ya existe un Pan llamado 'simple'"

**Nombres duplicados entre categorías SÍ permitidos:**
- Pan "simple" → ID basado en "Pan:simple"
- Salsa "simple" → ID basado en "Salsa:simple"
- Diferentes IDs → sin colisión ✅

**Fecha:** NOV 14, 2025

---

#### 6. Persistencia de IDs en Archivos Locales

**Decisión:** Los IDs se persisten en los archivos JSON locales, no solo en memoria.

**Flujo:**
1. **Primera carga** (desde GitHub sin IDs):
   ```
   GitHub → GitHubClient → IDAdapter (agrega IDs) → DataSource
                                                    ↓
                                            data/ingredientes.json (CON IDs)
   ```

2. **Cargas posteriores** (desde local):
   ```
   data/ingredientes.json (CON IDs) → DataSource
   ```

3. **Reset/Reload** (force_external=True):
   ```
   GitHub → IDAdapter (regenera MISMOS IDs) → data/ingredientes.json
   ```

**Ventajas:**
- No hay que regenerar IDs en cada startup
- Archivos locales son source of truth con IDs
- IDs persisten entre sesiones
- Performance: solo se generan una vez

**Fecha:** NOV 14, 2025

---

### Estructura Final del Sistema

**Módulos creados:**
```
clients/
├── id_processors.py              # Funciones de generación de IDs
├── adapters/
│   ├── __init__.py
│   └── id_adapter.py            # IDAdapter class
└── external_sources/
    ├── external_source_client.py  # Contrato actualizado
    └── github_client.py          # Sin cambios (permanece simple)
```

**Flujo de datos completo:**
```
1. Configuración
   github_client = GitHubClient(...)
   adapted = IDAdapter(github_client, process_grouped_structure_ids)
   
2. Inicialización
   data_source.initialize({'ingredientes': adapted})
   
3. Interno del adapter
   raw_data = github_client.fetch_data('ingredientes.json')  # Sin IDs
   processed_data, modified = processor(raw_data)             # Con IDs
   return processed_data
   
4. DataSource persiste
   data_source._save_local('ingredientes', processed_data)   # Guarda con IDs
```

---

### Testing

**Tests implementados:**
1. `test_stable_id_generation()`: Verifica determinismo y formato UUID
2. `test_id_adapter()`: Prueba adapters con GROUPED y FLAT
3. `test_data_source_client_with_ids()`: Integración completa end-to-end

**Cobertura:**
- ✅ Generación determinística de IDs
- ✅ Formato UUID válido
- ✅ Adapter con múltiples estructuras
- ✅ Persistencia de IDs en archivos locales
- ✅ Estabilidad de IDs entre reloads
- ✅ Integración con DataSourceClient

---

### Ventajas del Sistema

**Para el proyecto:**
- IDs únicos y consistentes garantizados
- Referencias entre entidades estables
- No se rompen al hacer reset desde GitHub
- Sistema extensible a nuevas fuentes de datos

**Para arquitectura:**
- Separation of concerns clara
- GitHubClient reutilizable sin conocimiento del dominio
- DataSourceClient agnóstico de estructura
- Adapter Pattern bien aplicado
- Fácil agregar nuevas fuentes (MongoDB, APIs, etc.)

**Para testing:**
- Mocks simples sin preocuparse por IDs
- Tests unitarios de cada componente
- Tests de integración end-to-end

---

### Trade-offs

**Ventajas vs alternativas:**
- ✅ Más simple que registry persistente
- ✅ Más flexible que IDs en GitHubClient
- ✅ Más robusto que UUIDs aleatorios

**Limitaciones:**
- ⚠️ MD5 no es criptográficamente seguro (pero suficiente para IDs)
- ⚠️ Cambiar nombre de item cambia su ID (pero esto es esperado)
- ⚠️ Colisiones posibles en teoría (pero extremadamente improbables)

---

**Última actualización**: NOV 14, 2025 - Rafael Correa


