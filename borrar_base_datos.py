"""
Script de Borrado Exhaustivo de Base de Datos
- Crea respaldo automático antes de borrar
- Limpia completamente todas las tablas de datos
- Elimina caché después del borrado
"""
import sqlite3
import shutil
import os
from datetime import datetime
import glob

def crear_respaldo():
    """Crea una copia de respaldo de la base de datos"""
    db_path = 'SERVITEC.DB'
    if not os.path.exists(db_path):
        print("❌ Base de datos no encontrada")
        return None
    
    # Crear carpeta de respaldos si no existe
    backup_dir = '../backups/db_backups'
    os.makedirs(backup_dir, exist_ok=True)
    
    # Nombre del respaldo con fecha y hora
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(backup_dir, f'SERVITEC_BACKUP_{timestamp}.db')
    
    try:
        shutil.copy2(db_path, backup_path)
        print(f"✅ Respaldo creado: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ Error al crear respaldo: {e}")
        return None

def limpiar_cache():
    """Elimina todos los archivos de caché de Python"""
    print("\n🧹 Limpiando caché de Python...")
    try:
        # Limpiar carpetas __pycache__
        for pycache_dir in glob.glob("**/__pycache__", recursive=True):
            if os.path.exists(pycache_dir):
                shutil.rmtree(pycache_dir, ignore_errors=True)
                print(f"  ✓ Eliminado: {pycache_dir}")
        
        # Limpiar archivos .pyc
        pyc_count = 0
        for pyc_file in glob.glob("**/*.pyc", recursive=True):
            if os.path.exists(pyc_file):
                os.remove(pyc_file)
                pyc_count += 1
        
        if pyc_count > 0:
            print(f"  ✓ Eliminados {pyc_count} archivos .pyc")
        
        print("✅ Caché limpiado completamente")
    except Exception as e:
        print(f"⚠️ Error limpiando caché: {e}")

def borrar_base_datos():
    """Borra todos los datos de las tablas principales"""
    db_path = 'SERVITEC.DB'
    
    if not os.path.exists(db_path):
        print("❌ Base de datos no encontrada")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Tablas a limpiar (mantiene usuarios y configuración)
        tablas_limpiar = [
            'ordenes',
            'finanzas',
            'ventas',
            'detalle_ventas',
            'repuestos',
            'pedidos',
            'compras',
            'detalle_compras',
            'gastos',
            'caja_sesiones',
            'clientes'  # También limpiamos clientes
        ]
        
        print("\n🗑️ Borrando datos de las tablas...")
        for tabla in tablas_limpiar:
            try:
                cursor.execute(f'DELETE FROM {tabla}')
                filas = cursor.rowcount
                print(f"  ✓ {tabla}: {filas} registros eliminados")
            except sqlite3.Error as e:
                if "no such table" not in str(e):
                    print(f"  ⚠️ {tabla}: {e}")
        
        # Resetear secuencias de autoincremento
        cursor.execute("DELETE FROM sqlite_sequence")
        print("  ✓ Secuencias de autoincremento reseteadas")
        
        conn.commit()
        conn.close()
        
        print("✅ Base de datos limpiada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error al borrar datos: {e}")
        return False

def main():
    print("═" * 70)
    print("  BORRADO EXHAUSTIVO DE BASE DE DATOS - SERVITEC MANAGER")
    print("═" * 70)
    print("\n⚠️  ADVERTENCIA: Esta acción borrará TODOS los datos")
    print("   (Órdenes, Clientes, Ventas, Finanzas, Inventario, etc.)")
    print("\n   Se mantendrán: Usuarios, Configuración de empresa")
    print("\n" + "═" * 70)
    
    respuesta = input("\n¿Está seguro de continuar? (SI/no): ").strip().upper()
    
    if respuesta != "SI":
        print("\n❌ Operación cancelada")
        return
    
    print("\n" + "═" * 70)
    print("INICIANDO PROCESO DE BORRADO")
    print("═" * 70)
    
    # Paso 1: Crear respaldo
    print("\n[1/3] Creando respaldo de seguridad...")
    backup_path = crear_respaldo()
    if not backup_path:
        respuesta = input("\n⚠️  No se pudo crear respaldo. ¿Continuar de todos modos? (si/NO): ").strip().lower()
        if respuesta != "si":
            print("❌ Operación cancelada por seguridad")
            return
    
    # Paso 2: Borrar datos
    print("\n[2/3] Borrando datos de la base de datos...")
    if not borrar_base_datos():
        print("\n❌ No se pudo completar el borrado")
        return
    
    # Paso 3: Limpiar caché
    print("\n[3/3] Limpiando caché del sistema...")
    limpiar_cache()
    
    print("\n" + "═" * 70)
    print("  ✅ PROCESO COMPLETADO EXITOSAMENTE")
    print("═" * 70)
    if backup_path:
        print(f"\n📦 Respaldo guardado en: {backup_path}")
    print("\n💡 Reinicie ServitecManager para ver los cambios")
    print("=" * 70)
    
    input("\nPresione ENTER para salir...")

if __name__ == "__main__":
    # Cambiar al directorio servitec_manager
    if os.path.basename(os.getcwd()) != 'servitec_manager':
        os.chdir('servitec_manager')
    
    main()
