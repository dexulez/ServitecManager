"""
Script para generar plantillas de Excel para importar datos a ServitecManager
"""

import pandas as pd
from datetime import datetime
import os

def crear_plantilla_repuestos():
    """Crear plantilla Excel para importar repuestos"""
    
    # Datos de ejemplo
    data = {
        'nombre': [
            'Pantalla Samsung A54',
            'Batería iPhone 13',
            'Cargador USB-C 20W'
        ],
        'categoria': [
            'PANTALLA',
            'BATERIA',
            'ACCESORIO'
        ],
        'precio_venta': [
            45000,
            28000,
            8500
        ],
        'stock_actual': [
            15,
            20,
            50
        ],
        'stock_minimo': [
            5,
            5,
            10
        ]
    }
    
    df = pd.DataFrame(data)
    filename = 'PLANTILLA_REPUESTOS.xlsx'
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Repuestos', index=False)
        
        # Crear hoja de instrucciones
        instrucciones = pd.DataFrame({
            'INSTRUCCIONES': [
                '1. Complete los datos de los repuestos en la hoja "Repuestos"',
                '2. Campos obligatorios: nombre, categoria, precio_venta',
                '3. Categorías válidas: PANTALLA, BATERIA, ACCESORIO, CAMARA, OTRO',
                '4. Los precios deben ser números sin puntos ni comas',
                '5. Stock actual y stock mínimo son opcionales (se pondrán en 0)',
                '6. Guarde el archivo y use la opción Importar en el sistema',
                '',
                'IMPORTANTE:',
                '- No modifique los nombres de las columnas',
                '- Elimine las filas de ejemplo antes de importar sus datos',
                '- Un repuesto por fila',
                '- Máximo 1000 repuestos por archivo'
            ]
        })
        instrucciones.to_excel(writer, sheet_name='Instrucciones', index=False)
    
    print(f"✓ Creada plantilla: {filename}")
    return filename

def crear_plantilla_productos():
    """Crear plantilla Excel para importar productos"""
    
    # Datos de ejemplo
    data = {
        'nombre': [
            'Funda Silicona Universal',
            'Vidrio Templado 9H',
            'Cable Lightning 1m'
        ],
        'categoria': [
            'ACCESORIO',
            'PROTECCION',
            'CABLE'
        ],
        'precio_venta': [
            3500,
            2500,
            5000
        ],
        'stock_actual': [
            100,
            120,
            80
        ],
        'stock_minimo': [
            20,
            25,
            15
        ],
        'codigo_barra': [
            '7501234567890',
            '7501234567891',
            '7501234567892'
        ]
    }
    
    df = pd.DataFrame(data)
    filename = 'PLANTILLA_PRODUCTOS.xlsx'
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Productos', index=False)
        
        # Crear hoja de instrucciones
        instrucciones = pd.DataFrame({
            'INSTRUCCIONES': [
                '1. Complete los datos de los productos en la hoja "Productos"',
                '2. Campos obligatorios: nombre, categoria, precio_venta',
                '3. Categorías válidas: ACCESORIO, PROTECCION, CABLE, CARGADOR, AUDIO, OTRO',
                '4. Los precios deben ser números sin puntos ni comas',
                '5. Stock actual y stock mínimo son opcionales (se pondrán en 0)',
                '6. El código de barras es opcional',
                '7. Guarde el archivo y use la opción Importar en el sistema',
                '',
                'IMPORTANTE:',
                '- No modifique los nombres de las columnas',
                '- Elimine las filas de ejemplo antes de importar sus datos',
                '- Un producto por fila',
                '- Máximo 1000 productos por archivo'
            ]
        })
        instrucciones.to_excel(writer, sheet_name='Instrucciones', index=False)
    
    print(f"✓ Creada plantilla: {filename}")
    return filename

def crear_plantilla_servicios():
    """Crear plantilla Excel para importar servicios predefinidos"""
    
    # Datos de ejemplo
    data = {
        'nombre': [
            'Cambio de Pantalla',
            'Reemplazo de Batería',
            'Limpieza Interna',
            'Actualización de Software'
        ],
        'descripcion': [
            'Cambio completo de pantalla LCD + táctil',
            'Reemplazo de batería original',
            'Limpieza interna de placa y componentes',
            'Actualización del sistema operativo'
        ],
        'precio_base': [
            35000,
            25000,
            15000,
            10000
        ],
        'tiempo_estimado_minutos': [
            60,
            45,
            30,
            20
        ],
        'categoria': [
            'REPARACION',
            'REPARACION',
            'MANTENIMIENTO',
            'SOFTWARE'
        ]
    }
    
    df = pd.DataFrame(data)
    filename = 'PLANTILLA_SERVICIOS.xlsx'
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Servicios', index=False)
        
        # Crear hoja de instrucciones
        instrucciones = pd.DataFrame({
            'INSTRUCCIONES': [
                '1. Complete los datos de los servicios en la hoja "Servicios"',
                '2. Campos obligatorios: nombre, precio_base',
                '3. Categorías válidas: REPARACION, MANTENIMIENTO, SOFTWARE, DIAGNOSTICO, OTRO',
                '4. Los precios deben ser números sin puntos ni comas',
                '5. El tiempo estimado es en minutos (opcional)',
                '6. La descripción es opcional pero recomendada',
                '7. Guarde el archivo y use la opción Importar en el sistema',
                '',
                'IMPORTANTE:',
                '- No modifique los nombres de las columnas',
                '- Elimine las filas de ejemplo antes de importar sus datos',
                '- Un servicio por fila',
                '- Máximo 500 servicios por archivo'
            ]
        })
        instrucciones.to_excel(writer, sheet_name='Instrucciones', index=False)
    
    print(f"✓ Creada plantilla: {filename}")
    return filename

def crear_todas_plantillas():
    """Crear todas las plantillas de una vez"""
    print("\n" + "="*60)
    print("  GENERADOR DE PLANTILLAS EXCEL - SERVITECMANAGER")
    print("="*60 + "\n")
    
    archivos_creados = []
    
    try:
        archivos_creados.append(crear_plantilla_repuestos())
        archivos_creados.append(crear_plantilla_productos())
        archivos_creados.append(crear_plantilla_servicios())
        
        print("\n" + "="*60)
        print("  ✓ PLANTILLAS CREADAS EXITOSAMENTE")
        print("="*60 + "\n")
        
        print("Archivos generados:")
        for archivo in archivos_creados:
            print(f"  • {archivo}")
        
        print("\nPuede abrir estos archivos con Excel, completar los datos")
        print("y luego importarlos desde el sistema ServitecManager.\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")

if __name__ == "__main__":
    crear_todas_plantillas()
    input("Presione ENTER para cerrar...")
