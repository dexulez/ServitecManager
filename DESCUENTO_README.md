# Actualización: Funcionalidad de Descuento

## Cambios Implementados

### 1. Base de Datos
- ✅ Agregada columna `descuento` (INTEGER DEFAULT 0) a la tabla `ordenes`
- ✅ Base de datos limpiada (todas las órdenes, ventas, finanzas, pedidos eliminados)
- ✅ Usuarios y clientes mantenidos intactos

### 2. Interfaz de Recepción (UI)
- ✅ Nuevo campo "DESCUENTO" agregado en la sección de montos
- ✅ Campo ubicado entre PRESUPUESTO y ABONO
- ✅ Validación y formato de dinero aplicados automáticamente
- ✅ Variable `self.var_discount` creada y configurada

### 3. Lógica de Negocio
- ✅ Función `CREAR_ORDEN()` actualizada para recibir parámetro `descuento`
- ✅ Función `ACTUALIZAR_ORDEN()` actualizada para incluir descuento
- ✅ INSERT y UPDATE queries modificados para incluir el nuevo campo

### 4. Generación de PDF
- ✅ PDF actualizado para mostrar el descuento en el bloque financiero
- ✅ Índices de datos corregidos (descuento: 13, abono: 14, fecha_entrega: 15)
- ✅ Datos del cliente mantienen índices correctos (rut: 16, nombre: 17, teléfono: 18)

## Funcionamiento

Cuando se crea una orden:
1. El usuario ingresa el PRESUPUESTO (precio total sin descuento)
2. Opcionalmente ingresa un DESCUENTO (monto a descontar)
3. El ABONO es el pago inicial recibido
4. El sistema guarda todos estos valores en la base de datos
5. El PDF muestra:
   - SUBTOTAL (presupuesto sin IVA)
   - DESCUENTO (si aplica)
   - IVA (19%)
   - TOTAL (presupuesto final)
   - ABONO (pago recibido)
   - SALDO (total - abono)

## Notas Técnicas

- El descuento se almacena como INTEGER (centavos/pesos)
- El campo es opcional (DEFAULT 0)
- Compatible con órdenes existentes (valores NULL se tratan como 0)
- El historial muestra el campo TOTAL (presupuesto) sin mostrar descuento separado

## Próximos Pasos Opcionales

Si deseas que el historial muestre la columna de descuento:
1. Agregar columna DESCUENTO al header del historial
2. Modificar query `OBTENER_HISTORIAL_COMPLETO_ORDENES` para incluir `o.descuento`
3. Ajustar índices en history.py para mostrar el descuento

---

**Fecha:** 15 de diciembre de 2025
**Versión:** ServitecManager v1.1
**Commit:** dddf487
