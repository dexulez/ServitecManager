import sqlite3
import os

db_path = 'servitec_manager/SERVITEC.DB'

print("🧹 Limpiando base de datos...")
print("─" * 60)

try:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Eliminar datos (ignorar errores si tabla no existe)
    tablas = ['ordenes', 'clientes', 'ventas', 'detalle_ventas', 'inventario', 
              'finanzas', 'proveedores', 'pedidos', 'detalle_pedidos', 'caja']
    
    for tabla in tablas:
        try:
            c.execute(f'DELETE FROM {tabla}')
        except:
            pass
    
    try:
        c.execute('DELETE FROM servicios WHERE id > 1')
        c.execute('DELETE FROM repuestos WHERE id > 1')
    except:
        pass
    
    # Reiniciar secuencias
    c.execute('UPDATE sqlite_sequence SET seq = 0 WHERE name IN ("ordenes", "clientes", "ventas", "inventario", "finanzas", "proveedores", "pedidos", "caja")')
    
    conn.commit()
    
    # Verificar
    ordenes = c.execute('SELECT COUNT(*) FROM ordenes').fetchone()[0]
    clientes = c.execute('SELECT COUNT(*) FROM clientes').fetchone()[0]
    usuarios = c.execute('SELECT COUNT(*) FROM usuarios').fetchone()[0]
    
    print('✅ Base de datos limpiada correctamente')
    print()
    print('📊 Registros actuales:')
    print(f'   - Órdenes: {ordenes}')
    print(f'   - Clientes: {clientes}')
    print(f'   - Usuarios: {usuarios} (conservados)')
    
    conn.close()
    
except Exception as e:
    print(f'❌ Error: {e}')
