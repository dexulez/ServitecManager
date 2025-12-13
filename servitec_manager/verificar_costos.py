from database import GESTOR_BASE_DATOS

bd = GESTOR_BASE_DATOS('SERVITEC.DB')

# Verificar costos de repuestos
print("=== REPUESTOS CON 'PANTALLA' EN EL NOMBRE ===")
repuestos = bd.OBTENER_TODOS("""
    SELECT id, nombre, costo 
    FROM repuestos 
    WHERE nombre LIKE '%PANTALLA%' 
    LIMIT 10
""", ())

for r in repuestos:
    print(f"ID: {r[0]}")
    print(f"  Nombre: {r[1]}")
    print(f"  Costo: {r[2]}")
    print()

# Verificar pedidos
print("\n=== PEDIDOS EXISTENTES ===")
pedidos = bd.OBTENER_TODOS("""
    SELECT p.id, p.repuesto_id, p.producto_id, p.cantidad, r.nombre as rep_nombre, i.nombre as prod_nombre
    FROM pedidos p
    LEFT JOIN repuestos r ON p.repuesto_id = r.id
    LEFT JOIN inventario i ON p.producto_id = i.id
    LIMIT 5
""", ())

for p in pedidos:
    print(f"Pedido ID: {p[0]}")
    print(f"  Repuesto ID: {p[1]}")
    print(f"  Producto ID: {p[2]}")
    print(f"  Cantidad: {p[3]}")
    print(f"  Nombre Repuesto: {p[4]}")
    print(f"  Nombre Producto: {p[5]}")
    print()
