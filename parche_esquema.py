"""
Parche de esquema para SERVITEC_TEST_OPTIMIZED.DB
Aplica cambios faltantes para compatibilidad con código de SEMANA 3
"""
import sqlite3
import sys

print("Aplicando parche de esquema a SERVITEC_TEST_OPTIMIZED.DB...")
print()

try:
    conn = sqlite3.connect('servitec_manager/SERVITEC_TEST_OPTIMIZED.DB')
    cursor = conn.cursor()
    
    # CAMBIO 1: Renombrar columna rut a cedula en tabla clientes
    print("1. Verificando columna 'rut' en tabla clientes...")
    cursor.execute("PRAGMA table_info(clientes)")
    columnas = cursor.fetchall()
    columnas_nombres = [col[1] for col in columnas]
    
    if 'rut' in columnas_nombres and 'cedula' not in columnas_nombres:
        print("   -> Renombrando 'rut' a 'cedula'...")
        cursor.execute("ALTER TABLE clientes RENAME COLUMN rut TO cedula")
        print("   APLICADO: Columna renombrada a 'cedula'")
    elif 'cedula' in columnas_nombres:
        print("   OK: Columna 'cedula' ya existe")
    else:
        print("   ADVERTENCIA: No se encontro ni 'rut' ni 'cedula'")
    
    # CAMBIO 2: Actualizar índice de rut a cedula
    print()
    print("2. Actualizando índice de clientes...")
    try:
        cursor.execute("DROP INDEX IF EXISTS idx_clientes_rut")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_clientes_cedula ON clientes(cedula)")
        print("   APLICADO: Indice 'idx_clientes_cedula' creado")
    except Exception as e:
        print(f"   ADVERTENCIA: Error en indice - {e}")
    
    # CAMBIO 3: Crear tabla cuentas_bancarias si no existe
    print()
    print("3. Verificando tabla 'cuentas_bancarias'...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cuentas_bancarias'")
    tabla_existe = cursor.fetchone()
    
    if not tabla_existe:
        print("   -> Creando tabla 'cuentas_bancarias'...")
        cursor.execute("""
            CREATE TABLE cuentas_bancarias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                banco TEXT NOT NULL,
                numero_cuenta TEXT NOT NULL UNIQUE,
                tipo_cuenta TEXT,
                titular TEXT NOT NULL,
                rut_titular TEXT,
                notas TEXT,
                activa INTEGER DEFAULT 1,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("   APLICADO: Tabla 'cuentas_bancarias' creada")
    else:
        print("   OK: Tabla 'cuentas_bancarias' ya existe")
    
    # Confirmar cambios
    conn.commit()
    conn.close()
    
    print()
    print("=" * 70)
    print("PARCHE APLICADO EXITOSAMENTE")
    print("=" * 70)
    print("Cambios realizados:")
    print("  - Columna 'rut' renombrada a 'cedula' en tabla clientes")
    print("  - Indice 'idx_clientes_cedula' actualizado")
    print("  - Tabla 'cuentas_bancarias' creada")
    print()
    print("La base de datos ahora es compatible con el codigo de SEMANA 3.")
    print("Puede reiniciar la aplicacion: python servitec_manager\\main.py")
    print()
    sys.exit(0)
    
except Exception as e:
    print()
    print("=" * 70)
    print("ERROR AL APLICAR PARCHE")
    print("=" * 70)
    print(f"Error: {e}")
    print()
    sys.exit(1)
