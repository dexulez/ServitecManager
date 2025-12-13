# 📦 ACTUALIZACIÓN DE SERVITECMANAGER VÍA PENDRIVE

## ✅ ARCHIVOS EXPORTADOS EXITOSAMENTE

**Fecha de exportación:** 4 de diciembre de 2025  
**Versión:** 1.1.0  

### 📊 Contenido de la base de datos exportada:
- ✅ **3** clientes
- ✅ **3** órdenes de servicio  
- ✅ **917** repuestos en inventario
- ✅ **1** proveedor
- ✅ **44** modelos de equipos
- ✅ Notificaciones del sistema
- ✅ Configuración de versión

**Tamaño de la base de datos:** 444 KB

---

## 📁 QUÉ COPIAR AL PENDRIVE

Copia **TODA** la carpeta `ServitecManager` al pendrive, que incluye:

```
📂 ServitecManager/
├── 📂 servitec_manager/              # Código fuente actualizado
├── 📂 BASE_DATOS_EXPORT_20251204_175753/  # Tu base de datos
│   ├── SERVITEC.DB                   # Base de datos completa
│   ├── LEEME_IMPORTACION.txt         # Instrucciones detalladas
│   ├── INFO_BASE_DATOS.json          # Estadísticas
│   ├── notificaciones.db.json        # Notificaciones
│   └── version.json                  # Versión
├── actualizar_desde_pendrive.py      # Script de actualización automática
├── exportar_base_datos.py            # Herramienta de backup
├── PREPARAR_PENDRIVE.bat             # Preparador automático
└── INSTRUCCIONES_ACTUALIZACION_PENDRIVE.md  # Este archivo
```

---

## 🔄 OPCIÓN 1: ACTUALIZACIÓN AUTOMÁTICA (RECOMENDADO)

### En el otro computador:

1. **Conecta el pendrive** con la carpeta ServitecManager

2. **Cierra ServitecManager** si está abierto

3. **Ejecuta el script de actualización:**
   ```
   Doble clic en: actualizar_desde_pendrive.py
   ```
   O desde PowerShell:
   ```powershell
   cd E:\ServitecManager  # (Cambia E: por la letra de tu pendrive)
   python actualizar_desde_pendrive.py
   ```

4. **Sigue las instrucciones en pantalla:**
   - Te preguntará dónde está instalado ServitecManager (por defecto: `C:\ServitecManager`)
   - Confirmará la ubicación
   - Creará un backup automático de tu base de datos actual
   - Copiará todos los archivos actualizados
   - **Preservará tu base de datos** del otro PC (no la sobrescribirá)

5. **Verifica que todo funcione:**
   - Abre ServitecManager normalmente
   - Revisa que tus datos estén intactos

---

## 📥 OPCIÓN 2: IMPORTAR TU BASE DE DATOS AL OTRO PC

Si quieres llevar **TUS datos** (clientes, órdenes, repuestos) al otro computador:

### Paso 1: Actualizar el código

Ejecuta `actualizar_desde_pendrive.py` como se indicó arriba.

### Paso 2: Importar tu base de datos

**Método A - Automático:**
```powershell
cd E:\ServitecManager  # Cambia E: por tu pendrive
python exportar_base_datos.py
# Selecciona opción 2 (IMPORTAR)
```

**Método B - Manual:**

1. Cierra ServitecManager en el otro PC

2. Navega a: `C:\ServitecManager\servitec_manager\`

3. **Crea un backup** de la base de datos actual:
   ```
   Copia SERVITEC.DB → SERVITEC_BACKUP.DB
   ```

4. **Copia tu base de datos:**
   ```
   Desde: E:\ServitecManager\BASE_DATOS_EXPORT_20251204_175753\SERVITEC.DB
   Hacia: C:\ServitecManager\servitec_manager\SERVITEC.DB
   ```

5. Abre ServitecManager y verifica tus datos

---

## ⚠️ IMPORTANTE - LEE ANTES DE CONTINUAR

### ✅ Lo que SÍ hace el actualizador automático:
- ✅ Actualiza todo el código de ServitecManager
- ✅ Crea backup automático de la base de datos del otro PC
- ✅ **PRESERVA** la base de datos existente en el otro PC
- ✅ Mantiene carpetas de órdenes, reportes y backups
- ✅ Actualiza todas las funcionalidades a la última versión

### ❌ Lo que NO hace (para tu seguridad):
- ❌ **NO** sobrescribe tu base de datos automáticamente
- ❌ **NO** mezcla datos de ambos PCs
- ❌ **NO** elimina información existente

### 🔀 Para combinar datos de ambos PCs:

**No es posible automáticamente.** Tendrías que:
1. Elegir qué base de datos usar (la del pendrive o la del otro PC)
2. Si quieres ambas, necesitarás importar manualmente los datos que falten

---

## 🆘 SOLUCIÓN DE PROBLEMAS

### ❌ Error: "No se encuentra python"
```powershell
# Instala Python 3.13 o superior desde python.org
# O usa el ejecutable completo:
C:\Users\TuUsuario\AppData\Local\Programs\Python\Python313\python.exe actualizar_desde_pendrive.py
```

### ❌ Error: "Archivo en uso" o "Permiso denegado"
1. Cierra ServitecManager completamente
2. Abre el Administrador de Tareas (Ctrl+Shift+Esc)
3. Finaliza cualquier proceso `python.exe` relacionado
4. Intenta nuevamente

### ❌ Error: "No se encuentra la base de datos"
- Verifica que la carpeta `BASE_DATOS_EXPORT_*` esté en el pendrive
- Asegúrate de estar ejecutando desde la carpeta correcta

### ❌ "Perdí mis datos después de actualizar"
- No te preocupes, se creó un backup automático en:
  ```
  C:\ServitecManager\backups\SERVITEC_BACKUP_*.DB
  ```
- Copia ese archivo de vuelta a `servitec_manager\SERVITEC.DB`

---

## 📋 CHECKLIST DE ACTUALIZACIÓN

Antes de empezar:
- [ ] Pendrive conectado con todos los archivos
- [ ] ServitecManager cerrado en el otro PC
- [ ] Decidiste si quieres preservar datos del otro PC o usar los tuyos

Durante la actualización:
- [ ] Script ejecutado exitosamente
- [ ] Backup creado automáticamente
- [ ] Archivos copiados sin errores

Después de actualizar:
- [ ] ServitecManager abre correctamente
- [ ] Puedes crear una orden de prueba
- [ ] Tus datos están presentes
- [ ] Nuevas funcionalidades funcionan:
  - [ ] Gestión de proveedores mejorada
  - [ ] Importación de listas de precios
  - [ ] Campo de observaciones único en recepción
  - [ ] Limpieza automática de campos al generar orden

---

## 🎯 RESUMEN RÁPIDO

**¿Solo quieres actualizar el código del otro PC?**
→ Ejecuta `actualizar_desde_pendrive.py` y presiona ENTER

**¿Quieres llevar TUS datos al otro PC?**
→ Ejecuta `actualizar_desde_pendrive.py` primero  
→ Luego ejecuta `exportar_base_datos.py` y selecciona opción 2

**¿Tienes dudas?**
→ Lee el archivo `LEEME_IMPORTACION.txt` en la carpeta de base de datos

---

## 📞 SOPORTE

Si encuentras problemas:
1. Revisa la sección "Solución de Problemas" arriba
2. Verifica que el backup automático se haya creado
3. Contacta al administrador del sistema

---

**¡Listo para actualizar! 🚀**

El proceso es seguro y reversible gracias a los backups automáticos.
