"""
Script de migración para agregar la columna descuento a la tabla ordenes
"""
import sqlite3
import os

def migrar_base_datos():
    db_path = 'SERVITEC.DB'
    
    if not os.path.exists(db_path):
        print(f"❌ Base de datos no encontrada: {db_path}")
        print(f"   Ubicación esperada: {os.path.abspath(db_path)}")
        return False
    
    try:
        print(f"📂 Base de datos encontrada: {os.path.abspath(db_path)}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Desactivar foreign keys temporalmente
        cursor.execute("PRAGMA foreign_keys = OFF")
        
        # Verificar si la columna ya existe
        cursor.execute("PRAGMA table_info(ordenes)")
        columnas = cursor.fetchall()
        columnas_nombres = [col[1] for col in columnas]
        
        print(f"📋 Columnas actuales en tabla 'ordenes': {', '.join(columnas_nombres)}")
        
        if 'descuento' in columnas_nombres:
            print("✓ La columna 'descuento' ya existe en la tabla ordenes")
            cursor.execute("PRAGMA foreign_keys = ON")
            conn.close()
            return True
        
        # Agregar la columna descuento
        print("🔧 Agregando columna 'descuento' a la tabla ordenes...")
        cursor.execute("ALTER TABLE ordenes ADD COLUMN descuento INTEGER DEFAULT 0")
        conn.commit()
        print("✓ Columna 'descuento' agregada exitosamente")
        
        # Reactivar foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Verificar que se agregó correctamente
        cursor.execute("PRAGMA table_info(ordenes)")
        columnas_nuevas = cursor.fetchall()
        columnas_nuevas_nombres = [col[1] for col in columnas_nuevas]
        
        if 'descuento' in columnas_nuevas_nombres:
            print("✓ Verificación exitosa: columna 'descuento' confirmada")
        else:
            print("⚠️ Advertencia: No se pudo verificar la columna")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error al migrar base de datos: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("MIGRACIÓN DE BASE DE DATOS - COLUMNA DESCUENTO")
    print("=" * 60)
    migrar_base_datos()
    print("=" * 60)
    input("Presione ENTER para salir...")
