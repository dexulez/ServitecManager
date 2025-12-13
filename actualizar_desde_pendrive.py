"""
Script de actualización para ServitecManager
Actualiza código sin modificar la base de datos existente
Para usar con pendrive en otro computador
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

def crear_backup_bd(destino):
    """Crear backup de la base de datos antes de actualizar"""
    bd_origen = Path(destino) / "servitec_manager" / "SERVITEC.DB"
    
    if bd_origen.exists():
        backup_dir = Path(destino) / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"SERVITEC_BACKUP_{timestamp}.DB"
        
        print(f"📦 Creando backup de base de datos...")
        shutil.copy2(bd_origen, backup_path)
        print(f"✅ Backup guardado en: {backup_path}")
        return True
    else:
        print("⚠️  No se encontró base de datos existente (primera instalación)")
        return False

def actualizar_codigo(origen, destino):
    """Actualizar archivos de código preservando la base de datos"""
    print("\n🔄 INICIANDO ACTUALIZACIÓN DE SERVITECMANAGER")
    print("=" * 60)
    
    origen_path = Path(origen)
    destino_path = Path(destino)
    
    # Verificar que la carpeta de origen existe
    if not origen_path.exists():
        print(f"❌ ERROR: No se encuentra la carpeta de origen: {origen}")
        return False
    
    # Crear carpeta de destino si no existe
    destino_path.mkdir(parents=True, exist_ok=True)
    
    # Crear backup de la base de datos
    crear_backup_bd(destino)
    
    # Guardar la base de datos existente temporalmente
    bd_destino = destino_path / "servitec_manager" / "SERVITEC.DB"
    bd_temp = None
    
    if bd_destino.exists():
        bd_temp = destino_path / "SERVITEC_TEMP.DB"
        print(f"\n💾 Preservando base de datos existente...")
        shutil.copy2(bd_destino, bd_temp)
    
    # Archivos y carpetas a excluir de la copia
    excluir = {
        '__pycache__',
        '.git',
        '.venv',
        'venv',
        'build',
        'dist',
        '*.pyc',
        '*.pyo',
        '*.egg-info',
        'SERVITEC.DB',  # No sobrescribir la BD
        'SERVITEC_TEMP.DB',
        'backups',  # Preservar backups
        'ordenes',  # Preservar órdenes generadas
        'reports',  # Preservar reportes
        'updates',  # Carpeta de actualizaciones
        'notificaciones.db.json'  # Preservar notificaciones
    }
    
    print(f"\n📁 Copiando archivos desde: {origen}")
    print(f"📁 Hacia: {destino}")
    print("\n⏳ Actualizando archivos...")
    
    archivos_copiados = 0
    carpetas_copiadas = 0
    
    # Copiar estructura principal
    for item in origen_path.rglob('*'):
        # Calcular ruta relativa
        rel_path = item.relative_to(origen_path)
        
        # Verificar si debe excluirse
        debe_excluir = False
        for patron in excluir:
            if patron in str(rel_path).split(os.sep):
                debe_excluir = True
                break
            if patron.startswith('*') and str(rel_path).endswith(patron[1:]):
                debe_excluir = True
                break
        
        if debe_excluir:
            continue
        
        destino_item = destino_path / rel_path
        
        try:
            if item.is_dir():
                destino_item.mkdir(parents=True, exist_ok=True)
                carpetas_copiadas += 1
            else:
                destino_item.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, destino_item)
                archivos_copiados += 1
                
                if archivos_copiados % 50 == 0:
                    print(f"  📄 {archivos_copiados} archivos copiados...")
        except Exception as e:
            print(f"⚠️  Error copiando {rel_path}: {e}")
    
    # Restaurar base de datos preservada
    if bd_temp and bd_temp.exists():
        print(f"\n♻️  Restaurando base de datos original...")
        shutil.copy2(bd_temp, bd_destino)
        bd_temp.unlink()  # Eliminar archivo temporal
        print("✅ Base de datos preservada correctamente")
    
    print(f"\n✅ ACTUALIZACIÓN COMPLETADA")
    print(f"   📁 {carpetas_copiadas} carpetas procesadas")
    print(f"   📄 {archivos_copiados} archivos actualizados")
    print(f"\n💡 IMPORTANTE:")
    print(f"   - Tu base de datos NO fue modificada")
    print(f"   - Se creó un backup en: {destino_path / 'backups'}")
    print(f"   - Todas tus órdenes y reportes se mantienen intactos")
    
    return True

def main():
    print("\n" + "=" * 60)
    print("  📦 ACTUALIZADOR DE SERVITECMANAGER - VERSIÓN PENDRIVE")
    print("=" * 60)
    print("\nEste script actualizará ServitecManager preservando tu base de datos\n")
    
    # Detectar si estamos en el pendrive
    script_dir = Path(__file__).parent
    
    print(f"📍 Ubicación del script: {script_dir}")
    
    # Pedir destino de instalación
    print("\n" + "-" * 60)
    destino_default = "C:\\ServitecManager"
    
    print(f"\n¿Dónde está instalado ServitecManager en este PC?")
    print(f"Presiona ENTER para usar: {destino_default}")
    destino_input = input("Ruta de instalación: ").strip()
    
    destino = destino_input if destino_input else destino_default
    
    # Confirmar actualización
    print("\n" + "-" * 60)
    print(f"ORIGEN (Pendrive):  {script_dir}")
    print(f"DESTINO (PC):       {destino}")
    print("-" * 60)
    
    confirmar = input("\n¿Desea continuar con la actualización? (S/N): ").strip().upper()
    
    if confirmar != 'S':
        print("\n❌ Actualización cancelada por el usuario")
        return
    
    # Ejecutar actualización
    if actualizar_codigo(script_dir, destino):
        print("\n" + "=" * 60)
        print("  ✅ ACTUALIZACIÓN EXITOSA")
        print("=" * 60)
        print("\n📋 PRÓXIMOS PASOS:")
        print("   1. Verificar que todos los archivos se copiaron correctamente")
        print("   2. Ejecutar ServitecManager normalmente")
        print("   3. Verificar que todo funciona correctamente")
        print(f"\n💾 Ruta de instalación: {destino}")
    else:
        print("\n❌ La actualización falló. Revisa los mensajes de error arriba.")
    
    print("\n" + "=" * 60)
    input("\nPresiona ENTER para cerrar...")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        input("\nPresiona ENTER para cerrar...")
