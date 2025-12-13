# SERVITEC MANAGER

## 📋 Descripción
Sistema de gestión integral para taller de reparación de electrónica. Incluye módulos de recepción, taller, administración, inventario, reportes y gestión de proveedores.

## 🏗️ Arquitectura

### Backend
- **Database**: `database.py` - GESTOR_BASE_DATOS (SQLite con SQL 100% MAYÚSCULA)
- **Logic**: `logic.py` - 10 gestores en MAYÚSCULA (GESTOR_CLIENTES, GESTOR_ORDENES, GESTOR_PROVEEDORES, etc.)
- **Main**: `main.py` - Punto de entrada (PRINCIPAL(), GESTOR_LOGICA, APLICACION)

### Frontend
- **Framework**: CustomTkinter (Python 3.13)
- **App**: `ui/app.py` - APLICACION (ventana principal)
- **Módulos UI**: 
  - `reception.py` - Ingreso de órdenes
  - `workshop.py` - Gestión de técnicos y órdenes
  - `admin.py` - Gestión de personal
  - `inventory.py` - Gestión de inventario
  - `providers_ui.py` - Gestión de proveedores ⭐ (Refactorizado v2.0.0)
  - `dashboard.py` - Panel de control
  - `history.py` - Historial
  - `reports.py` - Reportes
  - `cash.py` - Gestión de caja
  - `pos.py` - Punto de venta
  - `login.py` - Autenticación

## 🎯 Estándares de Código

### Nomenclatura
- **Clases**: PascalCase MAYÚSCULA (GESTOR_CLIENTES, APLICACION)
- **Métodos**: MAYÚSCULA_CON_GUIONES en documentación, snake_case en código
- **SQL**: 100% MAYÚSCULA (SELECT, INSERT, UPDATE, DELETE)
- **Constantes**: MAYÚSCULAS (MODO_APARIENCIA, TEMA_COLOR_DEFECTO)
- **UI Textos**: 100% MAYÚSCULAS (v2.0.0+)
- **Parámetros**: snake_case con nombres en español

### Sin acentos en identificadores
- GESTOR_LOGICA (no LÓGICA)
- TECNICO (no TÉCNICO)
- DEBITO (no DÉBITO)
- CREDITO (no CRÉDITO)
- ENVIO (no ENVÍO)

### UI en MAYÚSCULAS (v2.0.0+)
- Labels: "GESTIÓN DE PROVEEDORES"
- Placeholders: "NOMBRE EMPRESA", "TELÉFONO"
- Botones: "GUARDAR PROVEEDOR", "ACTUALIZAR LISTA"
- Encabezados: "NOMBRE", "TELÉFONO", "EMAIL"

## 🚀 Instalación

### Requisitos
- Python 3.13+
- Windows 10/11

### Setup
```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
python servitec_manager/main.py
```

### Credenciales por defecto
- Usuario: `ADMIN`
- Contraseña: `admin123`
- O: `TECNICO1` / `1234`

## 📦 Dependencias
- customtkinter (GUI)
- pandas (Excel)
- openpyxl (Excel avanzado)
- pdfplumber (lectura PDF)
- reportlab (generación PDF)
- matplotlib (gráficos)
- Pillow (imágenes)

## 📁 Estructura

```
ServitecManager/
├── .gitignore
├── CHANGELOG.md
├── README.md
├── requirements.txt
├── .versions/
│   └── v2.0.0.json
├── ordenes/              # Órdenes generadas
├── servitec_manager/
│   ├── main.py
│   ├── database.py
│   ├── logic.py
│   ├── pdf_generator.py
│   ├── importer.py
│   ├── requirements.txt
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── login.py
│   │   ├── reception.py
│   │   ├── workshop.py
│   │   ├── admin.py
│   │   ├── inventory.py
│   │   ├── providers_ui.py
│   │   ├── dashboard.py
│   │   ├── history.py
│   │   ├── reports.py
│   │   ├── cash.py
│   │   ├── pos.py
│   │   └── import_dialog.py
│   └── __pycache__/
```

## 🔄 Versionado

### Versión Actual: 2.0.0 (2025-11-27)
- Refactorización completa de UI a MAYÚSCULAS
- Todos los módulos UI con textos en MAYÚSCULAS
- 48 cambios totales aplicados

Ver `CHANGELOG.md` para historial completo.

## 🤝 Contribuciones

### Proceso de cambios
1. Hacer cambios en archivos
2. Probar funcionalidad
3. Documentar en CHANGELOG.md
4. Actualizar versionado en `.versions/`
5. Confirmar que tests pasen

## 📞 Soporte

Para reportar problemas o sugerencias, por favor contactar al equipo de desarrollo.

---

**Última actualización**: 2025-11-27  
**Versión**: 2.0.0  
**Estado**: Producción ✓
