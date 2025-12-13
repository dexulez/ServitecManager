"""
Script para crear ejecutable con PyInstaller
Más confiable que cx_Freeze para Windows
"""
import os
import subprocess
import sys
import shutil
from datetime import datetime

def crear_ejecutable():
    """Crea ejecutable standalone con PyInstaller"""
    
    print("=" * 70)
    print("CREANDO EJECUTABLE SERVITECMANAGER v1.1.0 CON PYINSTALLER")
    print("=" * 70)
    
    # 1. Limpiar compilaciones anteriores
    print("\n[1/5] Limpiando compilaciones anteriores...")
    for carpeta in ["build", "dist"]:
        if os.path.exists(carpeta):
            shutil.rmtree(carpeta)
            print(f"   ✓ Carpeta {carpeta} eliminada")
    
    # Eliminar spec si existe
    if os.path.exists("ServitecManager.spec"):
        os.remove("ServitecManager.spec")
        print("   ✓ Archivo .spec eliminado")
    
    # 2. Respaldar BD actual
    bd_actual = os.path.join("servitec_manager", "SERVITEC.DB")
    bd_backup = os.path.join("servitec_manager", "SERVITEC.DB.backup")
    
    print("\n[2/5] Gestionando base de datos...")
    if os.path.exists(bd_actual):
        shutil.copy2(bd_actual, bd_backup)
        os.remove(bd_actual)
        print(f"   ✓ BD respaldada y removida para instalación limpia")
    else:
        print("   ℹ No hay BD actual")
    
    # 3. Preparar comando PyInstaller
    print("\n[3/5] Configurando PyInstaller...")
    
    comando = [
        sys.executable, "-m", "PyInstaller",
        "--name=ServitecManager",
        "--onedir",  # Un directorio con todas las dependencias
        "--windowed",  # Sin consola
        "--icon=NONE",  # Sin icono por ahora
        "--add-data=servitec_manager/assets;assets",
        "--add-data=servitec_manager/version.json;.",
        "--hidden-import=customtkinter",
        "--hidden-import=PIL._tkinter_finder",
        "--hidden-import=babel.numbers",
        "--hidden-import=tkinter",
        "--hidden-import=sqlite3",
        "--collect-all=customtkinter",
        "--collect-all=tkcalendar",
        "--collect-all=PIL",
        "--collect-all=reportlab",
        "--collect-all=matplotlib",
        "--collect-all=pandas",
        "--collect-all=openpyxl",
        "--collect-all=pdfplumber",
        "--noconfirm",
        "servitec_manager/main.py"
    ]
    
    print("   ✓ Comando preparado")
    
    # 4. Ejecutar PyInstaller
    print("\n[4/5] Compilando con PyInstaller...")
    print("   ⏳ Esto puede tardar varios minutos...\n")
    
    try:
        resultado = subprocess.run(
            comando,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        # Mostrar últimas líneas de salida
        lineas = resultado.stdout.split('\n')
        for linea in lineas[-20:]:
            if linea.strip():
                print(f"   {linea}")
        
        if resultado.returncode != 0:
            print(f"\n❌ ERROR: Compilación falló con código {resultado.returncode}")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR durante compilación: {e}")
        return False
    
    # 5. Verificar ejecutable
    print("\n[5/5] Verificando ejecutable creado...")
    
    exe_path = os.path.join("dist", "ServitecManager", "ServitecManager.exe")
    
    if not os.path.exists(exe_path):
        print(f"   ✗ No se encontró el ejecutable en: {exe_path}")
        return False
    
    tamaño_mb = os.path.getsize(exe_path) / (1024 * 1024)
    print(f"   ✓ Ejecutable creado: {os.path.basename(exe_path)}")
    print(f"   ✓ Tamaño: {tamaño_mb:.2f} MB")
    
    # 6. Contar archivos en dist
    archivos_dist = []
    for root, dirs, files in os.walk("dist/ServitecManager"):
        archivos_dist.extend(files)
    
    print(f"   ✓ Total de archivos: {len(archivos_dist)}")
    
    # 7. Restaurar BD original
    print("\n[6/5] Restaurando base de datos original...")
    if os.path.exists(bd_backup):
        shutil.move(bd_backup, bd_actual)
        print(f"   ✓ BD restaurada")
    
    # Resumen final
    print("\n" + "=" * 70)
    print("✅ EJECUTABLE CREADO EXITOSAMENTE")
    print("=" * 70)
    print(f"\n📂 Carpeta: dist/ServitecManager/")
    print(f"📦 Ejecutable: ServitecManager.exe")
    print(f"📊 Tamaño: {tamaño_mb:.2f} MB")
    print(f"📁 Archivos totales: {len(archivos_dist)}")
    print(f"\n💡 Para probar:")
    print(f"   cd dist\\ServitecManager")
    print(f"   .\\ServitecManager.exe")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    try:
        exito = crear_ejecutable()
        sys.exit(0 if exito else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso cancelado por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
