### Fase 1.2: Sistema Genérico de Entidades con Plugin Architecture

#### 1. Preparación
- [ ] Crear estructura de directorios:
  - [ ] `models/`
  - [ ] `models/core/` (código genérico reutilizable)
  - [ ] `models/schemas/` (definiciones por dominio)
  - [ ] `models/plugins/` (funcionalidad específica)
  - [ ] `models/plugins/ingredients/`
  - [ ] `models/plugins/hotdogs/`
  - [ ] `models/plugins/sales/`
  - [ ] `models/entities/` (clases generadas exportables)

#### 2. Core - Base Entity (core/base_entity.py)
- [x] Definir clase `Entity` completamente genérica con:
  - [x] Atributos core: id, entity_type
  - [x] `__init__` que acepta **kwargs para propiedades dinámicas
  - [x] Método `to_dict()` para serialización
  - [x] Método `from_dict()` para deserialización
  - [x] Hook `validate()` (será inyectado por plugins)
  - [x] `__repr__()` para debugging

#### 3. Core - Method Registry (core/method_registry.py)
- [x] Crear clase `MethodRegistry` con:
  - [x] `_methods` dict anidado: {entity_type: {method_name: func}}
  - [x] `_validators` dict: {entity_type: validator_func}
  - [x] `register_method(entity_type, method_name, func)`
  - [x] `register_validator(entity_type, func)`
  - [x] `get_methods(entity_type)` → Dict[str, Callable]
  - [x] `get_validator(entity_type)` → Callable
  - [x] `clear()` para testing

#### 4. Core - Entity Factory (core/entity_factory.py)
- [x] Función `create_entity_class()` con parámetros:
  - [x] class_name: nombre de la clase a generar
  - [x] entity_type: tipo para lookup en registry
  - [x] properties: lista de propiedades
  - [x] base_class: clase base (default: Entity)
- [x] Lógica de generación:
  - [x] Crear clase con `make_dataclass()`
  - [x] Inyectar métodos desde `MethodRegistry`
  - [x] Inyectar validador desde `MethodRegistry`
  - [x] Retornar clase generada
- [x] Función `create_entities_from_schemas()`:
  - [x] Recibe dict de schemas
  - [x] Itera y genera múltiples clases
  - [x] Retorna dict de clases generadas

#### 5. Schemas - Ingredientes (schemas/ingredient_schemas.py)
- [ ] Definir `INGREDIENT_SCHEMAS` dict:
  - [ ] Pan: ['nombre', 'tipo', 'tamaño', 'unidad']
  - [ ] Salchicha: ['nombre', 'tipo', 'tamaño', 'unidad']
  - [ ] Topping: ['nombre', 'tipo']
  - [ ] Salsa: ['nombre', 'tipo']
  - [ ] Acompañante: ['nombre', 'tipo']

#### 6. Schemas - HotDogs (schemas/hotdog_schemas.py)
- [ ] Definir `HOTDOG_SCHEMAS` dict:
  - [ ] HotDog: ['nombre', 'pan_id', 'salchicha_id', 'topping_ids', 'salsa_ids', 'acompañante_id']

#### 7. Schemas - Ventas (schemas/sale_schemas.py)
- [ ] Definir `SALE_SCHEMAS` dict:
  - [ ] VentaRegistro: ['cliente_id', 'hotdog_ids', 'acompañantes_extra', 'exito', 'motivo_fallo', 'fecha']
  - [ ] ResultadoDia: [todas las métricas del día]

#### 8. Plugins - Ingredientes
- [ ] `plugins/ingredients/pan_plugin.py`:
  - [ ] Registrar método `es_largo()` con MethodRegistry
  - [ ] Registrar método `es_pequeño()`
  - [ ] Registrar validador `validate()`
- [ ] `plugins/ingredients/salchicha_plugin.py`:
  - [ ] Registrar método `es_larga()`
  - [ ] Registrar validador `validate()`
- [ ] `plugins/ingredients/topping_plugin.py`:
  - [ ] Registrar validador `validate()`
- [ ] `plugins/ingredients/salsa_plugin.py`:
  - [ ] Registrar validador `validate()`
- [ ] `plugins/ingredients/acompañante_plugin.py`:
  - [ ] Registrar validador `validate()`
- [ ] `plugins/ingredients/__init__.py`:
  - [ ] Importar todos los plugins (auto-registro)

#### 9. Plugins - HotDogs
- [ ] `plugins/hotdogs/hotdog_plugin.py`:
  - [ ] Registrar método `tiene_toppings()`
  - [ ] Registrar método `tiene_salsas()`
  - [ ] Registrar método `es_combo()` (tiene acompañante)
  - [ ] Registrar validador `validate()`
- [ ] `plugins/hotdogs/__init__.py`:
  - [ ] Importar plugin

#### 10. Plugins - Ventas
- [ ] `plugins/sales/venta_plugin.py`:
  - [ ] Registrar método `fue_exitosa()`
  - [ ] Registrar método `total_items()`
  - [ ] Registrar validador `validate()`
- [ ] `plugins/sales/resultado_dia_plugin.py`:
  - [ ] Registrar métodos de cálculo si necesarios
  - [ ] Registrar validador `validate()`
- [ ] `plugins/sales/__init__.py`:
  - [ ] Importar plugins

#### 11. Entidades - Ingredientes (entities/ingredients.py)
- [ ] Importar core: `create_entities_from_schemas`
- [ ] Importar schema: `INGREDIENT_SCHEMAS`
- [ ] Importar plugins para auto-registro: `import models.plugins.ingredients`
- [ ] Generar clases: `_classes = create_entities_from_schemas(INGREDIENT_SCHEMAS)`
- [ ] Exportar individualmente: `Pan = _classes['Pan']`, etc.

#### 12. Entidades - HotDogs (entities/hotdogs.py)
- [ ] Importar y generar igual que ingredientes
- [ ] Exportar: `HotDog`

#### 13. Entidades - Ventas (entities/sales.py)
- [ ] Importar y generar igual que ingredientes
- [ ] Exportar: `VentaRegistro`, `ResultadoDia`

#### 14. Exportación Principal (models/__init__.py)
- [ ] Importar desde entities:
  - [ ] `from models.entities.ingredients import Pan, Salchicha, Topping, Salsa, Acompañante`
  - [ ] `from models.entities.hotdogs import HotDog`
  - [ ] `from models.entities.sales import VentaRegistro, ResultadoDia`
- [ ] Exportar todo en `__all__`

#### 15. Testing
- [ ] Test de core genérico (independiente del dominio)
- [ ] Test de cada tipo de entidad:
  - [ ] Crear instancias
  - [ ] Verificar métodos inyectados
  - [ ] Verificar validadores
  - [ ] Verificar `to_dict()` y `from_dict()`
  - [ ] Verificar que son instancias de `Entity`
- [ ] Test de integración entre entidades