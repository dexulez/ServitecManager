"""
Script para exportar/importar base de datos de ServitecManager
Crea un backup completo que se puede transferir entre computadores
"""

import os
import sys
import shutil
import sqlite3
from pathlib import Path
from datetime import datetime
import json

def exportar_base_datos():
    """Exportar base de datos con información detallada"""
    print("\n" + "=" * 60)
    print("  📦 EXPORTADOR DE BASE DE DATOS - SERVITECMANAGER")
    print("=" * 60)
    
    # Ubicación de la base de datos
    bd_origen = Path("servitec_manager/SERVITEC.DB")
    
    if not bd_origen.exists():
        print(f"\n❌ ERROR: No se encontró la base de datos en: {bd_origen}")
        input("Presiona ENTER para cerrar...")
        return False
    
    # Crear carpeta de exportación
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_dir = Path(f"BASE_DATOS_EXPORT_{timestamp}")
    export_dir.mkdir(exist_ok=True)
    
    print(f"\n📁 Carpeta de exportación: {export_dir}")
    
    # 1. Copiar base de datos
    print("\n📋 Paso 1/4: Copiando base de datos...")
    bd_destino = export_dir / "SERVITEC.DB"
    shutil.copy2(bd_origen, bd_destino)
    print(f"✅ Base de datos copiada: {bd_destino}")
    
    # 2. Obtener información de la BD
    print("\n📊 Paso 2/4: Extrayendo información de la base de datos...")
    try:
        conn = sqlite3.connect(bd_origen)
        cursor = conn.cursor()
        
        info = {
            "fecha_exportacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.1.0",
            "estadisticas": {}
        }
        
        # Obtener estadísticas de cada tabla
        tablas = [
            "clientes", "ordenes", "inventario", "repuestos", 
            "servicios", "proveedores", "tecnicos", "marcas", "modelos"
        ]
        
        for tabla in tablas:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                count = cursor.fetchone()[0]
                info["estadisticas"][tabla] = count
                print(f"   📌 {tabla}: {count} registros")
            except:
                info["estadisticas"][tabla] = 0
        
        conn.close()
        
        # Guardar información
        with open(export_dir / "INFO_BASE_DATOS.json", "w", encoding="utf-8") as f:
            json.dump(info, f, indent=2, ensure_ascii=False)
        
        print("✅ Información extraída correctamente")
        
    except Exception as e:
        print(f"⚠️  Advertencia al extraer información: {e}")
    
    # 3. Copiar archivos adicionales importantes
    print("\n📁 Paso 3/4: Copiando archivos adicionales...")
    archivos_importantes = [
        "servitec_manager/notificaciones.db.json",
        "servitec_manager/version.json"
    ]
    
    for archivo in archivos_importantes:
        origen = Path(archivo)
        if origen.exists():
            destino = export_dir / origen.name
            shutil.copy2(origen, destino)
            print(f"   ✅ {origen.name}")
    
    # 4. Crear README con instrucciones
    print("\n📝 Paso 4/4: Creando instrucciones de importación...")
    
    readme_content = f"""
═══════════════════════════════════════════════════════════════
  BACKUP DE BASE DE DATOS - SERVITECMANAGER
═══════════════════════════════════════════════════════════════

📅 Fecha de exportación: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
📊 Versión: 1.1.0

CONTENIDO DE ESTE BACKUP:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• SERVITEC.DB - Base de datos completa
• INFO_BASE_DATOS.json - Estadísticas de la exportación
• notificaciones.db.json - Notificaciones del sistema (si existe)
• version.json - Información de versión (si existe)

ESTADÍSTICAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
    
    # Agregar estadísticas si están disponibles
    if 'info' in locals():
        for tabla, count in info["estadisticas"].items():
            readme_content += f"   {tabla.upper():20} {count:>6} registros\n"
    
    readme_content += """

INSTRUCCIONES PARA IMPORTAR EN OTRO COMPUTADOR:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OPCIÓN 1: Importación Manual
────────────────────────────

1. En el otro computador, cierra ServitecManager si está abierto

2. Navega a la carpeta de instalación:
   C:\\ServitecManager\\servitec_manager
   
3. CREA UN BACKUP de tu base de datos actual (si existe):
   - Copia SERVITEC.DB a un lugar seguro
   
4. Copia SERVITEC.DB de este backup a:
   C:\\ServitecManager\\servitec_manager\\SERVITEC.DB
   
5. (Opcional) Copia notificaciones.db.json a:
   C:\\ServitecManager\\servitec_manager\\notificaciones.db.json

6. Abre ServitecManager normalmente


OPCIÓN 2: Script Automático
───────────────────────────

1. Ejecuta: python importar_base_datos.py
   (si existe en este backup)

2. Sigue las instrucciones en pantalla


