# 📖 Manual de Usuario - Hot Dog CCS

Guía completa de uso del sistema de gestión Hot Dog CCS.

---

## 📑 Tabla de Contenidos

1. [Inicio del Sistema](#inicio-del-sistema)
2. [Navegación General](#navegación-general)
3. [Módulo 1: Gestión de Ingredientes](#módulo-1-gestión-de-ingredientes)
4. [Módulo 2: Gestión de Inventario](#módulo-2-gestión-de-inventario)
5. [Módulo 3: Gestión del Menú](#módulo-3-gestión-del-menú)
6. [Módulo 4: Gestión de Ventas](#módulo-4-gestión-de-ventas)
7. [Módulo 5: Reportes y Estadísticas](#módulo-5-reportes-y-estadísticas)
8. [Menú Debug](#menú-debug)
9. [Preguntas Frecuentes](#preguntas-frecuentes)

---

## Inicio del Sistema

### Primera Ejecución

1. Asegúrate de haber configurado el archivo `.env` con los datos de GitHub:
   ```env
   GITHUB_OWNER=FernandoSapient
   GITHUB_REPO=BPTSP05_2526-1
   GITHUB_BRANCH=main
   ```

2. Ejecuta el programa:
   ```bash
   python main.py
   ```

3. El sistema descargará automáticamente los datos desde GitHub y mostrará:
   ```
   🔧 Setting up data sources...
   📦 Configuring ingredients source...
   🌭 Configuring menu source...
   ✅ Data sources ready!
   
   🏗️  Setting up entity classes...
   ✅ Entity classes ready!
   
   📊 Setting up data handler...
   ✅ Data handler ready!
   ```

4. Aparecerá el menú principal.

### Menú Principal

```
🌭 HOT DOG CCS - SISTEMA DE GESTIÓN

1. 📦 Gestión de Ingredientes
2. 🌭 Gestión del Menú
3. 💰 Gestión de Ventas
4. 📊 Reportes y Estadísticas
9. 🔧 Debug / Diagnostics

0. Volver
x. Salir
```

---

## Navegación General

### Controles Básicos

- **Números (1-9)**: Seleccionar opciones del menú
- **0**: Volver al menú anterior
- **x**: Salir de la aplicación
- **Enter**: Continuar / Aceptar valor por defecto

### Confirmaciones

Cuando el sistema pide confirmación:
- **y / yes / s / sí**: Confirmar acción
- **n / no**: Cancelar acción
- **Enter sin texto**: Usar valor por defecto (indicado entre paréntesis)

### Códigos de Color

El sistema usa colores para facilitar la lectura:

- 🟢 **Verde**: Operaciones exitosas, stock suficiente
- 🔴 **Rojo**: Errores, stock agotado (0)
- 🟡 **Amarillo**: Advertencias, stock bajo (< 10)
- 🔵 **Azul**: Información, títulos
- ⚪ **Gris**: Texto informativo

---

## Módulo 1: Gestión de Ingredientes

**Acceso:** Menú Principal → Opción 1

### Opciones Disponibles

```
📦 INGREDIENT MANAGEMENT

1. Listar por categoría
2. Listar por tipo
3. Ver inventario
4. Actualizar stock
5. Agregar ingrediente
6. Eliminar ingrediente
```

---

### 1.1 Listar por Categoría

**Ruta:** Ingredientes → Opción 1

**Función:** Muestra todos los ingredientes de una categoría específica.

**Pasos:**
1. Selecciona la categoría:
   - 1: Pan
   - 2: Salchicha
   - 3: Toppings
   - 4: Salsa
   - 5: Acompañante

2. El sistema muestra una tabla con:
   - ID del ingrediente
   - Nombre
   - Tipo
   - Tamaño (si aplica)
   - Unidad (si aplica)

**Ejemplo de salida:**
```
Categoría: Pan

ID                                      Nombre      Tipo           Tamaño  Unidad
────────────────────────────────────────────────────────────────────────────────
cdd0f64a-b192-29e3-ef8f-df41e2da3287   simple      blanco         6       pulgadas
e5f6a8b9-c3d4-e5f6-a7b8-c9d0e1f2a3b4   integral    trigo entero   6       pulgadas
```

---

### 1.2 Listar por Tipo

**Ruta:** Ingredientes → Opción 2

**Función:** Filtra ingredientes por categoría y tipo específico.

**Pasos:**
1. Selecciona la categoría
2. Ingresa el tipo a buscar (ejemplo: "blanco", "weiner", "cebolla")

**Ejemplo:**
```
Categoría seleccionada: Pan
Tipo a buscar: blanco

Ingredientes encontrados: 1

ID                                      Nombre      Tipo     Tamaño  Unidad
─────────────────────────────────────────────────────────────────────────────
cdd0f64a-b192-29e3-ef8f-df41e2da3287   simple      blanco   6       pulgadas
```

---

### 1.3 Ver Inventario

**Ruta:** Ingredientes → Opción 3

**Función:** Muestra el inventario completo con código de colores según stock.

**Interpretación de colores:**
- 🟢 **Verde (✓)**: Stock > 10 unidades
- 🟡 **Amarillo (⚠️)**: Stock < 10 unidades
- 🔴 **Rojo (❌)**: Stock = 0 (agotado)

**Ejemplo:**
```
INVENTARIO COMPLETO

Pan:
  ✓ simple: 100
  ⚠️ integral: 8
  ❌ francés: 0

Salchicha:
  ✓ weiner: 75
  ✓ breakfast: 60
```

---

### 1.4 Actualizar Stock

**Ruta:** Ingredientes → Opción 4

**Función:** Modifica la cantidad de stock de un ingrediente.

**Pasos:**
1. Selecciona la categoría
2. Se muestra lista de ingredientes con stock actual
3. Ingresa el nombre del ingrediente
4. Ingresa la cantidad a agregar o restar:
   - **Número positivo**: Suma al stock (compra)
   - **Número negativo**: Resta del stock (uso/venta manual)

**Validaciones:**
- ✅ El stock nunca puede ser negativo
- ✅ Si intentas restar más de lo disponible, se muestra error

**Ejemplo:**
```
Categoría: Pan
Ingredientes disponibles:
  • simple (stock actual: 100)
  • integral (stock actual: 8)

Nombre del ingrediente: simple
Cantidad a modificar (+/-): -10

✅ Stock actualizado
Stock anterior: 100
Stock nuevo: 90
```

---

### 1.5 Agregar Ingrediente

**Ruta:** Ingredientes → Opción 5

**Función:** Registra un nuevo ingrediente en el sistema.

**Pasos:**
1. Selecciona la categoría
2. Ingresa el nombre del ingrediente
3. Ingresa las propiedades según la categoría:

**Pan / Salchicha:**
- Tipo (ej: "blanco", "integral", "weiner")
- Tamaño (número, ej: 6)
- Unidad (ej: "pulgadas", "cm")
- Stock inicial (número, default: 0)

**Toppings / Salsas / Acompañantes:**
- Tipo (ej: "vegetal", "picante", "frito")
- Stock inicial (número, default: 0)

**Validaciones:**
- ✅ El nombre debe ser único dentro de la categoría
- ✅ Todos los campos requeridos deben estar completos
- ✅ Stock debe ser un número no negativo

**Ejemplo:**
```
Categoría: Pan

Nombre: artesanal
Tipo: masa madre
Tamaño: 8
Unidad: pulgadas
Stock inicial (default: 0): 50

✅ Ingrediente 'artesanal' agregado exitosamente!
```

---

### 1.6 Eliminar Ingrediente

**Ruta:** Ingredientes → Opción 6

**Función:** Elimina un ingrediente del sistema.

**⚠️ Patrón de Confirmación de Dos Pasos:**

Si el ingrediente está siendo usado por hot dogs del menú:
1. **Primera llamada:** El sistema muestra hot dogs afectados
2. **Pregunta confirmación:** ¿Eliminar ingrediente Y hot dogs?
3. **Segunda llamada:** Ejecuta eliminación

Si el ingrediente NO está en el menú:
- Eliminación directa con una sola confirmación

**Pasos:**
1. Selecciona la categoría
2. Ingresa el nombre del ingrediente
3. Si hay hot dogs afectados:
   - Sistema muestra lista de hot dogs que se eliminarán
   - Pregunta confirmación
   - Elimina ingrediente + hot dogs O cancela

**Ejemplo con dependencias:**
```
Categoría: Pan
Nombre: simple

⚠️  ADVERTENCIA
El ingrediente 'simple' está siendo usado en los siguientes hot dogs:
  • simple
  • básico
  • económico

Si eliminas el ingrediente, estos 3 hot dogs también se eliminarán del menú.

¿Confirmar eliminación? (y/n): y

✅ Ingrediente 'simple' eliminado
Hot dogs eliminados: 3
  • simple
  • básico
  • económico
```

**Ejemplo sin dependencias:**
```
Categoría: Topping
Nombre: aceitunas

¿Confirmar eliminación de 'aceitunas'? (y/n): y

✅ Ingrediente 'aceitunas' eliminado exitosamente
```

---

## Módulo 2: Gestión de Inventario

**Nota:** Las funciones de inventario están integradas en el módulo de Ingredientes.

**Ver:**
- [1.3 Ver Inventario](#13-ver-inventario) - Visualizar todo el inventario
- [1.4 Actualizar Stock](#14-actualizar-stock) - Modificar cantidades

---

## Módulo 3: Gestión del Menú

**Acceso:** Menú Principal → Opción 2

### Opciones Disponibles

```
🌭 GESTIÓN DEL MENÚ

1. Ver lista de hot dogs
2. Verificar disponibilidad
3. Agregar hot dog
4. Eliminar hot dog
```

---

### 3.1 Ver Lista de Hot Dogs

**Ruta:** Menú → Opción 1

**Función:** Muestra todos los hot dogs registrados con sus ingredientes.

**Ejemplo de salida:**
```
HOT DOGS EN EL MENÚ

1. simple
   Pan: simple
   Salchicha: weiner
   Toppings: (ninguno)
   Salsas: (ninguno)
   Acompañante: (ninguno)

2. combo especial
   Pan: integral
   Salchicha: breakfast
   Toppings: cebolla, tomate
   Salsas: mostaza, ketchup
   Acompañante: Papas

Total: 10 hot dogs
```

---

### 3.2 Verificar Disponibilidad

**Ruta:** Menú → Opción 2

**Función:** Verifica si hay inventario suficiente para preparar un hot dog.

**Pasos:**
1. Se muestra lista de hot dogs
2. Ingresa el nombre del hot dog a verificar
3. Sistema muestra:
   - ✅ Disponible: Todos los ingredientes tienen stock
   - ❌ No disponible: Lista de ingredientes faltantes

**Ejemplo disponible:**
```
Hot dog seleccionado: simple

✅ HAY INVENTARIO DISPONIBLE

Ingredientes necesarios:
  ✓ Pan simple: disponible (stock: 100)
  ✓ Salchicha weiner: disponible (stock: 75)
```

**Ejemplo no disponible:**
```
Hot dog seleccionado: combo especial

❌ NO HAY INVENTARIO SUFICIENTE

Ingredientes faltantes:
  • cebolla (Toppings) - Necesita: 1, Disponible: 0
  • Papas (Acompañante) - Necesita: 1, Disponible: 0
```

---

### 3.3 Agregar Hot Dog

**Ruta:** Menú → Opción 3

**Función:** Crea un nuevo hot dog en el menú.

**Proceso Interactivo:**

**Paso 1: Nombre**
```
Nombre del hot dog: fitness
```

**Paso 2: Seleccionar Pan**
```
Selecciona el pan:

1. simple (stock: 100) ✓
2. integral (stock: 8) ⚠️
3. francés (stock: 0) ❌

Opción: 2
```

**Paso 3: Seleccionar Salchicha**
```
Selecciona la salchicha:

1. weiner (stock: 75) ✓
2. breakfast (stock: 60) ✓

Opción: 2
```

**Paso 4: Seleccionar Toppings** (múltiple)
```
Selecciona toppings (números separados por comas, Enter para ninguno):

1. cebolla (stock: 50) ✓
2. tomate (stock: 30) ✓
3. lechuga (stock: 0) ❌

Toppings (ej: 1,2): 2

Toppings seleccionados: tomate
```

**Paso 5: Seleccionar Salsas** (múltiple)
```
Selecciona salsas (números separados por comas, Enter para ninguno):

1. mostaza (stock: 100) ✓
2. ketchup (stock: 80) ✓
3. mayonesa (stock: 5) ⚠️

Salsas (ej: 1,3): 1

Salsas seleccionadas: mostaza
```

**Paso 6: Seleccionar Acompañante** (opcional)
```
¿Incluir acompañante? (y/n): n

Acompañante: ninguno
```

**Paso 7: Resumen y Confirmación**
```
RESUMEN DEL HOT DOG

Nombre: fitness
Pan: integral
Salchicha: breakfast
Toppings: tomate
Salsas: mostaza
Acompañante: ninguno

¿Guardar este hot dog? (y/n): y

✅ Hot dog 'fitness' agregado exitosamente!
```

**Validaciones Automáticas:**

**⚠️ Advertencia de Tamaños Diferentes:**
```
⚠️  ADVERTENCIA
El tamaño del pan (8 pulgadas) y la salchicha (6 pulgadas) no coinciden.
¿Continuar de todas formas? (y/n):
```

**⚠️ Advertencia de Stock:**
```
⚠️  ADVERTENCIA
No hay inventario del ingrediente 'lechuga' (stock: 0)
El hot dog se guardará pero no podrá venderse hasta reponer stock.
```

**❌ Error de Nombre Duplicado:**
```
❌ Error: Ya existe un hot dog con el nombre 'fitness'
Ingresa un nombre diferente.
```

---

### 3.4 Eliminar Hot Dog

**Ruta:** Menú → Opción 4

**Función:** Elimina un hot dog del menú.

**⚠️ Patrón de Confirmación Condicional:**

**Con inventario disponible:**
```
Hot dog seleccionado: fitness

⚠️  ADVERTENCIA
Hay inventario suficiente para vender 'fitness'.
¿Estás seguro de eliminarlo del menú? (y/n): y

✅ Hot dog 'fitness' eliminado del menú
```

**Sin inventario disponible:**
```
Hot dog seleccionado: combo especial

✅ Hot dog 'combo especial' eliminado del menú
(No había inventario disponible)
```

---

## Módulo 4: Gestión de Ventas

**Acceso:** Menú Principal → Opción 3

### Opciones Disponibles

```
💰 GESTIÓN DE VENTAS

1. Registrar venta
2. Ver todas las ventas
3. Ver ventas por fecha/rango
4. Estadísticas de ventas
5. 🎲 Simular día de ventas
```

---

### 4.1 Registrar Venta

**Ruta:** Ventas → Opción 1

**Función:** Registra una venta usando el patrón Builder (construcción paso a paso).

**Flujo Completo:**

**Paso 1: Crear Draft**
```
REGISTRAR VENTA

Construye la venta agregando hot dogs uno por uno.
Comandos disponibles:
  add    - Agregar hot dog
  remove - Quitar hot dog
  list   - Ver draft actual
  clear  - Limpiar todo
  done   - Finalizar y confirmar venta
  cancel - Cancelar
```

**Paso 2: Agregar Items**
```
Comando: add

Hot dogs disponibles:
1. simple
2. combo especial
3. fitness

Selecciona hot dog (nombre): simple
Cantidad (default: 1): 2

✅ Agregado: simple x2
```

**Agregar más items:**
```
Comando: add

Hot dog: combo especial
Cantidad: 1

✅ Agregado: combo especial x1
```

**Si agregas el mismo hot dog, se hace merge automático:**
```
Comando: add

Hot dog: simple
Cantidad: 1

ℹ️  Merged: simple ahora tiene cantidad 3 (era 2, +1)
```

**Paso 3: Ver Draft**
```
Comando: list

DRAFT ACTUAL:
  • simple x3
  • combo especial x1

Total items: 4 hot dogs
```

**Paso 4: Preview (Verificar Inventario)**
```
Comando: done

PREVIEW DE LA VENTA:
  • simple x3
  • combo especial x1

Total: 4 hot dogs

Verificando inventario...
✅ HAY INVENTARIO DISPONIBLE para todos los items

¿Confirmar venta? (y/n): y
```

**Paso 5: Confirmación**
```
✅ Venta registrada exitosamente!
ID: venta-2024-11-16-001
Inventario descontado:
  - Pan simple: 3 unidades
  - Salchicha weiner: 3 unidades
  - Pan integral: 1 unidad
  - Salchicha breakfast: 1 unidad
  - Toppings (cebolla): 1 unidad
  - Papas: 1 unidad
```

**Comandos Adicionales:**

**Quitar item:**
```
Comando: remove

Hot dog a quitar: simple

✅ Removido: simple
```

**Limpiar draft:**
```
Comando: clear

¿Limpiar todos los items? (y/n): y

ℹ️  Draft limpiado
```

**Cancelar:**
```
Comando: cancel

ℹ️  Venta cancelada (draft descartado)
```

**Si no hay inventario:**
```
Comando: done

PREVIEW:
  • fitness x1

❌ NO HAY INVENTARIO SUFICIENTE

Ingredientes faltantes:
  • lechuga (Toppings) - Necesita: 1, Disponible: 0

Hot dogs que no se pueden hacer:
  • fitness

No se puede completar la venta.
Opciones:
  - Quitar items sin inventario (comando: remove)
  - Cancelar venta (comando: cancel)
```

---

### 4.2 Ver Todas las Ventas

**Ruta:** Ventas → Opción 2

**Función:** Muestra historial completo de ventas ordenado por fecha (más reciente primero).

**Ejemplo:**
```
HISTORIAL DE VENTAS

════════════════════════════════════════════════════════════

Venta: venta-2024-11-16-002
Fecha: 2024-11-16 15:30:00
Items:
  • simple x2
  • combo especial x1
Total: 3 hot dogs

────────────────────────────────────────────────────────────

Venta: venta-2024-11-16-001
Fecha: 2024-11-16 10:00:00
Items:
  • simple x1
Total: 1 hot dog

════════════════════════════════════════════════════════════

Total de ventas: 2
```

---

### 4.3 Ver Ventas por Fecha/Rango

**Ruta:** Ventas → Opción 3

**Función:** Filtra ventas por fecha específica o rango de fechas.

**Opciones de Filtrado:**

**Opción 1: Fecha Única**
```
Ingresa fecha (YYYY-MM-DD): 2024-11-16

Ventas encontradas: 5

[... lista de ventas del 16 de noviembre ...]

RESUMEN:
  Total de ventas: 5
  Total de hot dogs vendidos: 12
  Promedio por venta: 2.4
```

**Opción 2: Fecha Parcial** (mes completo)
```
Ingresa fecha (YYYY-MM): 2024-11

Ventas encontradas: 45

[... lista de ventas de todo noviembre ...]

RESUMEN:
  Total de ventas: 45
  Total de hot dogs vendidos: 123
  Promedio por venta: 2.73
```

**Opción 3: Rango de Fechas**
```
Fecha inicio (YYYY-MM-DD): 2024-11-01
Fecha fin (Enter para solo fecha inicio): 2024-11-07

Ventas desde 2024-11-01 hasta 2024-11-07
Ventas encontradas: 28

[... lista de ventas de la semana ...]

RESUMEN:
  Total de ventas: 28
  Total de hot dogs vendidos: 75
  Promedio por venta: 2.68
```

---

### 4.4 Estadísticas de Ventas

**Ruta:** Ventas → Opción 4

**Función:** Muestra estadísticas generales de todas las ventas.

**Ejemplo:**
```
ESTADÍSTICAS DE VENTAS

Resumen General:
  Total de ventas: 109
  Total de hot dogs vendidos: 287
  Promedio de items por venta: 2.63

Top 5 Hot Dogs Más Vendidos:
  1. simple: 45 unidades
  2. combo especial: 38 unidades
  3. fitness: 32 unidades
  4. económico: 28 unidades
  5. premium: 25 unidades

Distribución:
  Ventas con 1 item: 23
  Ventas con 2 items: 35
  Ventas con 3 items: 28
  Ventas con 4 items: 15
  Ventas con 5 items: 8
```

---

### 4.5 Simular Día de Ventas

**Ruta:** Ventas → Opción 5

**Función:** Simula un día completo de ventas con clientes y órdenes aleatorias.

**Pasos:**

**1. Configuración:**
```
SIMULAR DÍA DE VENTAS

Fecha a simular (YYYY-MM-DD, Enter para hoy): 2024-11-17

Simulando día: 2024-11-17
```

**2. Simulación en Progreso:**
```
Generando clientes aleatorios...
Total de clientes: 150

Procesando ventas...
Progreso: [████████████░░░░] 150/150 (100.0%)
```

**3. Reporte Final:**
```
════════════════════════════════════════════════════════════
REPORTE DEL DÍA: 2024-11-17
════════════════════════════════════════════════════════════

Clientes:
  Total de clientes: 150
  Cambiaron de opinión: 23 (15.3%)
  No pudieron comprar: 18 (12.0%)
  Compraron exitosamente: 109 (72.7%)

Hot Dogs:
  Total vendidos: 287
  Promedio por cliente: 2.63
  Más vendido: simple (45 unidades)

Hot Dogs que causaron que clientes se marcharan:
  • fitness
  • premium

Ingredientes faltantes que causaron pérdidas:
  • lechuga (Toppings)
  • queso (Toppings)
  • Papas (Acompañante)

Acompañantes:
  Total vendidos (incluyendo combos): 52

════════════════════════════════════════════════════════════
✅ Simulación completada: 109 ventas registradas
════════════════════════════════════════════════════════════
```

**Explicación del Reporte:**

- **Cambiaron de opinión**: Clientes que fueron generados pero no ordenaron nada (0 hot dogs)
- **No pudieron comprar**: Clientes cuya orden no pudo completarse por falta de inventario
- **Compraron exitosamente**: Clientes cuya orden se registró y descontó inventario
- **Hot dogs que causaron pérdidas**: Hot dogs que no pudieron venderse por falta de ingredientes
- **Ingredientes faltantes**: Ingredientes específicos que se agotaron y causaron pérdidas de venta

---

## Módulo 5: Reportes y Estadísticas

**Acceso:** Menú Principal → Opción 4

### Opciones Disponibles

```
📊 REPORTES Y GRÁFICOS

1. 📈 Generar todos los gráficos
2. 📉 Gráfico: Ventas por día
3. 🏆 Gráfico: Hot dogs más vendidos
4. 🕐 Gráfico: Distribución por hora
5. 📊 Gráfico: Comparar fechas
6. 📄 Reporte general (texto)
```

---

### 5.1 Generar Todos los Gráficos

**Ruta:** Reportes → Opción 1

**Función:** Genera los 5 gráficos principales de una sola vez.

**Proceso:**
```
GENERAR TODOS LOS GRÁFICOS

Generando gráficos...

  📈 Ventas por día...
  📈 Hot dogs vendidos por día...
  🏆 Hot dogs más vendidos...
  🥫 Ingredientes consumidos...
  🕐 Distribución por hora...

✅ 5 gráficos generados exitosamente!

Archivos guardados:
  📊 charts/ventas_por_dia.png
  📊 charts/hotdogs_por_dia.png
  📊 charts/top_hotdogs.png
  📊 charts/ingredientes_consumidos.png
  📊 charts/ventas_por_hora.png

💡 Abre los archivos con tu visor de imágenes preferido.
```

**Gráficos generados:**
1. **ventas_por_dia.png** - Evolución temporal de número de ventas
2. **hotdogs_por_dia.png** - Total de hot dogs vendidos por día
3. **top_hotdogs.png** - Ranking de hot dogs más vendidos
4. **ingredientes_consumidos.png** - Top 15 ingredientes más utilizados
5. **ventas_por_hora.png** - Distribución de ventas por hora del día

---

### 5.2 Gráfico: Ventas por Día

**Ruta:** Reportes → Opción 2

**Función:** Gráfico de línea mostrando evolución de ventas por día.

**Generación:**
```
GRÁFICO: VENTAS POR DÍA

Generando gráfico...

✅ Gráfico generado: charts/ventas_por_dia.png
```

**Descripción del gráfico:**
- **Tipo**: Línea con marcadores circulares
- **Eje X**: Fechas (YYYY-MM-DD)
- **Eje Y**: Número de ventas
- **Color**: Azul (#2E86AB)
- **Características**: 
  - Valores etiquetados en cada punto
  - Grid para facilitar lectura
  - Rotación de fechas para mejor visualización

---

### 5.3 Gráfico: Hot Dogs Más Vendidos

**Ruta:** Reportes → Opción 3

**Función:** Ranking de hot dogs más populares.

**Configuración:**
```
GRÁFICO: HOT DOGS MÁS VENDIDOS

Cantidad de hot dogs a mostrar (default: 10): 15

Generando gráfico...

✅ Gráfico generado: charts/top_hotdogs.png
```

**Descripción del gráfico:**
- **Tipo**: Barras horizontales
- **Orden**: Mayor cantidad arriba
- **Colores**: Gradiente viridis (más vendido = más brillante)
- **Características**:
  - Valores en las barras
  - Altura dinámica según cantidad de items
  - Etiquetas de ejes en negrita

---

### 5.4 Gráfico: Distribución por Hora

**Ruta:** Reportes → Opción 4

**Función:** Muestra en qué horas del día hay más ventas.

**Generación:**
```
GRÁFICO: DISTRIBUCIÓN POR HORA

Generando gráfico...

✅ Gráfico generado: charts/ventas_por_hora.png
```

**Descripción del gráfico:**
- **Tipo**: Barras verticales
- **Eje X**: Horas del día (00:00 a 23:00)
- **Eje Y**: Número de ventas
- **Colores**: Gradiente coolwarm (azul = pocas ventas, rojo = muchas ventas)
- **Utilidad**: Identificar franjas horarias pico

---

### 5.5 Gráfico: Comparar Fechas

**Ruta:** Reportes → Opción 5

**Función:** Compara métricas de ventas entre múltiples fechas.

**Modo 1: Fechas Específicas**
```
GRÁFICO: COMPARAR FECHAS

Fechas disponibles: 2024-11-01 a 2024-11-30

Días con ventas:
  • 2024-11-16: 15 ventas
  • 2024-11-17: 20 ventas
  • 2024-11-18: 18 ventas
  ... y 27 días más

Opciones:
  1. Comparar fechas específicas
  2. Comparar rango de fechas

Selecciona opción (1 o 2): 1

Ingresa las fechas a comparar, separados por comas (YYYY-MM-DD):
Ejemplo: 2024-11-16, 2024-11-17, 2024-11-18

Fechas: 2024-11-16, 2024-11-17, 2024-11-20

Generando gráfico...

✅ Gráfico generado: charts/comparacion_fechas.png

Resumen:
  2024-11-16: 15 ventas, 45 hot dogs
  2024-11-17: 20 ventas, 67 hot dogs
  2024-11-20: 12 ventas, 32 hot dogs
```

**Modo 2: Rango de Fechas**
```
Selecciona opción (1 o 2): 2

Fecha inicio (YYYY-MM-DD): 2024-11-01
Fecha fin (YYYY-MM-DD): 2024-11-07

ℹ️  Se compararán 7 días

Generando gráfico...

✅ Gráfico generado: charts/comparacion_fechas.png

Resumen:
  2024-11-01: 10 ventas, 28 hot dogs
  2024-11-02: 15 ventas, 42 hot dogs
  ...
  2024-11-07: 18 ventas, 50 hot dogs
```

**Descripción del gráfico:**
- **Tipo**: Barras agrupadas
- **Grupos**: Ventas (azul) y Hot Dogs (magenta)
- **Características**: 
  - Dos barras por fecha
  - Valores etiquetados
  - Leyenda clara

---

### 5.6 Reporte General (Texto)

**Ruta:** Reportes → Opción 6

**Función:** Reporte estadístico completo en formato texto.

**Ejemplo:**
```
REPORTE GENERAL DE ESTADÍSTICAS

═══════════════════════════════════════════════════════════

Período:
  Desde: 2024-11-01
  Hasta: 2024-11-30
  Días con ventas: 25

Ventas:
  Total de ventas: 287
  Total de hot dogs: 825
  Promedio por venta: 2.87

Tamaño de ventas:
  Venta más grande: 5 hot dogs
  Venta más pequeña: 1 hot dog

Top 5 Hot Dogs:
  1. simple: 145 unidades
  2. combo especial: 128 unidades
  3. fitness: 98 unidades
  4. económico: 87 unidades
  5. premium: 75 unidades

Ventas por franja horaria:
  Mañana (6am-12pm): 95
  Tarde (1pm-6pm): 128
  Noche (7pm-11pm): 64

═══════════════════════════════════════════════════════════
```

---

## Menú Debug

**Acceso:** Menú Principal → Opción 9

### Opciones Disponibles

```
🔧 DEBUG - SYSTEM DIAGNOSTICS

1. 📋 Show Entity Classes
2. 📦 Show Categories
3. 🔍 Compare Classes vs Categories
4. 🔄 Reset Data (Reload from GitHub)
```

---

### Reset Data (Reload from GitHub)

**Ruta:** Debug → Opción 4

**Función:** Reinicia el sistema a estado inicial eliminando todos los datos locales.

**⚠️ Proceso con Doble Confirmación:**

```
RESET DE DATOS

⚠️  ADVERTENCIA

Esta acción eliminará:
  • Todos los datos locales (data/)
  • Todos los gráficos generados (charts/)
  • Todas las ventas registradas
  • Todos los cambios de inventario
  • Todos los hot dogs agregados al menú

Los datos se recargarán desde GitHub al reiniciar.

Esta acción NO se puede deshacer.

¿Estás seguro de que quieres resetear todos los datos? (y/n): y

¿Estás REALMENTE seguro? Esta es tu última oportunidad. (y/n): y

Reseteando datos...

  ✓ Directorio data/ eliminado
  ✓ Directorio charts/ eliminado

✅ Datos reseteados exitosamente!

La aplicación se cerrará.
ℹ️  Ejecuta python main.py para reiniciar con datos frescos desde GitHub.

Presiona Enter para continuar...
```

**Después del reset:**
```bash
python main.py
```

El sistema descargará datos frescos desde GitHub.

---

## Preguntas Frecuentes

### ❓ ¿Cómo vuelvo al estado inicial?

**Respuesta:** Usa la función Reset Data en el menú Debug (Opción 9 → Opción 4). Esto eliminará todos los cambios locales y recargará desde GitHub.

---

### ❓ ¿Dónde se guardan mis ventas?

**Respuesta:** Las ventas se guardan en `data/ventas.json`. Este archivo se crea automáticamente la primera vez que registras o simulas una venta.

---

### ❓ ¿Dónde están los gráficos generados?

**Respuesta:** Los gráficos se guardan en el directorio `charts/` en formato PNG. Puedes abrirlos con cualquier visor de imágenes.

---

### ❓ ¿Puedo agregar ingredientes que no están en GitHub?

**Respuesta:** Sí, usa la opción "Agregar ingrediente" en el módulo de Ingredientes. Estos ingredientes se guardan localmente en `data/ingredientes.json`.

---

### ❓ ¿Qué pasa si elimino un ingrediente que está en un hot dog?

**Respuesta:** El sistema te advertirá y mostrará qué hot dogs se eliminarán también. Debes confirmar explícitamente para proceder.

---

### ❓ ¿Puedo vender un hot dog sin inventario?

**Respuesta:** No. El sistema verifica inventario antes de confirmar la venta. Si falta algún ingrediente, la venta no se puede completar.

---

### ❓ ¿Cómo funciona el merge automático en ventas?

**Respuesta:** Si agregas el mismo hot dog varias veces al draft, el sistema suma las cantidades automáticamente en lugar de crear items duplicados.

**Ejemplo:**
```
add simple x2
add simple x1
= simple x3 (no dos items separados)
```

---

### ❓ ¿Las simulaciones afectan el inventario real?

**Respuesta:** Sí. Las simulaciones descuentan inventario como ventas reales. Usa Reset Data si quieres volver al inventario inicial.

---

### ❓ ¿Puedo comparar fechas que no tienen ventas?

**Respuesta:** Sí, el gráfico mostrará esas fechas con valores en 0.

---

### ❓ ¿Qué formato de fecha debo usar?

**Respuesta:** Siempre usa el formato `YYYY-MM-DD` (ejemplo: `2024-11-16`). Para filtros por mes, usa `YYYY-MM` (ejemplo: `2024-11`).

---

### ❓ ¿El sistema valida tamaños de pan y salchicha?

**Respuesta:** Sí. Si los tamaños no coinciden, recibirás una advertencia pero puedes continuar si lo confirmas.

---

### ❓ ¿Puedo cancelar una operación en cualquier momento?

**Respuesta:** Sí. En confirmaciones, responde `n` (no). En construcción de ventas, usa el comando `cancel`.

---

## 📞 Soporte

Para problemas técnicos o preguntas adicionales sobre el uso del sistema, consulta la documentación técnica en [DESARROLLO.md](DESARROLLO.md).

---

**Hot Dog CCS - Sistema de Gestión**  
**Versión 1.0**  
**Desarrollado por Rafael Correa - Universidad Metropolitana**
