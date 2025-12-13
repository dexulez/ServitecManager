import sqlite3

# Verificar la BD del root
print('=== BD EN ROOT ===')
conn1 = sqlite3.connect('SERVITEC.DB')
cur1 = conn1.cursor()
ordenes1 = cur1.execute('SELECT id, cliente_id, tecnico_id, equipo, modelo, estado FROM ORDENES ORDER BY id DESC').fetchall()
print(f'Total órdenes: {len(ordenes1)}')
for o in ordenes1[:5]:
    cliente = cur1.execute('SELECT nombre FROM clientes WHERE id = ?', (o[1],)).fetchone()
    tecnico = cur1.execute('SELECT nombre FROM usuarios WHERE id = ?', (o[2],)).fetchone()
    print(f'  #{o[0]}: cliente={cliente[0] if cliente else "NULL"}, equipo={o[3]} {o[4]}, tecnico_id={o[2]}, tecnico_nombre={tecnico[0] if tecnico else "NULL"}, estado={o[5]}')
conn1.close()

print('\n=== BD EN servitec_manager/ ===')
conn2 = sqlite3.connect('servitec_manager/SERVITEC.DB')
cur2 = conn2.cursor()
ordenes2 = cur2.execute('SELECT id, cliente_id, tecnico_id, equipo, modelo, estado FROM ORDENES ORDER BY id DESC').fetchall()
print(f'Total órdenes: {len(ordenes2)}')
for o in ordenes2[:5]:
    cliente = cur2.execute('SELECT nombre FROM clientes WHERE id = ?', (o[1],)).fetchone()
    tecnico = cur2.execute('SELECT nombre FROM usuarios WHERE id = ?', (o[2],)).fetchone()
    print(f'  #{o[0]}: cliente={cliente[0] if cliente else "NULL"}, equipo={o[3]} {o[4]}, tecnico_id={o[2]}, tecnico_nombre={tecnico[0] if tecnico else "NULL"}, estado={o[5]}')
conn2.close()
