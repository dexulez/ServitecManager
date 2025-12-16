# 🔧 INSTRUCCIONES PARA ACTUALIZAR EN EL OTRO COMPUTADOR

## Problema
El error `table ordenes has no column named descuento` indica que la base de datos no tiene la columna descuento.

## Solución

### OPCIÓN 1: Actualización Automática (Recomendada)

1. **Cerrar ServitecManager** si está abierto

2. **Actualizar desde GitHub:**
   ```bash
   cd C:\ruta\a\ServitecManager
   git pull
   ```

3. **Ejecutar el script de migración:**
   ```bash
   cd servitec_manager
   python migrar_descuento.py
   ```

4. **Reiniciar ServitecManager:**
   ```bash
   python main.py
   ```

### OPCIÓN 2: Actualización Manual (Si no funciona la Opción 1)

1. **Cerrar ServitecManager**

2. **Descargar instalador desde GitHub:**
   - Ir a: https://github.com/dexulez/ServitecManager
   - Descargar código actualizado

3. **Hacer backup de la base de datos:**
   ```bash
   copy servitec_manager\SERVITEC.DB servitec_manager\SERVITEC.DB.backup
   ```

4. **Ejecutar migración manual:**
   ```bash
   cd servitec_manager
   python migrar_descuento.py
   ```

5. **Verificar que funcionó:**
   - El script debería mostrar: "✓ Columna 'descuento' agregada exitosamente"

6. **Iniciar ServitecManager:**
   ```bash
   python main.py
   ```

### OPCIÓN 3: Desde PowerShell (Una línea)

```powershell
cd C:\ruta\a\ServitecManager\servitec_manager; python migrar_descuento.py; python main.py
```

## Verificación

Si la migración fue exitosa, verás:
- ✅ Sin errores al iniciar
- ✅ Campo "DESCUENTO ($):" visible en Recepción
- ✅ Órdenes se generan correctamente
- ✅ PDF muestra descuento correctamente

## Si persiste el error

1. **Verificar versión de Python:**
   ```bash
   python --version
   ```
   Debe ser Python 3.10 o superior

2. **Verificar que existe la base de datos:**
   ```bash
   dir servitec_manager\SERVITEC.DB
   ```

3. **Ejecutar diagnóstico:**
   ```bash
   cd servitec_manager
   python diagnostico.py
   ```

## Contacto

Si ninguna opción funciona, contactar con el mensaje de error completo.

---
**Última actualización:** 16 de diciembre de 2025
