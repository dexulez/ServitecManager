# 🔄 ACTUALIZACIÓN AUTOMÁTICA DE SERVITEC MANAGER

## Para el otro computador

### Windows (Recomendado)

1. **Abrir el explorador de archivos** y navegar a la carpeta donde está instalado ServitecManager

2. **Doble clic en:** `actualizar.bat`

3. El script hará automáticamente:
   - ✅ Descargar últimos cambios de GitHub
   - ✅ Aplicar migración de base de datos (columna descuento)
   - ✅ Limpiar caché antiguo
   - ✅ Verificar e instalar dependencias
   - ✅ Iniciar ServitecManager

### Linux/Mac

1. Abrir terminal en la carpeta de ServitecManager

2. Dar permisos de ejecución (solo primera vez):
   ```bash
   chmod +x actualizar.sh
   ```

3. Ejecutar:
   ```bash
   ./actualizar.sh
   ```

## Actualización manual paso a paso

Si el script automático no funciona:

```bash
# 1. Actualizar código
git pull origin main

# 2. Aplicar migración
cd servitec_manager
python migrar_descuento.py

# 3. Limpiar caché
rm -rf __pycache__
rm -rf ui/__pycache__

# 4. Instalar dependencias (si falta alguna)
pip install -r requirements.txt

# 5. Ejecutar
python main.py
```

## Verificación de actualización exitosa

Después de actualizar, verifica que:

- ✅ La aplicación inicia sin errores
- ✅ En **Recepción** aparece el campo "DESCUENTO ($):"
- ✅ Puedes crear órdenes normalmente
- ✅ El **Historial** muestra los totales correctos con descuento aplicado
- ✅ Los **PDFs** generados muestran el descuento

## Solución de problemas

### Error: "git pull" falla

Si no tienes Git instalado o configurado:

1. Descargar el código manualmente desde:
   https://github.com/dexulez/ServitecManager

2. Extraer y reemplazar los archivos en tu instalación actual

3. **IMPORTANTE:** No reemplaces la carpeta `servitec_manager` completa, 
   solo los archivos de código (`.py`)

4. Mantén tu base de datos `SERVITEC.DB` intacta

### Error: "table ordenes has no column named descuento"

Ejecutar manualmente la migración:
```bash
cd servitec_manager
python migrar_descuento.py
```

### La aplicación no inicia

1. Verificar versión de Python:
   ```bash
   python --version
   ```
   Debe ser 3.10 o superior

2. Reinstalar dependencias:
   ```bash
   cd servitec_manager
   pip install -r requirements.txt
   ```

3. Ejecutar diagnóstico:
   ```bash
   python diagnostico.py
   ```

## Archivos importantes que NO se deben modificar

Durante la actualización, estos archivos se mantienen intactos:

- ✅ `SERVITEC.DB` - Tu base de datos
- ✅ `ordenes/` - PDFs generados
- ✅ `backups/` - Respaldos
- ✅ `reports/` - Reportes generados

## Frecuencia recomendada de actualización

- **Diaria:** Si hay cambios activos en desarrollo
- **Semanal:** Para mantenimiento regular
- **Inmediata:** Cuando se reporte un bug crítico

## Soporte

Si tienes problemas con la actualización:

1. Revisa los mensajes de error en la terminal
2. Ejecuta `python diagnostico.py` en la carpeta `servitec_manager`
3. Contacta con el mensaje de error completo

---

**Última actualización:** 16 de diciembre de 2025
