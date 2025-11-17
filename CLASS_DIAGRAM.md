# 📐 Diagramas de Clases - Hot Dog CCS

## 🎨 Cómo Visualizar los Diagramas

Los diagramas están escritos en **PlantUML**, un lenguaje que genera diagramas UML automáticamente desde código.

### Opción 1: Visualizador Online (Recomendado)

1. Ve a [PlantUML Online Editor](https://www.plantuml.com/plantuml/uml/)
2. Abre cualquier archivo `.puml` de la carpeta `classDiagrams/`
3. Copia todo el contenido
4. Pégalo en el editor
5. El diagrama se renderiza automáticamente

**Para exportar como imagen:**
- Click derecho en el diagrama → "Guardar imagen como..."
- Formatos disponibles: PNG, SVG

### Opción 2: VS Code (Local)

1. Instala la extensión "PlantUML" en VS Code
2. Abre cualquier archivo `.puml`
3. Presiona `Alt + D` para ver el preview en vivo

---

## 📚 Organización de los Diagramas

El sistema está dividido en **6 diagramas** que representan diferentes capas y aspectos de la arquitectura. Esta separación permite:

- ✅ **Legibilidad**: Cada diagrama es enfocado y comprensible
- ✅ **Mantenibilidad**: Fácil actualizar partes específicas
- ✅ **Documentación**: Sirve como referencia técnica por capa

---

## 1️⃣ Diagrama de Arquitectura General

**Vista de alto nivel del sistema completo.**

Este diagrama muestra la **arquitectura en capas** del sistema, ilustrando cómo fluyen las dependencias desde la capa de presentación (CLI) hasta la capa de acceso a datos (Clients). Cada capa tiene responsabilidades claras y se comunica únicamente con la capa inmediatamente inferior, siguiendo el principio de **Separation of Concerns**.

**Capas principales:**
- **CLI Layer**: Interfaz de usuario (Router Pattern)
- **Service Layer**: Lógica de negocio
- **Data Layer**: Gestión de datos (Repository + Unit of Work)
- **Model Layer**: Entidades dinámicas (Metaprogramming)
- **Clients Layer**: Adaptadores de fuentes externas (Adapter Pattern)

📄 **Archivo:** [`classDiagrams/01_architecture_overview.puml`](classDiagrams/01_architecture_overview.puml)

---

## 2️⃣ Capa de Datos (Data Layer)

**Gestión de fuentes de datos, adaptadores y persistencia.**

Este diagrama detalla cómo el sistema obtiene, procesa y almacena datos. Implementa el **Adapter Pattern** para transformar datos crudos de GitHub en estructuras procesadas con IDs determinísticos, claves normalizadas, stock inicializado y referencias estructuradas. También muestra el **Repository Pattern** a través de las Collections y el **Unit of Work Pattern** mediante el DataHandler.

**Componentes clave:**
- **Cadena de Adapters**: GitHub → IDs → KeyNormalization → Stock → IngredientReference
- **DataSourceClient**: Cache en memoria + persistencia local
- **DataHandler**: Orquestador de múltiples collections
- **Collections**: IngredientCollection, HotDogCollection, VentaCollection

📄 **Archivo:** [`classDiagrams/02_data_layer.puml`](classDiagrams/02_data_layer.puml)

---

## 3️⃣ Núcleo del Modelo (Model Core)

**Sistema de metaprogramming para generación dinámica de clases.**

Este diagrama expone la "magia" detrás de las entidades del sistema. Utiliza **metaprogramming** en Python para generar clases dinámicamente en runtime a partir de schemas inferidos desde datos reales. Los plugins registran validadores y métodos personalizados que se inyectan automáticamente en las clases generadas, sin necesidad de hardcodear lógica.

**Patrones aplicados:**
- **Factory Pattern**: EntityFactory genera clases con `make_dataclass()`
- **Registry Pattern**: MethodRegistry centraliza métodos y validadores
- **Plugin Architecture**: Extensibilidad mediante side-effects al importar

**Flujo:**
1. Schemas se infieren desde JSON (data-driven)
2. Plugins se registran en MethodRegistry
3. EntityFactory genera clases dinámicas
4. Métodos/validadores se inyectan automáticamente

📄 **Archivo:** [`classDiagrams/03_model_core.puml`](classDiagrams/03_model_core.puml)

---

## 4️⃣ Entidades del Dominio (Domain Entities)

**Clases concretas del negocio de hot dogs.**

Este diagrama muestra las **entidades específicas del dominio** generadas dinámicamente por el sistema de metaprogramming. Representa el modelo de negocio completo con relaciones de herencia (ingredientes especializados), composición (hot dogs contienen ingredientes) y agregación (ventas contienen items).

**Jerarquía de entidades:**
- **Ingredient** (base): Pan, Salchicha, Toppings, Salsa, Acompañante
- **HotDog**: Composición de ingredientes con referencias estructuradas
- **Venta**: Registro de venta con lista de items (hot dogs vendidos)

**Nota:** Estas clases NO están hardcodeadas en el código fuente. Se generan dinámicamente al iniciar la aplicación a partir de los datos de GitHub.

📄 **Archivo:** [`classDiagrams/04_domain_entities.puml`](classDiagrams/04_domain_entities.puml)

---

## 5️⃣ Capa de Servicios (Service Layer)

**Lógica de negocio aislada de persistencia y presentación.**

Este diagrama ilustra el **Service Layer Pattern**, donde toda la lógica de negocio reside en servicios sin estado (static methods). Los servicios orquestan operaciones entre el DataHandler y las entidades, validando reglas de negocio y coordinando transacciones complejas.

**Servicios implementados:**
- **IngredientService**: Gestión de catálogo e inventario
- **MenuService**: Operaciones CRUD sobre hot dogs
- **VentaService**: Registro de ventas con **Builder Pattern** (VentaBuilder)
- **ReportingService**: Análisis y agregación de datos
- **ChartGenerator**: Visualización con matplotlib

**Características:**
- Stateless (sin estado interno)
- Reciben DataHandler como parámetro
- Retornan estructuras de datos simples (Dict, List)
- Coordinan múltiples collections cuando es necesario

📄 **Archivo:** [`classDiagrams/05_service_layer.puml`](classDiagrams/05_service_layer.puml)

---

## 6️⃣ Capa de Presentación (CLI Layer)

**Interfaz de usuario con Router Pattern y UI declarativa.**

Este diagrama muestra la arquitectura del CLI, implementando el **Router Pattern** similar a frameworks web (Flask, Express) pero adaptado para aplicaciones de línea de comandos. La UI es completamente **declarativa**: los menús se definen como estructuras de datos, no código imperativo.

**Componentes principales:**
- **MenuRouter**: Orquestador central (navegación, ejecución de actions, stack)
- **MenuDefinition/MenuOption**: Definición declarativa de menús
- **ActionResult**: Comunicación entre actions y router
- **Views/Colors**: Utilidades de I/O con formato consistente
- **Actions**: Módulos que orquestan Services + Views

**Características del core CLI:**
- ✅ 100% genérico y reutilizable (portable a otros proyectos)
- ✅ Navegación con stack (back/forward)
- ✅ Context compartido entre actions
- ✅ Validación automática de input
- ✅ Confirmaciones y manejo de errores

📄 **Archivo:** [`classDiagrams/06_cli_layer.puml`](classDiagrams/06_cli_layer.puml)

---

## 🎓 Patrones de Diseño Aplicados

A lo largo de los 6 diagramas, se pueden identificar los siguientes patrones:

| Patrón | Ubicación | Propósito |
|--------|-----------|-----------|
| **Adapter** | Data Layer | Transformar datos de fuentes externas |
| **Repository** | Data Layer | Abstraer acceso a datos |
| **Unit of Work** | DataHandler | Coordinar transacciones |
| **Factory** | Model Core | Generar clases dinámicamente |
| **Registry** | Model Core | Centralizar plugins |
| **Plugin Architecture** | Model Core | Extensibilidad sin modificar código |
| **Builder** | Service Layer | Construcción diferida de ventas |
| **Service Layer** | Service Layer | Aislar lógica de negocio |
| **Router** | CLI Layer | Navegación declarativa |
| **Command** | CLI Layer | Actions como comandos ejecutables |

---

## 📖 Convenciones de los Diagramas

**Estereotipos utilizados:**
- `<<static>>`: Clase con solo métodos estáticos (sin instanciación)
- `<<utility>>`: Clase de utilidades (funciones helper)
- `<<abstract>>`: Clase abstracta (no se instancia directamente)
- `<<module>>`: Módulo Python con funciones
- `<<example>>`: Ejemplo de uso (no exhaustivo)

**Símbolos de relación:**
- `--|>`: Herencia (extends)
- `..|>`: Implementación (implements)
- `*--`: Composición (fuerte, ciclo de vida acoplado)
- `o--`: Agregación (débil, independiente)
- `-->`: Asociación dirigida
- `..>`: Dependencia (uso temporal)

**Colores:**
- 🟣 Púrpura: Core/Orchestrator
- 🔵 Azul: Estructuras de datos
- 🟢 Verde: Análisis/Reporting
- 🟠 Naranja: Lógica de negocio
- 🟡 Amarillo: Utilidades

---

## 🚀 Orden Recomendado de Lectura

Si es tu primera vez explorando el sistema, sigue este orden:

1. **01_architecture_overview** → Entender capas y flujo general
2. **04_domain_entities** → Conocer entidades del negocio
3. **05_service_layer** → Ver lógica de negocio
4. **02_data_layer** → Comprender persistencia
5. **03_model_core** → Explorar metaprogramming (avanzado)
6. **06_cli_layer** → Estudiar interfaz de usuario

---

**Autor:** Rafael Correa  
**Fecha:** Noviembre 2025  
**Proyecto:** Hot Dog CCS - Sistema de Gestión para Cadena de Hot Dogs
