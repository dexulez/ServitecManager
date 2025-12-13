"""
Script para cargar datos de prueba en ServitecManager
Ejecutar este script para poblar la base de datos con datos de ejemplo
"""

import sqlite3
from datetime import datetime, timedelta
import os

DB_NAME = "SERVITEC.DB"

def crear_conexion():
    """Crear conexión a la base de datos"""
    return sqlite3.connect(DB_NAME)

def poblar_base_datos():
    """Poblar la base de datos con datos de prueba"""
    
    print("="*60)
    print("  CARGANDO DATOS DE PRUEBA EN SERVITECMANAGER")
    print("="*60)
    print()
    
    conn = crear_conexion()
    cursor = conn.cursor()
    
    # 1. USUARIOS
    print("✓ Creando usuarios...")
    usuarios = [
        ("admin", "admin123", "Administrador", 1),
        ("tecnico1", "tec123", "Juan Técnico", 0),
        ("tecnico2", "tec123", "María Soporte", 0),
    ]
    
    cursor.execute("DELETE FROM usuarios")
    cursor.executemany("""
        INSERT INTO usuarios (usuario, password, nombre, es_admin)
        VALUES (?, ?, ?, ?)
    """, usuarios)
    
    # 2. CLIENTES
    print("✓ Creando clientes...")
    clientes = [
        ("Juan Pérez González", "18.234.567-8", "+56 9 8765 4321", "juan.perez@email.com", "Av. Principal 123, Santiago"),
        ("María López Fernández", "17.456.789-0", "+56 9 7654 3210", "maria.lopez@email.com", "Calle Los Pinos 456"),
        ("Carlos Rodríguez Silva", "19.123.456-7", "+56 9 6543 2109", "carlos.rodriguez@email.com", "Pasaje Las Flores 789"),
        ("Ana Martínez Torres", "16.987.654-3", "+56 9 5432 1098", "ana.martinez@email.com", "Av. Libertad 321"),
        ("Pedro Sánchez Muñoz", "20.345.678-9", "+56 9 4321 0987", "pedro.sanchez@email.com", "Los Aromos 654"),
    ]
    
    cursor.execute("DELETE FROM clientes")
    cursor.executemany("""
        INSERT INTO clientes (nombre, rut, telefono, email, direccion)
        VALUES (?, ?, ?, ?, ?)
    """, clientes)
    
    # 3. PROVEEDORES
    print("✓ Creando proveedores...")
    proveedores = [
        ("Repuestos Electrónicos Ltda.", "+56 2 2345 6789", "ventas@repuestos.cl", "Av. Industrial 1000"),
        ("Distribuidora Tech", "+56 2 3456 7890", "contacto@techstore.cl", "Los Cerrillos 500"),
        ("Importadora Mobile Parts", "+56 2 4567 8901", "info@mobileparts.cl", "San Pablo 2000"),
    ]
    
    cursor.execute("DELETE FROM proveedores")
    cursor.executemany("""
        INSERT INTO proveedores (nombre, telefono, email, direccion)
        VALUES (?, ?, ?, ?)
    """, proveedores)
    
    # 4. PRODUCTOS/REPUESTOS
    print("✓ Creando productos...")
    productos = [
        ("Pantalla Samsung A54", "PANTALLA", 45000, 15, 5),
        ("Batería iPhone 13", "BATERIA", 28000, 20, 5),
        ("Cargador USB-C 20W", "ACCESORIO", 8500, 50, 10),
        ("Cable Lightning", "ACCESORIO", 5000, 80, 15),
        ("Pantalla Xiaomi Redmi Note 11", "PANTALLA", 38000, 12, 5),
        ("Batería Samsung S21", "BATERIA", 32000, 18, 5),
        ("Módulo Táctil Motorola G60", "PANTALLA", 35000, 10, 5),
        ("Funda Silicona Universal", "ACCESORIO", 3500, 100, 20),
        ("Vidrio Templado Universal", "ACCESORIO", 2500, 120, 25),
        ("Auriculares Bluetooth", "ACCESORIO", 15000, 30, 8),
    ]
    
    cursor.execute("DELETE FROM productos")
    cursor.executemany("""
        INSERT INTO productos (nombre, categoria, precio_venta, stock_actual, stock_minimo)
        VALUES (?, ?, ?, ?, ?)
    """, productos)
    
    # 5. ÓRDENES DE TRABAJO
    print("✓ Creando órdenes de trabajo...")
    
    # Obtener IDs de clientes
    cursor.execute("SELECT id FROM clientes LIMIT 5")
    cliente_ids = [row[0] for row in cursor.fetchall()]
    
    # Obtener ID del técnico
    cursor.execute("SELECT id FROM usuarios WHERE nombre='Juan Técnico' LIMIT 1")
    tecnico_id = cursor.fetchone()[0]
    
    fecha_base = datetime.now() - timedelta(days=15)
    
    ordenes = []
    for i in range(8):
        cliente_id = cliente_ids[i % len(cliente_ids)]
        fecha = (fecha_base + timedelta(days=i*2)).strftime("%Y-%m-%d %H:%M:%S")
        
        equipos = [
            ("CELULAR MOTOROLA G9 PLUS", "SN2021MG9P001"),
            ("CELULAR SAMSUNG A54", "SN2022SA54002"),
            ("CELULAR IPHONE 13", "SN2021IP13003"),
            ("TABLET SAMSUNG TAB A7", "SN2020STA7004"),
            ("CELULAR XIAOMI REDMI NOTE 11", "SN2022XRN11005"),
        ]
        
        equipo, serie = equipos[i % len(equipos)]
        
        fallas = [
            "PANTALLA ROTA. PRESENTA MANCHAS NEGRAS EN ESQUINA SUPERIOR. TOUCH FUNCIONA PARCIALMENTE.",
            "BATERÍA NO CARGA. EQUIPO SE APAGA AL 30%. PUERTO USB FUNCIONA CORRECTAMENTE.",
            "NO ENCIENDE. SE MOJÓ. NECESITA LIMPIEZA Y REVISIÓN DE PLACA.",
            "TOUCH NO RESPONDE EN ZONA INFERIOR. PANTALLA EN BUEN ESTADO.",
            "SPEAKER NO FUNCIONA. MICRÓFONO FUNCIONAL. VIBRADOR OK.",
        ]
        
        falla = fallas[i % len(fallas)]
        
        estados = ["Recibido", "En Diagnóstico", "Esperando Repuesto", "En Reparación", "Listo"]
        estado = estados[min(i, len(estados)-1)]
        
        accesorios = ["BANDEJA SIM", "CARGADOR", "MICRO SD"] if i % 2 == 0 else ["BANDEJA SIM"]
        accesorios_json = ",".join(accesorios)
        
        ordenes.append((
            cliente_id, equipo, serie, fecha, None, falla, estado,
            tecnico_id, accesorios_json, 0, "2025-12-15"
        ))
    
    cursor.execute("DELETE FROM ordenes")
    cursor.executemany("""
        INSERT INTO ordenes (
            cliente_id, equipo, serie_imei, fecha_recepcion, fecha_entrega,
            falla_reportada, estado, tecnico_asignado, accesorios_entregados,
            prioridad, fecha_estimada_entrega
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ordenes)
    
    # 6. FINANZAS (algunas órdenes ya pagadas)
    print("✓ Creando registros financieros...")
    
    cursor.execute("SELECT id FROM ordenes LIMIT 4")
    orden_ids = [row[0] for row in cursor.fetchall()]
    
    finanzas = []
    for orden_id in orden_ids:
        fecha = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S")
        montos = [45000, 35000, 28000, 50000]
        idx = orden_ids.index(orden_id)
        monto = montos[idx % len(montos)]
        
        # Alternar métodos de pago
        if idx % 3 == 0:
            finanzas.append((orden_id, monto, 0, 0, 0, fecha, fecha))
        elif idx % 3 == 1:
            finanzas.append((orden_id, 0, monto, 0, 0, fecha, fecha))
        else:
            finanzas.append((orden_id, 0, 0, monto, 0, fecha, fecha))
    
    cursor.execute("DELETE FROM finanzas")
    cursor.executemany("""
        INSERT INTO finanzas (
            orden_id, monto_efectivo, monto_transferencia, monto_debito,
            monto_credito, fecha_apertura, fecha_cierre
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, finanzas)
    
    # 7. VENTAS POS (algunas ventas directas)
    print("✓ Creando ventas POS...")
    
    ventas = []
    for i in range(5):
        fecha = (datetime.now() - timedelta(days=i*3)).strftime("%Y-%m-%d %H:%M:%S")
        items = [
            "1x Cargador USB-C 20W - $8.500",
            "2x Cable Lightning - $10.000",
            "1x Funda Silicona - $3.500",
            "3x Vidrio Templado - $7.500",
            "1x Auriculares Bluetooth - $15.000",
        ]
        
        totales = [8500, 10000, 3500, 7500, 15000]
        
        if i % 2 == 0:
            ventas.append((fecha, items[i], totales[i], 0, 0, 0))
        else:
            ventas.append((fecha, items[i], 0, totales[i], 0, 0))
    
    cursor.execute("DELETE FROM ventas")
    cursor.executemany("""
        INSERT INTO ventas (
            fecha, items, pago_efectivo, pago_transferencia,
            pago_debito, pago_credito
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, ventas)
    
    # 8. CONFIGURACIÓN DE EMPRESA
    print("✓ Configurando datos de empresa...")
    
    cursor.execute("DELETE FROM configuracion_empresa")
    cursor.execute("""
        INSERT INTO configuracion_empresa (
            nombre, direccion, telefono, email, rut, 
            terminos_condiciones, logo_path
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        "SERVITEC",
        "Av. Principal 1234, Santiago, Chile",
        "+56 2 2345 6789",
        "contacto@servitec.cl",
        "76.543.210-9",
        "1. Garantía de 30 días en reparaciones.\n2. Cliente debe presentar boleta para garantía.\n3. Equipos no retirados en 60 días serán dados de baja.",
        "assets/servitec_logo.png"
    ))
    
    conn.commit()
    conn.close()
    
    print()
    print("="*60)
    print("  ✓ DATOS DE PRUEBA CARGADOS EXITOSAMENTE")
    print("="*60)
    print()
    print("CREDENCIALES DE ACCESO:")
    print("-" * 60)
    print("  Usuario: admin      | Contraseña: admin123")
    print("  Usuario: tecnico1   | Contraseña: tec123")
    print("  Usuario: tecnico2   | Contraseña: tec123")
    print("-" * 60)
    print()
    print("DATOS CREADOS:")
    print(f"  • {len(usuarios)} usuarios")
    print(f"  • {len(clientes)} clientes")
    print(f"  • {len(proveedores)} proveedores")
    print(f"  • {len(productos)} productos")
    print(f"  • {len(ordenes)} órdenes de trabajo")
    print(f"  • {len(finanzas)} registros financieros")
    print(f"  • {len(ventas)} ventas POS")
    print()
    print("Ahora puede iniciar ServitecManager.exe y probar el sistema.")
    print()

if __name__ == "__main__":
    try:
        poblar_base_datos()
        input("\nPresione ENTER para cerrar...")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        input("\nPresione ENTER para cerrar...")
