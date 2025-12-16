# 🔄 INSTRUCCIONES PARA ACTUALIZAR EN EL OTRO COMPUTADOR

## Pasos para actualizar ServitecManager

### 1️⃣ Abrir PowerShell o CMD en la carpeta de ServitecManager

```bash
cd C:\ruta\donde\esta\ServitecManager
```

### 2️⃣ Ejecutar el script de actualización

**Opción A - Automática (Recomendada):**
```bash
actualizar.bat
```

**Opción B - Manual:**
```bash
git pull
cd servitec_manager
python migrar_descuento.py
python main.py
```

---

## ⚡ Comandos rápidos para copiar y pegar

### Si tienes Git configurado:
```powershell
git pull
cd servitec_manager
python main.py
```

### Si aparece error de columna descuento:
```powershell
cd servitec_manager
python migrar_descuento.py
python main.py
```

### Para actualización completa:
```powershell
git pull
cd servitec_manager
python migrar_descuento.py
rd /s /q __pycache__
rd /s /q ui\__pycache__
python main.py
```

---

## 🆕 Nuevas características actualizadas

✅ **Campo de descuento** en recepción de órdenes
✅ **Cálculo correcto** de totales con descuento
✅ **PDFs actualizados** con descuento aplicado
✅ **Historial** muestra totales correctos
✅ **Botón de respaldo** en Administración
✅ **Botón de limpiar BD** en Administración
✅ **Migración automática** al iniciar
✅ **Corrección de índices** en datos de cliente

---

## 🐛 Solución de problemas

### Error: "table ordenes has no column named descuento"
```powershell
cd servitec_manager
python migrar_descuento.py
```

### Error: "git command not found"
Descargar manualmente desde: https://github.com/dexulez/ServitecManager
Extraer y reemplazar archivos (mantener SERVITEC.DB intacta)

### La aplicación no inicia
```powershell
cd servitec_manager
pip install -r requirements.txt
python main.py
```

---

## 📝 Verificación post-actualización

Después de actualizar, verifica:

- [ ] Campo "DESCUENTO ($):" visible en Recepción
- [ ] PDFs se generan correctamente con descuento
- [ ] Historial muestra órdenes sin errores
- [ ] Botones de respaldo/limpiar en Administración
- [ ] Técnicos aparecen en lista al crear órdenes

---

## 📞 Soporte

Si hay problemas:
1. Capturar pantallazo del error
2. Ejecutar: `cd servitec_manager && python diagnostico.py`
3. Enviar resultado

**Fecha de actualización:** 16 de diciembre de 2025
