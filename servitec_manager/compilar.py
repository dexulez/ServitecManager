"""
Script simplificado para compilar ServitecManager
"""
import subprocess
import sys
import os

print("=" * 70)
print("  COMPILANDO SERVITECMANAGER")
print("=" * 70)

# Comando de PyInstaller
comando = [
    sys.executable,
    "-m", "PyInstaller",
    "main.py",
    "--noconfirm",
    "--onefile",
    "--windowed",
    "--collect-all", "customtkinter",
    "--collect-all", "PIL",
    "--add-data", "assets;assets",
    "--name", "ServitecManager",
    "--clean"
]

print("\nEjecutando PyInstaller...")
print(" ".join(comando))
print()

# Ejecutar PyInstaller
resultado = subprocess.run(comando, capture_output=False)

if resultado.returncode == 0:
    print("\n" + "=" * 70)
    print("  ✓ COMPILACIÓN EXITOSA")
    print("=" * 70)
    print(f"\nEjecutable generado en: dist\\ServitecManager.exe")
    
    # Abrir carpeta dist
    if os.path.exists("dist"):
        os.startfile("dist")
else:
    print("\n" + "=" * 70)
    print("  ✗ ERROR EN LA COMPILACIÓN")
    print("=" * 70)
    sys.exit(1)
