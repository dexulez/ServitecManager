"""
Script de corrección final: Recrea tabla clientes con columna cedula
"""
import sqlite3
import shutil
import os
from datetime import datetime

print("=" * 80)
print("CORRECCIÓN FINAL: Recreando tabla clientes con cedula")
print("=" * 80)
print()

db_path = 'servitec_manager/SERVITEC_TEST_OPTIMIZED.DB'

# Hacer backup
backup_path = f'servitec_manager/SERVITEC_TEST_OPTIMIZED_BACKUP_{datetime.now().strftime("%Y%m%d_%H%M%S")}.DB'
print(f"1. Creando backup: {backup_path}")
shutil.copy2(db_path, backup_path)
print("   BACKUP CREADO")
print()

# Conectar y recrear tabla
print("2. Recreando tabla clientes...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Obtener datos actuales
print("   -> Respaldando datos existentes...")
cursor.execute("SELECT * FROM clientes")
datos_antiguos = cursor.fetchall()
print(f"   -> {len(datos_antiguos)} clientes encontrados")

# Eliminar tabla vieja
print("   -> Eliminando tabla antigua...")
cursor.execute("DROP TABLE IF EXISTS clientes")

# Crear tabla nueva con cedula
print("   -> Creando tabla nueva con cedula...")
cursor.execute("""
    CREATE TABLE clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cedula TEXT UNIQUE,
        nombre TEXT NOT NULL,
        telefono TEXT,
        email TEXT,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Recrear índice
cursor.execute("CREATE INDEX idx_clientes_cedula ON clientes(cedula)")
cursor.execute("CREATE INDEX idx_clientes_nombre ON clientes(nombre)")

# Restaurar datos (mapear rut -> cedula)
print("   -> Restaurando datos...")
if datos_antiguos:
    # Detectar estructura antigua
    # Puede ser (id, rut, nombre, telefono, email, fecha_creacion)
    # o (id, cedula, nombre, telefono, email, fecha_creacion)
    for row in datos_antiguos:
        try:
            # Asumiendo: id, rut/cedula, nombre, telefono, email, fecha_creacion
            id_cliente = row[0]
            cedula = row[1]  # Ya sea rut o cedula
            nombre = row[2]
            telefono = row[3] if len(row) > 3 else ""
            email = row[4] if len(row) > 4 else ""
            fecha = row[5] if len(row) > 5 else datetime.now()
            
            cursor.execute(
                "INSERT INTO clientes (id, cedula, nombre, telefono, email, fecha_creacion) VALUES (?, ?, ?, ?, ?, ?)",
                (id_cliente, cedula, nombre, telefono, email, fecha)
            )
        except Exception as e:
            print(f"   ADVERTENCIA: Error restaurando cliente {row}: {e}")

print(f"   -> {cursor.lastrowid} clientes restaurados")

# Confirmar cambios
conn.commit()

# Verificar resultado
print()
print("3. Verificando estructura final...")
cursor.execute("PRAGMA table_info(clientes)")
columnas = cursor.fetchall()
print("   Columnas en tabla clientes:")
for col in columnas:
    print(f"      - {col[1]} ({col[2]})")

# Verificar datos
cursor.execute("SELECT COUNT(*) FROM clientes")
total = cursor.fetchone()[0]
print(f"   Total de clientes: {total}")

conn.close()

print()
print("=" * 80)
print("CORRECCIÓN COMPLETADA EXITOSAMENTE")
print("=" * 80)
print("Ahora puede reiniciar la aplicación:")
print("  python servitec_manager\\main.py")
print()
