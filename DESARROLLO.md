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
Construir la base del sistema de persistencia y acceso a datos, abstrayendo completamente la lógica de fetch desde GitHub y el manejo de archivos locales.

### Tareas
- [ ] Cliente para descargar datos desde GitHub
- [ ] Definir estructuras de datos principales (ingredientes, hot dogs, inventario, ventas)
- [ ] Sistema de colecciones genérico con operaciones CRUD
- [ ] Colecciones especializadas por tipo de dato
- [ ] Handler central que orqueste carga desde GitHub y archivos locales
- [ ] Archivo de configuración con constantes del proyecto
- [ ] Testing manual del flujo completo de datos

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

**Última actualización**: [NOV 12, 2025] - [Rafael Correa]
