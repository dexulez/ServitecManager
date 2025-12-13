# ServitecManager - Instalador

## Crear Instalador MSI para Windows

### Opción 1: Usar el script automático (RECOMENDADO)

1. Ejecuta el archivo `crear_instalador.bat`
2. Espera a que se complete el proceso
3. El instalador MSI se creará en la carpeta `dist\`

### Opción 2: Proceso manual

1. Instalar cx_Freeze:
```bash
pip install cx_Freeze
```

2. Instalar dependencias del proyecto:
```bash
pip install -r servitec_manager\requirements.txt
```

3. Crear el instalador:
```bash
python setup.py bdist_msi
```

### Resultado

El instalador MSI se creará en: `dist\ServitecManager-1.0.0-win64.msi`

### Instalación

1. Ejecuta el archivo .msi generado
2. Sigue el asistente de instalación
3. El programa se instalará en: `C:\Program Files\ServitecManager\`
4. Se creará un acceso directo en el menú Inicio

### Características del instalador

- ✅ Instalación en registro de Windows
- ✅ Acceso directo en menú Inicio
- ✅ Desinstalación desde Panel de Control
- ✅ Todas las dependencias incluidas
- ✅ Base de datos SQLite incluida
- ✅ Recursos y assets incluidos

### Notas

- El instalador requiere permisos de administrador
- La primera ejecución puede tardar unos segundos
- Los datos se guardan en la carpeta de instalación
- Para crear un icono personalizado, agrega un archivo .ico y modifica `setup.py`

### Actualizar versión

Para crear una nueva versión del instalador:

1. Modifica la versión en `setup.py` (línea 53)
2. Modifica la versión en `servitec_manager/version.json`
3. Ejecuta nuevamente `crear_instalador.bat`
