# 🔧 SOLUCIÓN AL ERROR DE ACTUALIZACIÓN

## Error que aparece:
```
error: Your local changes to the following files would be overwritten by merge:
        servitec_manager/SERVITEC.DB
Please commit your changes or stash them before you merge.
```

## ✅ SOLUCIÓN RÁPIDA (Copiar y pegar en PowerShell):

```powershell
cd C:\ruta\a\ServitecManager
git stash push servitec_manager/SERVITEC.DB -m "Guardar BD local"
git pull origin main
git stash pop
cd servitec_manager
python main.py
```

## O USAR ESTOS COMANDOS ALTERNATIVOS:

### Opción 1: Descartar cambios de la BD (si no te importa usar la BD del repositorio)
```powershell
cd C:\ruta\a\ServitecManager
git checkout servitec_manager/SERVITEC.DB
git pull origin main
cd servitec_manager
python main.py
```

### Opción 2: Mantener tu BD actual y solo actualizar el código
```powershell
cd C:\ruta\a\ServitecManager
git add servitec_manager/SERVITEC.DB
git commit -m "Guardar BD local"
git pull origin main
cd servitec_manager
python main.py
```

### Opción 3: Forzar actualización (CUIDADO: sobrescribe todo)
```powershell
cd C:\ruta\a\ServitecManager
git reset --hard origin/main
cd servitec_manager
python main.py
```

## 🔄 DESPUÉS DE RESOLVER:

1. Ejecutar de nuevo:
```powershell
actualizar.bat
```

2. O simplemente:
```powershell
cd servitec_manager
python main.py
```

## 📝 NOTA IMPORTANTE:

- La SERVITEC.DB se modifica cada vez que usas el programa
- Es normal que Git detecte cambios en ella
- El script actualizar.bat ahora maneja esto automáticamente
- Después de hacer `git pull` una vez con la solución, podrás usar `actualizar.bat` sin problemas

## ✅ El script actualizar.bat ya está corregido en GitHub

La próxima vez que actualices, el script manejará automáticamente los cambios en la base de datos.

---
**Fecha:** 16 de diciembre de 2025
