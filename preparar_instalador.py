"""
Script para preparar instalador con base de datos limpia
Crea una copia temporal sin la BD existente para instalación en otros equipos
"""
import os
import shutil
import subprocess
import sys

def preparar_instalador():
    """Prepara el entorno para crear instalador con BD limpia"""
    
    print("=" * 60)
    print("PREPARANDO INSTALADOR CON BASE DE DATOS LIMPIA")
    print("=" * 60)
    
    # 1. Verificar que no existan carpetas de compilación previas
    print("\n[1/5] Limpiando compilaciones anteriores...")
    if os.path.exists("build"):
        shutil.rmtree("build")
        print("   ✓ Carpeta 'build' eliminada")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
        print("   ✓ Carpeta 'dist' eliminada")
    
    # 2. Respaldar base de datos actual si existe
    bd_actual = os.path.join("servitec_manager", "SERVITEC.DB")
    bd_backup = os.path.join("servitec_manager", "SERVITEC.DB.backup")
    
    print("\n[2/5] Gestionando base de datos...")
    if os.path.exists(bd_actual):
        shutil.copy2(bd_actual, bd_backup)
        os.remove(bd_actual)
        print(f"   ✓ BD actual respaldada en: {bd_backup}")
        print(f"   ✓ BD eliminada para instalador limpio")
    else:
        print("   ℹ No hay BD actual (instalación limpia)")
    
    # 3. Verificar archivos necesarios
    print("\n[3/5] Verificando archivos necesarios...")
    archivos_requeridos = [
        "setup.py",
        "servitec_manager/main.py",
        "servitec_manager/database.py",
        "servitec_manager/logic.py",
        "servitec_manager/version.json",
    ]
    
    todos_ok = True
    for archivo in archivos_requeridos:
        if os.path.exists(archivo):
            print(f"   ✓ {archivo}")
        else:
            print(f"   ✗ FALTA: {archivo}")
            todos_ok = False
    
    if not todos_ok:
        print("\n❌ ERROR: Faltan archivos necesarios")
        return False
    
    # 4. Compilar instalador MSI
    print("\n[4/5] Compilando instalador MSI...")
    print("   ⏳ Esto puede tardar varios minutos...\n")
    
    try:
        # Ejecutar compilación con salida en tiempo real
        proceso = subprocess.Popen(
            [sys.executable, "setup.py", "bdist_msi"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Mostrar salida en tiempo real
        for linea in proceso.stdout:
            print(f"   {linea.rstrip()}")
        
        proceso.wait()
        
        if proceso.returncode != 0:
            print(f"\n❌ ERROR: Compilación falló con código {proceso.returncode}")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR durante compilación: {e}")
        return False
    
    # 5. Verificar que se creó el instalador
    print("\n[5/5] Verificando instalador creado...")
    
    if not os.path.exists("dist"):
        print("   ✗ No se creó la carpeta 'dist'")
        return False
    
    archivos_msi = [f for f in os.listdir("dist") if f.endswith(".msi")]
    
    if not archivos_msi:
        print("   ✗ No se encontró archivo MSI en carpeta dist")
        return False
    
    archivo_msi = archivos_msi[0]
    ruta_msi = os.path.join("dist", archivo_msi)
    tamaño_mb = os.path.getsize(ruta_msi) / (1024 * 1024)
    
    print(f"   ✓ Instalador creado: {archivo_msi}")
    print(f"   ✓ Tamaño: {tamaño_mb:.2f} MB")
    
    # Renombrar a nombre estándar
    nuevo_nombre = "ServitecManager-1.1.0-win64.msi"
    nueva_ruta = os.path.join("dist", nuevo_nombre)
    
    if archivo_msi != nuevo_nombre:
        shutil.move(ruta_msi, nueva_ruta)
        print(f"   ✓ Renombrado a: {nuevo_nombre}")
    
    # 6. Restaurar base de datos original
    print("\n[6/5] Restaurando base de datos original...")
    if os.path.exists(bd_backup):
        shutil.move(bd_backup, bd_actual)
        print(f"   ✓ BD restaurada desde backup")
    
    # Resumen final
    print("\n" + "=" * 60)
    print("✅ INSTALADOR CREADO EXITOSAMENTE")
    print("=" * 60)
    print(f"\n📦 Archivo: dist/{nuevo_nombre}")
    print(f"📊 Tamaño: {tamaño_mb:.2f} MB")
    print(f"\n💡 Características:")
    print(f"   • Base de datos limpia (se crea al instalar)")
    print(f"   • Usuario admin por defecto (contraseña: admin)")
    print(f"   • Acceso directo en escritorio y menú inicio")
    print(f"   • Instalación en: C:\\Program Files\\ServitecManager")
    print(f"\n✅ Listo para distribuir en otros computadores")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        exito = preparar_instalador()
        sys.exit(0 if exito else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso cancelado por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
