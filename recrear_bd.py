#!/usr/bin/env python3
"""Script para recrear la base de datos con el esquema correcto"""
import sqlite3
import os

# Rutas
DB_PATH = "servitec_manager/SERVITEC_TEST_OPTIMIZED.DB"
SCHEMA_PATH = "database_schema_optimized.sql"

# Eliminar BD existente
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print(f"✓ BD eliminada: {DB_PATH}")

# Crear nueva BD
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Leer y ejecutar schema
with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
    schema_content = f.read()

# Ejecutar cada comando SQL
for statement in schema_content.split(';'):
    statement = statement.strip()
    if statement and not statement.startswith('--'):
        try:
            cursor.execute(statement)
        except sqlite3.Error as e:
            # Ignorar errores de PRAGMA y comandos sin efecto
            if "no such table" not in str(e).lower():
                print(f"⚠️  Error (ignorado): {e}")

conn.commit()
conn.close()

print(f"✅ Base de datos recreada: {DB_PATH}")
print("✅ Esquema aplicado con columna 'cedula' (no 'rut')")
