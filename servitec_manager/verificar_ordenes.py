import sqlite3

conn = sqlite3.connect('SERVITEC_TEST_OPTIMIZED.DB')
c = conn.cursor()

print("\n" + "="*120)
print("ESTADO ACTUAL DE ÓRDENES - ANTES DEL COBRO EN POS")
print("="*120)
print(f"{'ID':<4} | {'EQUIPO':<25} | {'ESTADO':<12} | {'CONDICIÓN':<12} | {'PRESUP.':<10} | {'FECHA_CIERRE':<20}")
print("-"*120)

c.execute('''
    SELECT 
        id, 
        equipo, 
        estado, 
        condicion, 
        presupuesto_inicial, 
        fecha_cierre,
        COALESCE(pago_efectivo, 0) as pago_efec,
        COALESCE(pago_transferencia, 0) as pago_trf,
        COALESCE(utilidad_bruta, 0) as utilidad,
        COALESCE(comision_tecnico, 0) as comision
    FROM ordenes 
    ORDER BY id
''')

for r in c.fetchall():
    id_orden, equipo, estado, cond, presup, fecha_c, pago_e, pago_t, util, comis = r
    print(f"{id_orden:<4} | {equipo:<25} | {estado:<12} | {cond or 'PENDIENTE':<12} | ${presup:>9,.0f} | {fecha_c or 'NO CERRADA':<20}")

print("\n" + "="*120)
print("DETALLE FINANCIERO DE ORDEN #1 (Para cobrar en POS)")
print("="*120)

c.execute('''
    SELECT 
        id,
        equipo,
        estado,
        condicion,
        presupuesto_inicial,
        COALESCE(total_a_cobrar, 0),
        COALESCE(abono, 0),
        COALESCE(saldo_pendiente, 0),
        fecha_cierre,
        COALESCE(pago_efectivo, 0),
        COALESCE(pago_transferencia, 0),
        COALESCE(pago_debito, 0),
        COALESCE(pago_credito, 0),
        COALESCE(utilidad_bruta, 0),
        COALESCE(comision_tecnico, 0)
    FROM ordenes 
    WHERE id = 1
''')

orden = c.fetchone()
if orden:
    print(f"\n📋 ORDEN #{orden[0]}")
    print(f"   Equipo: {orden[1]}")
    print(f"   Estado: {orden[2]}")
    print(f"   Condición: {orden[3] or 'PENDIENTE'}")
    print(f"   Presupuesto Inicial: ${orden[4]:,.0f}")
    print(f"   Total a Cobrar: ${orden[5]:,.0f}")
    print(f"   Abono: ${orden[6]:,.0f}")
    print(f"   Saldo Pendiente: ${orden[7]:,.0f}")
    print(f"   Fecha Cierre: {orden[8] or 'NO CERRADA'}")
    print(f"\n💰 PAGOS:")
    print(f"   Efectivo: ${orden[9]:,.0f}")
    print(f"   Transferencia: ${orden[10]:,.0f}")
    print(f"   Débito: ${orden[11]:,.0f}")
    print(f"   Crédito: ${orden[12]:,.0f}")
    print(f"\n📊 FINANCIERO:")
    print(f"   Utilidad Bruta: ${orden[13]:,.0f}")
    print(f"   Comisión Técnico: ${orden[14]:,.0f}")
else:
    print("❌ Orden #1 no encontrada")

print("\n" + "="*120)
print("🎯 INSTRUCCIONES PARA LA PRUEBA:")
print("="*120)
print("1. Abre el módulo POS en la interfaz")
print("2. Agrega la ORDEN #1 al carrito")
print("3. Ingresa método de pago (ejemplo: $105,000 en Efectivo)")
print("4. Finaliza la venta")
print("5. Ejecuta nuevamente este script para ver los cambios")
print("6. Verifica que:")
print("   ✓ fecha_cierre tenga valor")
print("   ✓ estado = 'Entregado'")
print("   ✓ condicion = 'SOLUCIONADO'")
print("   ✓ pago_efectivo = 105000")
print("   ✓ utilidad_bruta > 0")
print("   ✓ comision_tecnico > 0")
print("="*120 + "\n")

conn.close()
