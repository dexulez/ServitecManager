"""
Script para limpiar completamente la base de datos
Elimina TODOS los registros excepto el usuario admin
"""
import sqlite3
import os
from datetime import datetime

DB_PATH = "SERVITEC_TEST_OPTIMIZED.DB"

def limpiar_base_datos():
    """Limpia toda la base de datos excepto usuario admin"""
    
    if not os.path.exists(DB_PATH):
        print(f"❌ ERROR: No se encuentra la base de datos en {DB_PATH}")
        return
    
    # Crear backup antes de limpiar
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{DB_PATH}.backup_antes_limpiar_{timestamp}"
    
    print("="*80)
    print("🗑️  LIMPIEZA TOTAL DE BASE DE DATOS")
    print("="*80)
    print(f"\n⚠️  ADVERTENCIA: Este script eliminará TODOS los datos de la base de datos")
    print(f"⚠️  Se mantendrá únicamente el usuario 'admin' con contraseña 'admin123'\n")
    
    # Solicitar confirmación
    respuesta = input("¿Estás seguro de continuar? (escribe 'SI' en mayúsculas): ")
    
    if respuesta != "SI":
        print("\n❌ Operación cancelada por el usuario")
        return
    
    print(f"\n[1/3] Creando backup de seguridad...")
    try:
        import shutil
        shutil.copy2(DB_PATH, backup_path)
        print(f"✅ Backup creado: {backup_path}")
    except Exception as e:
        print(f"⚠️  No se pudo crear backup: {e}")
        respuesta2 = input("¿Continuar sin backup? (SI/NO): ")
        if respuesta2 != "SI":
            return
    
    print(f"\n[2/3] Conectando a base de datos...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Obtener lista de todas las tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tablas = [t[0] for t in cursor.fetchall()]
        
        print(f"✅ Conexión establecida")
        print(f"\n[3/3] Limpiando {len(tablas)} tablas...")
        print("-"*80)
        
        # Desactivar foreign keys temporalmente
        cursor.execute("PRAGMA foreign_keys = OFF")
        
        tablas_limpiadas = 0
        registros_eliminados = 0
        
        for tabla in tablas:
            # Contar registros antes
            cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
            count_antes = cursor.fetchone()[0]
            
            if tabla == 'usuarios':
                # Para usuarios, eliminar todos EXCEPTO admin
                cursor.execute("DELETE FROM usuarios WHERE nombre != 'admin'")
                
                # Verificar si existe admin, si no, crearlo
                cursor.execute("SELECT COUNT(*) FROM usuarios WHERE nombre = 'admin'")
                if cursor.fetchone()[0] == 0:
                    # Crear usuario admin
                    # La contraseña debe estar hasheada según el sistema que uses
                    cursor.execute("""
                        INSERT INTO usuarios (nombre, password, rol, porcentaje_comision, activo, fecha_creacion)
                        VALUES ('admin', 'admin123', 'Admin', 50.0, 1, datetime('now'))
                    """)
                    print(f"  👤 usuarios: Usuario 'admin' creado")
                else:
                    # Actualizar contraseña de admin por si acaso
                    cursor.execute("UPDATE usuarios SET password = 'admin123', activo = 1 WHERE nombre = 'admin'")
                    print(f"  👤 usuarios: Mantenido usuario 'admin' (otros {count_antes - 1} eliminados)")
            else:
                # Para otras tablas, eliminar TODO
                cursor.execute(f"DELETE FROM {tabla}")
                
                if count_antes > 0:
                    print(f"  🗑️  {tabla}: {count_antes} registros eliminados")
                    registros_eliminados += count_antes
                    tablas_limpiadas += 1
        
        # Reactivar foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Hacer commit
        conn.commit()
        
        print("-"*80)
        print(f"\n✅ LIMPIEZA COMPLETADA EXITOSAMENTE")
        print(f"   • Tablas procesadas: {len(tablas)}")
        print(f"   • Tablas limpiadas: {tablas_limpiadas}")
        print(f"   • Total registros eliminados: {registros_eliminados}")
        print(f"   • Usuario 'admin' preservado ✓")
        print(f"\n💾 Backup disponible en: {backup_path}")
        
        # Mostrar estado final
        print(f"\n📊 ESTADO FINAL DE LA BASE DE DATOS:")
        print("-"*80)
        
        for tabla in sorted(tablas):
            cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
            count = cursor.fetchone()[0]
            if count > 0:
                print(f"  • {tabla}: {count} registro(s)")
        
        print("="*80)
        print("✅ Base de datos lista para usar con datos limpios")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ ERROR durante la limpieza: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    limpiar_base_datos()
    input("\nPresiona Enter para cerrar...")
