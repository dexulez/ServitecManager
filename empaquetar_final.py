"""
Script para crear paquete portable final con PyInstaller
"""
import os
import shutil
import zipfile
from datetime import datetime

def crear_paquete_final():
    """Crea paquete portable ZIP listo para distribución"""
    
    print("=" * 70)
    print("CREANDO PAQUETE PORTABLE FINAL v1.1.0")
    print("=" * 70)
    
    # 1. Verificar ejecutable
    if not os.path.exists("dist/ServitecManager/ServitecManager.exe"):
        print("\n❌ ERROR: No se encontró el ejecutable")
        print("   Ejecuta primero: python crear_ejecutable.py")
        return False
    
    print("\n[1/4] Verificando archivos...")
    
    # Contar archivos
    archivos = []
    for root, dirs, files in os.walk("dist/ServitecManager"):
        archivos.extend(files)
    
    tamaño_exe = os.path.getsize("dist/ServitecManager/ServitecManager.exe") / (1024 * 1024)
    print(f"   ✓ Ejecutable: {tamaño_exe:.2f} MB")
    print(f"   ✓ Total archivos: {len(archivos)}")
    
    # 2. Crear documentación
    print("\n[2/4] Creando documentación...")
    
    readme = """
╔══════════════════════════════════════════════════════════════════╗
║           SERVITECMANAGER v1.1.0 - PORTABLE EDITION             ║
║          Sistema de Gestión de Servicios Técnicos                ║
╚══════════════════════════════════════════════════════════════════╝

📦 INSTALACIÓN RÁPIDA
───────────────────────────────────────────────────────────────────

1. Extraer TODO el contenido del ZIP en una carpeta
2. Doble clic en "EJECUTAR SERVITECMANAGER.bat"
3. Login: admin / admin

⚙️  CARACTERÍSTICAS
───────────────────────────────────────────────────────────────────

✅ Base de datos limpia (se crea automáticamente)
✅ No requiere Python instalado
✅ Completamente portable
✅ Usuario admin configurado por defecto

🆕 NOVEDADES v1.1.0
───────────────────────────────────────────────────────────────────

• Sistema de notificaciones WhatsApp y Email
• Gestión completa de pedidos a proveedores
• Registro automático de compras
• Actualización automática de datos
• Menú reorganizado y mejorado
• Ventanas emergentes ajustadas correctamente

💻 REQUISITOS
───────────────────────────────────────────────────────────────────

• Windows 10+ (64-bit)
• 4 GB RAM mínimo
• 500 MB espacio en disco

📞 PRIMER USO
───────────────────────────────────────────────────────────────────

Usuario: admin
Contraseña: admin

⚠️  IMPORTANTE: Cambiar contraseña después del primer login

═══════════════════════════════════════════════════════════════════
"""
    
    with open("dist/ServitecManager/LEEME.txt", "w", encoding="utf-8") as f:
        f.write(readme)
    print("   ✓ LEEME.txt creado")
    
    # 3. Crear launcher
    print("\n[3/4] Creando launcher...")
    
    launcher = """@echo off
title ServitecManager v1.1.0
cd /d "%~dp0"
echo.
echo ===============================================
echo   INICIANDO SERVITECMANAGER v1.1.0
echo ===============================================
echo.
echo Cargando aplicacion...
echo.
start "" "ServitecManager.exe"
timeout /t 2 /nobreak >nul
exit
"""
    
    with open("dist/ServitecManager/EJECUTAR SERVITECMANAGER.bat", "w", encoding="utf-8") as f:
        f.write(launcher)
    print("   ✓ Launcher BAT creado")
    
    # 4. Crear ZIP
    print("\n[4/4] Creando archivo ZIP...")
    
    zip_name = f"ServitecManager-1.1.0-Portable-win64_{datetime.now().strftime('%Y%m%d')}.zip"
    zip_path = f"dist/{zip_name}"
    
    # Eliminar ZIP anterior si existe
    if os.path.exists(zip_path):
        os.remove(zip_path)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
        contador = 0
        for root, dirs, files in os.walk("dist/ServitecManager"):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.join("ServitecManager", os.path.relpath(file_path, "dist/ServitecManager"))
                zipf.write(file_path, arcname)
                contador += 1
                if contador % 100 == 0:
                    print(f"   Comprimiendo... {contador} archivos")
    
    tamaño_zip_mb = os.path.getsize(zip_path) / (1024 * 1024)
    
    print(f"   ✓ Comprimido: {contador} archivos")
    
    # Resumen final
    print("\n" + "=" * 70)
    print("✅ PAQUETE PORTABLE CREADO EXITOSAMENTE")
    print("=" * 70)
    print(f"\n📦 Archivo: {zip_name}")
    print(f"📊 Tamaño: {tamaño_zip_mb:.2f} MB")
    print(f"📂 Ubicación: dist/{zip_name}")
    print(f"\n🚀 LISTO PARA DISTRIBUIR")
    print(f"\n💡 Instrucciones para usuario final:")
    print(f"   1. Extraer el ZIP completo")
    print(f"   2. Ejecutar 'EJECUTAR SERVITECMANAGER.bat'")
    print(f"   3. Login: admin / admin")
    print(f"\n✅ Base de datos comienza LIMPIA")
    print(f"✅ Se crea automáticamente al primer uso")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    try:
        exito = crear_paquete_final()
        if exito:
            print("\n✓ Proceso completado")
        else:
            print("\n✗ Proceso falló")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
