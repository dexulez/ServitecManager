"""
Script para crear paquete portable de ServitecManager
Crea un ZIP con todo el ejecutable y dependencias listo para distribución
"""
import os
import shutil
import zipfile
from datetime import datetime

def crear_paquete_portable():
    """Crea paquete portable ZIP con ejecutable y recursos"""
    
    print("=" * 70)
    print("CREANDO PAQUETE PORTABLE SERVITECMANAGER v1.1.0")
    print("=" * 70)
    
    # Rutas
    build_dir = "build/exe.win-amd64-3.13"
    dist_dir = "dist_portable"
    zip_name = f"ServitecManager-1.1.0-Portable-win64_{datetime.now().strftime('%Y%m%d')}.zip"
    
    # 1. Verificar que existe el build
    if not os.path.exists(build_dir):
        print(f"\n❌ ERROR: No se encontró la carpeta de build: {build_dir}")
        print("   Ejecuta primero: python setup.py build")
        return False
    
    if not os.path.exists(f"{build_dir}/ServitecManager.exe"):
        print(f"\n❌ ERROR: No se encontró ServitecManager.exe en {build_dir}")
        return False
    
    print(f"\n[1/5] Preparando carpeta dist_portable...")
    
    # 2. Crear carpeta dist_portable
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir)
    print(f"   ✓ Carpeta {dist_dir} creada")
    
    # 3. Copiar todo el contenido del build
    print(f"\n[2/5] Copiando archivos del ejecutable...")
    app_dir = os.path.join(dist_dir, "ServitecManager")
    shutil.copytree(build_dir, app_dir)
    print(f"   ✓ {len(os.listdir(app_dir))} archivos copiados")
    
    # 4. Crear README.txt
    print(f"\n[3/5] Creando documentación...")
    readme_content = """
╔══════════════════════════════════════════════════════════════════╗
║           SERVITECMANAGER v1.1.0 - PORTABLE EDITION             ║
║          Sistema de Gestión de Servicios Técnicos                ║
╚══════════════════════════════════════════════════════════════════╝

📦 INSTALACIÓN PORTABLE
───────────────────────────────────────────────────────────────────

1. Extraer todo el contenido del ZIP en cualquier carpeta
2. Ejecutar ServitecManager.exe
3. ¡Listo! No requiere instalación en el sistema

⚙️  CARACTERÍSTICAS DE ESTA VERSIÓN
───────────────────────────────────────────────────────────────────

✅ Base de datos limpia (primera ejecución crea BD automáticamente)
✅ Usuario administrador por defecto:
   👤 Usuario: admin
   🔑 Contraseña: admin

✅ Todas las dependencias incluidas (no requiere Python instalado)
✅ Completamente portable (lleva en USB, ejecuta en cualquier PC)

🆕 NOVEDADES v1.1.0
───────────────────────────────────────────────────────────────────

• Sistema de notificaciones al cliente por WhatsApp y Email
• Notificación automática al cambiar estado en Taller y Dashboard
• Campo de notas adicionales en notificaciones
• Sistema de pedidos a proveedores completamente integrado
• Registro automático de compras al recibir mercancía
• Campo de notas en recepción de pedidos
• Botón de búsqueda de items en agregar pedidos
• Actualización automática de datos al cambiar pestañas
• Menú reorganizado con submenús colapsables exclusivos
• Corrección de estados: ESPERA DE REPUESTO
• Actualización inmediata de badges de estado en Dashboard
• Mejoras visuales en sidebar y fuentes de submenús

📋 REQUISITOS DEL SISTEMA
───────────────────────────────────────────────────────────────────

• Windows 10 o superior (64-bit)
• 4 GB RAM mínimo
• 500 MB espacio en disco
• Resolución mínima: 1366x768

💾 DATOS Y BACKUPS
───────────────────────────────────────────────────────────────────

La base de datos se crea automáticamente en:
   ServitecManager/SERVITEC.DB

Los reportes se guardan en:
   ServitecManager/reports/

Los backups automáticos en:
   ServitecManager/backups/

📞 SOPORTE
───────────────────────────────────────────────────────────────────

Para soporte técnico o consultas, contactar al administrador
del sistema.

═══════════════════════════════════════════════════════════════════
      © 2025 ServitecManager - Todos los derechos reservados
═══════════════════════════════════════════════════════════════════
"""
    
    with open(os.path.join(dist_dir, "LEEME.txt"), "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("   ✓ Archivo LEEME.txt creado")
    
    # 5. Crear acceso directo (script .bat)
    print(f"\n[4/5] Creando acceso directo...")
    bat_content = '''@echo off
cd /d "%~dp0ServitecManager"
start "" "ServitecManager.exe"
'''
    with open(os.path.join(dist_dir, "Ejecutar ServitecManager.bat"), "w") as f:
        f.write(bat_content)
    print("   ✓ Archivo Ejecutar ServitecManager.bat creado")
    
    # 6. Crear ZIP
    print(f"\n[5/5] Creando archivo ZIP...")
    
    if not os.path.exists("dist"):
        os.makedirs("dist")
    
    zip_path = os.path.join("dist", zip_name)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
        for root, dirs, files in os.walk(dist_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, dist_dir)
                zipf.write(file_path, arcname)
                
    # Calcular tamaño
    tamaño_mb = os.path.getsize(zip_path) / (1024 * 1024)
    
    print(f"   ✓ Archivo comprimido creado")
    
    # 7. Limpiar carpeta temporal
    shutil.rmtree(dist_dir)
    
    # Resumen final
    print("\n" + "=" * 70)
    print("✅ PAQUETE PORTABLE CREADO EXITOSAMENTE")
    print("=" * 70)
    print(f"\n📦 Archivo: dist/{zip_name}")
    print(f"📊 Tamaño: {tamaño_mb:.2f} MB")
    print(f"\n💡 Contenido del paquete:")
    print(f"   • ServitecManager.exe (ejecutable principal)")
    print(f"   • lib/ (bibliotecas y dependencias)")
    print(f"   • assets/ (recursos gráficos)")
    print(f"   • LEEME.txt (instrucciones)")
    print(f"   • Ejecutar ServitecManager.bat (acceso directo)")
    print(f"\n🚀 LISTO PARA DISTRIBUIR")
    print(f"   • Extrae el ZIP en cualquier carpeta")
    print(f"   • Ejecuta 'Ejecutar ServitecManager.bat'")
    print(f"   • Usuario: admin / Contraseña: admin")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    try:
        exito = crear_paquete_portable()
        if exito:
            print("\n✓ Proceso completado con éxito")
        else:
            print("\n✗ Proceso falló")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
