# 🔧 SOLUCIÓN: Problemas con Descuentos y Visualización de Órdenes

## Síntomas
- Los descuentos no se aplican en el PDF (aparece $0)
- Las órdenes no se visualizan en el historial
- Esto ocurre en el computador remoto después de actualizar

## Diagnóstico Rápido

1. **Abre PowerShell** en la carpeta del proyecto
2. Navega al directorio: 
   ```
   cd C:\Users\MAYA\Documents\ServitecManager\servitec_manager
   ```
3. Ejecuta el diagnóstico:
   ```
   python diagnostico.py
   ```

El script te mostrará:
- ✅ Si la columna descuento existe
- 📊 Cuántas órdenes hay en la base de datos
- 🔍 Datos de la última orden
- 📋 Qué órdenes aparecen en el historial

## Soluciones por Problema

### Problema 1: Columna descuento no existe

**Síntoma:** El diagnóstico muestra "❌ La columna 'descuento' NO EXISTE"

**Solución:**
```powershell
cd C:\Users\MAYA\Documents\ServitecManager
git pull origin main
cd servitec_manager
python main.py
```
La migración automática se aplicará al iniciar.

### Problema 2: Código desactualizado

**Síntoma:** El código no tiene los últimos cambios

**Solución:**
```powershell
cd C:\Users\MAYA\Documents\ServitecManager
git status
# Si hay cambios locales:
git reset --hard HEAD
git pull origin main
```

### Problema 3: Cache corrupto

**Síntoma:** Los datos no se reflejan correctamente

**Solución:**
```powershell
cd C:\Users\MAYA\Documents\ServitecManager\servitec_manager
# Eliminar archivos de cache
Remove-Item -Recurse -Force __pycache__
Remove-Item -Recurse -Force ui\__pycache__
# Reiniciar aplicación
python main.py
```

### Problema 4: Base de datos no sincronizada

**Síntoma:** La orden existe pero no se ve en historial

**Solución:**
1. Cerrar ServitecManager completamente
2. Ejecutar:
   ```powershell
   cd C:\Users\MAYA\Documents\ServitecManager\servitec_manager
   python -c "import sqlite3; conn = sqlite3.connect('SERVITEC.DB'); conn.execute('PRAGMA optimize'); conn.close(); print('Base de datos optimizada')"
   ```
3. Reiniciar ServitecManager

## Verificación Final

Después de aplicar las soluciones:

1. **Crear una orden de prueba** con descuento de $1000
2. **Verificar el PDF generado**: 
   - Debe mostrar el descuento en la sección financiera
   - El TOTAL debe reflejar: (Presupuesto - Descuento + IVA)
3. **Verificar el Historial**:
   - La orden debe aparecer inmediatamente
   - Los datos deben ser correctos

## Comandos de Actualización Completa

Si todo lo anterior falla, ejecuta una actualización completa:

```powershell
cd C:\Users\MAYA\Documents\ServitecManager

# 1. Descartar cambios locales
git reset --hard HEAD

# 2. Actualizar código
git pull origin main

# 3. Limpiar cache
cd servitec_manager
Remove-Item -Recurse -Force __pycache__, ui\__pycache__ -ErrorAction SilentlyContinue

# 4. Ejecutar diagnóstico
python diagnostico.py

# 5. Iniciar aplicación (aplicará migraciones automáticas)
python main.py
```

## Soporte Adicional

Si los problemas persisten, ejecuta el diagnóstico y envía el resultado completo.

---
**Última actualización:** 16 de diciembre de 2025  
**Versión:** ServitecManager v1.2
