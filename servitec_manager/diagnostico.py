"""
Script de diagnóstico para verificar el estado del sistema ServitecManager
Ejecutar este script para diagnosticar problemas con descuentos y órdenes
"""
import sqlite3
import os

print("=" * 70)
print("DIAGNÓSTICO DE SERVITECMANAGER")
print("=" * 70)
print()

# Verificar que existe la base de datos
if not os.path.exists('SERVITEC.DB'):
    print("❌ ERROR: No se encuentra la base de datos SERVITEC.DB")
    print("   Ubicación actual:", os.getcwd())
    input("\nPresiona ENTER para salir...")
    exit(1)

conn = sqlite3.connect('SERVITEC.DB')
cursor = conn.cursor()

print("1. VERIFICANDO ESTRUCTURA DE LA TABLA ORDENES")
print("-" * 70)
cursor.execute("PRAGMA table_info(ordenes)")
columnas = cursor.fetchall()
columnas_nombres = [col[1] for col in columnas]

print(f"   Total de columnas: {len(columnas)}")
print("   Columnas encontradas:")
for i, col in enumerate(columnas):
    print(f"      {i}: {col[1]} ({col[2]})")

if 'descuento' in columnas_nombres:
    print("\n   ✅ La columna 'descuento' EXISTE")
else:
    print("\n   ❌ La columna 'descuento' NO EXISTE")
    print("   💡 Solución: Ejecuta 'python main.py' para aplicar migración automática")

print("\n2. VERIFICANDO ÓRDENES EN LA BASE DE DATOS")
print("-" * 70)
cursor.execute("SELECT COUNT(*) FROM ordenes")
total_ordenes = cursor.fetchone()[0]
print(f"   Total de órdenes: {total_ordenes}")

if total_ordenes > 0:
    cursor.execute("SELECT id, fecha, estado FROM ordenes ORDER BY id DESC LIMIT 5")
    ordenes = cursor.fetchall()
    print("   Últimas 5 órdenes:")
    for orden in ordenes:
        print(f"      ID: {orden[0]}, Fecha: {orden[1]}, Estado: {orden[2]}")
    
    # Verificar última orden con todos sus datos
    print("\n3. VERIFICANDO DATOS DE LA ÚLTIMA ORDEN (CON DESCUENTO)")
    print("-" * 70)
    cursor.execute("SELECT * FROM ordenes ORDER BY id DESC LIMIT 1")
    ultima_orden = cursor.fetchone()
    
    if ultima_orden:
        print(f"   ID: {ultima_orden[0]}")
        print(f"   Cliente ID: {ultima_orden[1]}")
        print(f"   Técnico ID: {ultima_orden[2]}")
        print(f"   Fecha: {ultima_orden[3]}")
        print(f"   Equipo: {ultima_orden[4]}")
        print(f"   Presupuesto: ${ultima_orden[12]}")
        
        if len(ultima_orden) > 16:
            print(f"   Descuento: ${ultima_orden[16]}")
        else:
            print("   ⚠️ No se puede leer descuento (columna no existe en esta orden)")
        
        if len(ultima_orden) > 13:
            print(f"   Abono: ${ultima_orden[13]}")

print("\n4. VERIFICANDO QUERY DE HISTORIAL")
print("-" * 70)
cursor.execute("""
    SELECT o.id, o.fecha, c.nombre AS cliente_nombre, o.equipo || ' ' || o.modelo AS equipo_completo, 
           u.nombre AS tecnico_nombre, o.estado, o.observacion, o.fecha_entrega, 
           o.presupuesto, f.fecha_cierre
    FROM ORDENES o
    LEFT JOIN clientes c ON o.cliente_id = c.id
    LEFT JOIN usuarios u ON o.tecnico_id = u.id
    LEFT JOIN finanzas f ON o.id = f.orden_id
    ORDER BY o.id DESC
    LIMIT 3
""")
historial = cursor.fetchall()
print(f"   Órdenes en historial: {len(historial)}")
for h in historial:
    print(f"      ID: {h[0]}, Cliente: {h[2]}, Estado: {h[5]}")

conn.close()

print("\n" + "=" * 70)
print("DIAGNÓSTICO COMPLETADO")
print("=" * 70)
print()
input("Presiona ENTER para salir...")
