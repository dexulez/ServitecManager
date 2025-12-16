# 🐛 SOLUCIÓN: Bug de corrupción de datos de cliente al editar orden

## Problema identificado

Al editar una orden existente, los datos del cliente se corrompían y se creaba un nuevo cliente con datos erróneos. Por ejemplo:
- RUT mostraba "Pendiente" (estado de la orden)
- Nombre mostraba "1000" (posiblemente ID o monto)

## Causa raíz

La tabla `ordenes` tiene actualmente **17 columnas** (índices 0-16):
```
0: id
1: cliente_id  
2: tecnico_id
3: fecha
4: equipo
5: marca
6: modelo
7: serie
8: observacion
9: estado
10: accesorios
11: riesgoso
12: presupuesto
13: abono
14: fecha_entrega
15: condicion
16: descuento
```

El query `get_ticket_data()` hace:
```sql
SELECT o.*, c.rut, c.nombre, c.telefono, c.email FROM ordenes o JOIN clientes c ...
```

Esto devuelve:
- **Índices 0-16**: columnas de ordenes (17 columnas)
- **Índice 17**: c.rut
- **Índice 18**: c.nombre
- **Índice 19**: c.telefono
- **Índice 20**: c.email

Sin embargo, el código estaba usando índices incorrectos basados en un comentario desactualizado que decía "ordenes tiene 15 columnas (0-14)":
- ❌ `orden_data[15]` → Leía "condicion" en lugar de "rut"
- ❌ `orden_data[16]` → Leía "descuento" en lugar de "nombre"
- ❌ `orden_data[17]` → Leía "rut" en lugar de "telefono"
- ❌ `orden_data[18]` → Leía "nombre" en lugar de "email"

Esto causaba que al editar:
1. El campo RUT se llenara con el valor de "condicion" (a veces "Pendiente")
2. El campo Nombre se llenara con el valor de "descuento" (números)
3. Se creara un nuevo cliente con estos datos erróneos

## Solución aplicada

### 1. servitec_manager/ui/reception.py

**Líneas ~1500-1510** - Método `load_order_for_edit()`:
```python
# Antes (INCORRECTO):
self.var_rut.set(order_data[15])
self.var_name.set(order_data[16])
self.var_tel.set(order_data[17] if order_data[17] else "")
self.var_email.set(order_data[18] if order_data[18] else "")
self.selected_client_rut = order_data[15]

# Después (CORRECTO):
self.var_rut.set(order_data[17])
self.var_name.set(order_data[18])
self.var_tel.set(order_data[19] if order_data[19] else "")
self.var_email.set(order_data[20] if order_data[20] else "")
self.selected_client_rut = order_data[17]
```

**Línea ~1545** - Agregar carga del campo descuento:
```python
# Agregado:
self.var_discount.set(str(int(order_data[16])) if order_data[16] else "0")
```

**Línea ~1479** - Método `view_ticket_modal()`:
```python
# Antes (INCORRECTO):
info = f"...CLIENTE: {data[16]}..."

# Después (CORRECTO):
info = f"...CLIENTE: {data[18]}..."
```

### 2. servitec_manager/ui/history.py

**Línea ~202**:
```python
# Antes (INCORRECTO):
add_sec("CLIENTE", f"Nombre: {tdata[15]}\nRUT: {tdata[14]}\nTeléfono: {tdata[16]}\nEmail: {tdata[17]}")

# Después (CORRECTO):
add_sec("CLIENTE", f"Nombre: {tdata[18]}\nRUT: {tdata[17]}\nTeléfono: {tdata[19]}\nEmail: {tdata[20]}")
```

### 3. servitec_manager/pdf_generator_v2.py

**Líneas ~229-244**:
```python
# Antes (INCORRECTO):
cliente_nombre = str(orden_data[17] or "").upper()[:30]
cliente_rut = str(orden_data[16] or "")
cliente_tel = str(orden_data[18] or "")

# Después (CORRECTO):
cliente_nombre = str(orden_data[18] or "").upper()[:30]
cliente_rut = str(orden_data[17] or "")
cliente_tel = str(orden_data[19] or "")
```

## Archivos modificados

1. ✅ `servitec_manager/ui/reception.py`
   - Corregidos índices de datos del cliente en `load_order_for_edit()`
   - Agregada carga del campo descuento
   - Corregido índice en `view_ticket_modal()`

2. ✅ `servitec_manager/ui/history.py`
   - Corregidos índices de datos del cliente en vista de detalle

3. ✅ `servitec_manager/pdf_generator_v2.py`
   - Corregidos índices de datos del cliente en generación de PDF

## Pruebas recomendadas

1. ✅ Editar una orden existente
2. ✅ Verificar que los datos del cliente se carguen correctamente
3. ✅ Guardar cambios y verificar que no se cree un cliente duplicado
4. ✅ Generar PDF y verificar que muestre datos correctos del cliente
5. ✅ Ver historial de cliente y verificar que muestre datos correctos

## Estado

✅ **SOLUCIONADO** - Corregidos todos los índices en los 3 archivos afectados.

## Fecha
16 de diciembre de 2025
