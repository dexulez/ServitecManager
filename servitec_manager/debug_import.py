import pandas as pd
import sqlite3

# Cargar archivo Excel
archivo = "dist/LISTA_REPUESTOS_MULTI.xlsx"
df = pd.read_excel(archivo, engine='openpyxl')

print(f"Total de registros en Excel: {len(df)}")
print(f"Columnas: {list(df.columns)}")
print()

# Normalizar columnas
df.columns = df.columns.str.upper().str.strip()

# Verificar cuántos tienen precio válido
precio_col = 'PRECIO_PROVEEDOR'
nombre_col = 'NOMBRE'

registros_validos = 0
registros_sin_precio = 0
registros_sin_nombre = 0

for idx, row in df.iterrows():
    nombre = str(row[nombre_col]).upper().strip()
    
    if nombre == 'NAN' or not nombre:
        registros_sin_nombre += 1
        continue
    
    try:
        precio_val = row[precio_col]
        if pd.isna(precio_val) or precio_val == '' or precio_val == 0:
            registros_sin_precio += 1
            continue
        precio = float(precio_val)
        registros_validos += 1
    except:
        registros_sin_precio += 1
        continue

print(f"Registros válidos (con nombre y precio): {registros_validos}")
print(f"Registros sin nombre: {registros_sin_nombre}")
print(f"Registros sin precio o precio en 0: {registros_sin_precio}")
print()

# Verificar cuántos existen en la base de datos
conn = sqlite3.connect('SERVITEC.DB')
cursor = conn.cursor()
cursor.execute("SELECT id, nombre FROM repuestos")
repuestos_db = cursor.fetchall()
conn.close()

print(f"Total de repuestos en base de datos: {len(repuestos_db)}")
print()

# Verificar coincidencias
coincidencias = 0
no_encontrados = []

for idx, row in df.iterrows():
    nombre_excel = str(row[nombre_col]).upper().strip()
    
    if nombre_excel == 'NAN' or not nombre_excel:
        continue
    
    try:
        precio_val = row[precio_col]
        if pd.isna(precio_val) or precio_val == '' or precio_val == 0:
            continue
    except:
        continue
    
    # Buscar en BD
    encontrado = False
    for id_rep, nombre_db in repuestos_db:
        if nombre_db.upper() == nombre_excel:
            encontrado = True
            coincidencias += 1
            break
    
    if not encontrado:
        no_encontrados.append(nombre_excel)

print(f"Coincidencias encontradas: {coincidencias}")
print(f"No encontrados en BD: {len(no_encontrados)}")

if len(no_encontrados) > 0:
    print("\nPrimeros 10 no encontrados:")
    for nombre in no_encontrados[:10]:
        print(f"  - {nombre}")
