import sqlite3

conn = sqlite3.connect('SERVITEC.DB')
cursor = conn.cursor()

# Verificar si ya existe la columna en repuestos
cursor.execute('PRAGMA table_info(repuestos)')
cols = [col[1] for col in cursor.fetchall()]

if 'proveedor_id' not in cols:
    cursor.execute('ALTER TABLE repuestos ADD COLUMN proveedor_id INTEGER DEFAULT 0')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_repuestos_proveedor ON repuestos(proveedor_id)')
    print('✅ Columna proveedor_id agregada a repuestos')
else:
    print('✓ repuestos ya tiene proveedor_id')

# Verificar si ya existe la columna en inventario
cursor.execute('PRAGMA table_info(inventario)')
cols = [col[1] for col in cursor.fetchall()]

if 'proveedor_id' not in cols:
    cursor.execute('ALTER TABLE inventario ADD COLUMN proveedor_id INTEGER DEFAULT 0')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_inventario_proveedor ON inventario(proveedor_id)')
    print('✅ Columna proveedor_id agregada a inventario')
else:
    print('✓ inventario ya tiene proveedor_id')

# Verificar tabla pedidos
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pedidos'")
if not cursor.fetchone():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            orden_id INTEGER,
            producto_id INTEGER,
            repuesto_id INTEGER,
            proveedor_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            estado TEXT DEFAULT 'PENDIENTE',
            fecha_solicitud TEXT,
            fecha_pedido TEXT,
            fecha_recepcion TEXT,
            notas TEXT,
            usuario_solicita TEXT,
            FOREIGN KEY(orden_id) REFERENCES ordenes(id),
            FOREIGN KEY(producto_id) REFERENCES inventario(id),
            FOREIGN KEY(repuesto_id) REFERENCES repuestos(id),
            FOREIGN KEY(proveedor_id) REFERENCES proveedores(id)
        )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_pedidos_proveedor ON pedidos(proveedor_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_pedidos_estado ON pedidos(estado)')
    print('✅ Tabla pedidos creada')
else:
    print('✓ Tabla pedidos ya existe')

conn.commit()
conn.close()
print('\n✅ Migración completada exitosamente')
