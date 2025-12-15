# 🔧 SOLUCIÓN: Errores de Actualización en ServitecManager

## Problema 1: Error de Git "local changes would be overwritten"
```
error: Your local changes to the following files would be overwritten by merge:
        actualizar_servitec.bat
```

### Solución INMEDIATA:
1. Descarga el archivo: `resolver_conflictos.bat` del repositorio
2. Ejecútalo (doble clic)
3. El script descartará cambios locales y actualizará todo automáticamente

### O manualmente:
```batch
cd C:\Users\TuUsuario\Documents\ServitecManager
git reset --hard HEAD
git pull origin main
```

---

## Problema 2: Error "table ordenes has no column named descuento"
```
Error en EJECUTAR_CONSULTA: table ordenes has no column named descuento
```

### Causa
La base de datos local no tiene la nueva columna `descuento` que se agregó en la última actualización.

### Solución Rápida

### Opción 1: Ejecutar actualizar_servitec.bat (RECOMENDADO)
El actualizador ahora incluye migraciones automáticas:

1. Ejecuta `actualizar_servitec.bat`
2. El script descargará los cambios y aplicará automáticamente la migración
3. Reinicia ServitecManager

### Opción 2: Migración Manual
Si ya ejecutaste git pull manualmente:

1. Abre una terminal en: `C:\Users\TuUsuario\Documents\ServitecManager\servitec_manager`
2. Activa el entorno virtual:
   ```
   ..\.venv\Scripts\activate
   ```
3. Ejecuta la migración:
   ```
   python migrar_descuento.py
   ```
4. Presiona ENTER cuando termine
5. Reinicia ServitecManager

### Opción 3: SQL Directo
Si prefieres ejecutar SQL directamente:

1. Abre la base de datos `SERVITEC.DB` con un cliente SQLite
2. Ejecuta:
   ```sql
   ALTER TABLE ordenes ADD COLUMN descuento INTEGER DEFAULT 0;
   ```

## Verificación
Después de aplicar la solución, verifica que:
- ✅ ServitecManager inicia sin errores
- ✅ Puedes crear órdenes nuevas
- ✅ El campo DESCUENTO aparece en la recepción de equipos
- ✅ Los PDFs se generan correctamente

## Notas Importantes
- Esta migración solo necesita ejecutarse una vez por instalación
- No afecta datos existentes en la base de datos
- Es compatible con órdenes creadas antes de la actualización
- El actualizador automático aplicará futuras migraciones automáticamente

---
**Última actualización:** 15 de diciembre de 2025