⚠️  IMPORTANTE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Este backup REEMPLAZARÁ completamente la base de datos destino
• SIEMPRE crea un backup antes de importar
• Verifica que ServitecManager esté cerrado antes de copiar
• Si tienes problemas, contacta al soporte técnico


═══════════════════════════════════════════════════════════════
  Para más información: github.com/servitec
═══════════════════════════════════════════════════════════════
"""
    
    with open(export_dir / "LEEME_IMPORTACION.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("✅ Instrucciones creadas")
    
    # Resumen final
    print("\n" + "=" * 60)
    print("  ✅ EXPORTACIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 60)
    print(f"\n📁 Carpeta creada: {export_dir.absolute()}")
    print(f"💾 Tamaño de BD: {bd_destino.stat().st_size / 1024:.2f} KB")
    print("\n📋 CONTENIDO:")
    for item in export_dir.iterdir():
        print(f"   • {item.name}")
    
    print("\n💡 PRÓXIMOS PASOS:")
    print("   1. Copia toda la carpeta a un pendrive")
    print("   2. En el otro PC, sigue las instrucciones del archivo LEEME_IMPORTACION.txt")
    print("   3. O ejecuta el script de importación incluido")
    
    return True

def importar_base_datos():
    """Importar base de datos desde un backup"""
    print("\n" + "=" * 60)
    print("  📥 IMPORTADOR DE BASE DE DATOS - SERVITECMANAGER")
    print("=" * 60)
    
    # Buscar archivo SERVITEC.DB en el directorio actual
    bd_backup = None
    for archivo in Path(".").glob("*.DB"):
        if "SERVITEC" in archivo.name.upper():
            bd_backup = archivo
            break
    
    if not bd_backup:
        print("\n❌ No se encontró ningún archivo SERVITEC.DB en esta carpeta")
        ruta_manual = input("\nIngresa la ruta completa del archivo .DB: ").strip()
        if ruta_manual:
            bd_backup = Path(ruta_manual)
    
    if not bd_backup or not bd_backup.exists():
        print("\n❌ ERROR: No se pudo encontrar el archivo de base de datos")
        input("Presiona ENTER para cerrar...")
        return False
    
    print(f"\n📁 Base de datos encontrada: {bd_backup}")
    
    # Determinar destino
    destino_default = Path("C:/ServitecManager/servitec_manager/SERVITEC.DB")
    print(f"\n📍 Destino de importación:")
    print(f"   {destino_default}")
    
    usar_default = input("\n¿Usar esta ubicación? (S/N): ").strip().upper()
    
    if usar_default != 'S':
        ruta_destino = input("Ingresa la ruta completa de destino: ").strip()
        bd_destino = Path(ruta_destino)
    else:
        bd_destino = destino_default
    
    # Crear backup del destino si existe
    if bd_destino.exists():
        print(f"\n⚠️  ATENCIÓN: Ya existe una base de datos en el destino")
        crear_backup = input("¿Crear backup antes de reemplazar? (S/N): ").strip().upper()
        
        if crear_backup == 'S':
            backup_dir = bd_destino.parent / "backups"
            backup_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"SERVITEC_BACKUP_{timestamp}.DB"
            shutil.copy2(bd_destino, backup_path)
            print(f"✅ Backup creado: {backup_path}")
    
    # Confirmar importación
    print("\n" + "-" * 60)
    print(f"ORIGEN:  {bd_backup.absolute()}")
    print(f"DESTINO: {bd_destino}")
    print("-" * 60)
    
    confirmar = input("\n¿Continuar con la importación? (S/N): ").strip().upper()
    
    if confirmar != 'S':
        print("\n❌ Importación cancelada")
        input("Presiona ENTER para cerrar...")
        return False
    
    # Copiar base de datos
    print("\n⏳ Importando base de datos...")
    try:
        bd_destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(bd_backup, bd_destino)
        print("✅ Base de datos importada exitosamente")
        
        print("\n" + "=" * 60)
        print("  ✅ IMPORTACIÓN COMPLETADA")
        print("=" * 60)
        print("\n💡 Ahora puedes abrir ServitecManager normalmente")
        
        return True
    except Exception as e:
        print(f"\n❌ ERROR al importar: {e}")
        return False

def main():
    print("\n¿Qué deseas hacer?")
    print("1. EXPORTAR base de datos (crear backup)")
    print("2. IMPORTAR base de datos (restaurar backup)")
    print("3. Salir")
    
    opcion = input("\nSelecciona una opción (1/2/3): ").strip()
    
    if opcion == '1':
        exportar_base_datos()
    elif opcion == '2':
        importar_base_datos()
    else:
        print("\n👋 Saliendo...")
        return
    
    input("\nPresiona ENTER para cerrar...")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("\nPresiona ENTER para cerrar...")
