"""
Script para compilar el cargador de datos de prueba en un ejecutable
"""

import PyInstaller.__main__
import os

def build():
    """Compilar cargar_datos_prueba.py a ejecutable"""
    
    print("\n" + "="*60)
    print("  GENERANDO CARGADOR DE DATOS DE PRUEBA")
    print("="*60 + "\n")
    
    PyInstaller.__main__.run([
        'cargar_datos_prueba.py',
        '--name=CargarDatosPrueba',
        '--onefile',
        '--console',  # Con consola para ver los mensajes
        '--clean',
        '--noconfirm',
    ])
    
    print("\n" + "="*60)
    print("  ✓ COMPILACIÓN COMPLETADA")
    print("="*60)
    print(f"\nEl ejecutable está en: dist/CargarDatosPrueba.exe")
    print("Copie este archivo junto a ServitecManager.exe\n")

if __name__ == "__main__":
    build()
