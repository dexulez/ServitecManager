# Instalador de ServitecManager

## Instrucciones para generar el ejecutable

### 1. Instalar dependencias
```powershell
pip install -r requirements.txt
```

### 2. Generar el ejecutable
```powershell
python setup.py
```

### 3. Resultado
El ejecutable se generará en la carpeta `dist/ServitecManager.exe`

## Contenido del paquete

- **ServitecManager.exe**: Ejecutable independiente (no requiere Python instalado)
- **assets/**: Recursos incluidos (logos, imágenes)
- **Base de datos**: Se crea automáticamente al primer uso

## Distribución

El archivo `ServitecManager.exe` es completamente portable:
- Tamaño: ~100-150 MB
- No requiere instalación
- Incluye Python y todas las dependencias
- Crea automáticamente la estructura de carpetas necesaria

## Actualizaciones

Para crear un paquete de actualización:
1. Modificar solo los archivos necesarios
2. Versionar los cambios
3. Distribuir solo los archivos modificados
4. Mantener compatibilidad con la base de datos existente

## Notas

- El ejecutable incluye todas las librerías necesarias
- Se recomienda ejecutar como administrador en el primer uso
- Los datos se guardan en la misma carpeta del ejecutable
