"""
Script de migración para agregar la columna descuento a la tabla ordenes
"""
import sqlite3
import os

def migrar_base_datos():
    db_path = 'SERVITEC.DB'
    
    if not os.path.exists(db_path):
        print(f"❌ Base de datos no encontrada: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si la columna ya existe
        cursor.execute("PRAGMA table_info(ordenes)")
        columnas = cursor.fetchall()
        columnas_nombres = [col[1] for col in columnas]
        
        if 'descuento' in columnas_nombres:
            print("✓ La columna 'descuento' ya existe en la tabla ordenes")
            conn.close()
            return True
        
        # Agregar la columna descuento
        print("🔧 Agregando columna 'descuento' a la tabla ordenes...")
        cursor.execute("ALTER TABLE ordenes ADD COLUMN descuento INTEGER DEFAULT 0")
        conn.commit()
        print("✓ Columna 'descuento' agregada exitosamente")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error al migrar base de datos: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("MIGRACIÓN DE BASE DE DATOS - COLUMNA DESCUENTO")
    print("=" * 60)
    migrar_base_datos()
    print("=" * 60)
    input("Presione ENTER para salir...")
