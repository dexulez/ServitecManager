import sqlite3

conn = sqlite3.connect('SERVITEC_TEST_OPTIMIZED.DB')
cursor = conn.cursor()

print("=== TODOS LOS CLIENTES ===")
cursor.execute('SELECT id, cedula, nombre, telefono FROM clientes')
for row in cursor.fetchall():
    print(f"ID: {row[0]}, Cédula: {row[1]}, Nombre: {row[2]}, Teléfono: {row[3]}")

print("\n=== BÚSQUEDA POR CÉDULA FORMATEADA ===")
cursor.execute('SELECT * FROM clientes WHERE cedula LIKE ?', ('%26.595.544-4%',))
rows = cursor.fetchall()
print(f"Resultados con formato '26.595.544-4': {len(rows)} encontrados")
for row in rows:
    print(row)

print("\n=== BÚSQUEDA POR CÉDULA SIN FORMATO ===")
cursor.execute('SELECT * FROM clientes WHERE REPLACE(REPLACE(cedula, ".", ""), "-", "") LIKE ?', ('%265955444%',))
rows = cursor.fetchall()
print(f"Resultados sin formato '265955444': {len(rows)} encontrados")
for row in rows:
    print(row)

print("\n=== BÚSQUEDA COMO LO HACE BUSCAR_CLIENTES ===")
consulta = "26.595.544-4"
q = consulta.upper()
qc = ''.join(filter(lambda x: x.isalnum(), q))
print(f"q = '{q}'")
print(f"qc = '{qc}'")

cursor.execute(
    "SELECT * FROM clientes WHERE NOMBRE LIKE ? OR REPLACE(REPLACE(cedula, '.', ''), '-', '') LIKE ? LIMIT 50", 
    (f"%{q}%", f"%{qc}%")
)
rows = cursor.fetchall()
print(f"Resultados: {len(rows)} encontrados")
for row in rows:
    print(row)

conn.close()
