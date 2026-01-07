import sqlite3

conn = sqlite3.connect('servitec_manager/SERVITEC_TEST_OPTIMIZED.DB')
cursor = conn.cursor()

# Query exacto que usa el sistema para tickets
cursor.execute('SELECT o.*, c.cedula, c.nombre, c.telefono, c.email FROM ordenes o JOIN clientes c ON o.cliente_id = c.id WHERE o.id = 1')
row = cursor.fetchone()

if row:
    print(f"Total columnas: {len(row)}")
    print("\n" + "="*80)
    for i, val in enumerate(row):
        print(f"[{i:2d}] = {val}")
    print("="*80)
    
    # Identificar columnas clave
    print("\nColumnas críticas para PDF:")
    print(f"presupuesto_inicial: índice {row.index(50000.0) if 50000.0 in row else '?'}")
    print(f"total_a_cobrar: buscar manualmente")
    print(f"cedula cliente: índice {len(row)-4}")
    print(f"nombre cliente: índice {len(row)-3}")
    print(f"telefono cliente: índice {len(row)-2}")
    print(f"email cliente: índice {len(row)-1}")

conn.close()
