# NUEVA FUNCIÓN: EDICIÓN DE PRECIOS DE REPUESTOS

## 📝 Descripción
Se ha agregado un botón de **EDITAR** en el modal de búsqueda de repuestos que permite modificar directamente los precios, costos y stock de los repuestos sin necesidad de usar archivos Excel.

## 🎯 Ubicación
- **Módulo:** Recepción de Equipos
- **Acceso:** Al hacer clic en "🔍 BUSCAR" para seleccionar un repuesto

## 🔧 Funcionalidad

### Botón EDITAR
- **Ubicación:** Al lado del botón "ELEGIR" en cada repuesto de la lista
- **Color:** Naranja (#F39C12)
- **Icono:** ✏️ EDITAR

### Ventana de Edición
Al hacer clic en "✏️ EDITAR", se abre una ventana modal que muestra:

1. **Información del Repuesto:**
   - Nombre del repuesto
   - Categoría

2. **Campos Editables:**
   - **COSTO DE COMPRA ($):** Precio al que se compra el repuesto al proveedor
   - **PRECIO DE VENTA ($):** Precio al que se vende al cliente
   - **STOCK DISPONIBLE:** Cantidad en inventario

3. **Formato Automático:**
   - Los campos de dinero se formatean automáticamente con separadores de miles (puntos)
   - El stock solo acepta números enteros

### Validaciones
- El precio de venta debe ser mayor a 0
- El costo no puede ser negativo
- El stock no puede ser negativo
- Solo se aceptan valores numéricos válidos

### Guardar Cambios
- **Botón:** 💾 GUARDAR CAMBIOS (Verde)
- **Acción:** Actualiza los datos en la base de datos
- **Resultado:** La lista de repuestos se recarga automáticamente con los nuevos valores
- **Confirmación:** Mensaje de éxito al guardar correctamente

### Cancelar
- **Botón:** ❌ CANCELAR (Gris)
- **Acción:** Cierra la ventana sin guardar cambios

## 💡 Ventajas

1. **Edición Rápida:** No es necesario salir del módulo de recepción
2. **Sin Excel:** No requiere descargar plantillas ni importar archivos
3. **Inmediato:** Los cambios se aplican instantáneamente
4. **Validación en Tiempo Real:** Previene errores de entrada
5. **Formato Automático:** Los valores monetarios se formatean correctamente

## 🔄 Flujos de Trabajo

### Opción 1: Edición Individual (NUEVO)
1. Ir a Recepción → Buscar repuesto
2. Click en "✏️ EDITAR"
3. Modificar precio/costo/stock
4. Guardar cambios
5. ✅ Listo

### Opción 2: Edición Masiva (Existente)
1. Ir a Proveedores
2. Click en "📋 GENERAR PLANTILLA VACÍA"
3. Llenar precios en Excel
4. Click en "📥 CARGAR ARCHIVO EXCEL"
5. ✅ Listo

## 📋 Ejemplo de Uso

**Escenario:** Necesitas actualizar el precio de un conector USB-C

1. Vas a **Recepción** para ingresar un equipo
2. Click en "🔍 BUSCAR" en la sección de REPUESTO
3. Buscas "CONECTOR USB-C"
4. Click en "✏️ EDITAR"
5. Cambias:
   - Costo: $8.000 → $10.000
   - Precio: $15.000 → $18.000
   - Stock: 5 → 3
6. Click en "💾 GUARDAR CAMBIOS"
7. ✅ El repuesto queda actualizado inmediatamente

## 🛠️ Implementación Técnica

### Archivo Modificado
- `servitec_manager/ui/reception.py`

### Métodos Agregados
1. **`open_edit_part_dialog()`**
   - Abre el diálogo de edición
   - Crea formulario con validaciones
   - Maneja el guardado de cambios

2. **Modificación en `render_search_list()`**
   - Agregado botón "✏️ EDITAR" solo para repuestos (no servicios)

### Base de Datos
Utiliza los métodos existentes en `logic.py`:
- `update_part(id, nombre, categoria, costo, precio, stock)` - Actualización completa

### Validaciones
- Formato de dinero con `clean_money()`
- Formato de enteros con `format_live_int()`
- Validación de valores positivos
- Manejo de excepciones

## ⚠️ Notas Importantes

1. Solo aparece el botón EDITAR en la búsqueda de **REPUESTOS**, no en servicios
2. Los cambios son **inmediatos** en la base de datos
3. La lista se **recarga automáticamente** después de guardar
4. El nombre y categoría **NO** se pueden editar desde aquí (solo precio, costo, stock)

## 🎨 Diseño UI

- **Ventana:** 500x450px, centrada en pantalla
- **Botón EDITAR:** Naranja (#F39C12), 70px ancho
- **Botón GUARDAR:** Verde (#28a745)
- **Botón CANCELAR:** Gris
- **Campos:** Altura 35px, formato automático
- **Modal:** Topmost, transient, grab_set (modal verdadero)

## 📝 Versión
- **Fecha de Implementación:** 2025
- **Estado:** ✅ Completado y Funcional
