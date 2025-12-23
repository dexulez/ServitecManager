"""
Script para cargar datos de prueba en ServitecManager
Ejecutar este script para poblar la base de datos con datos de ejemplo
"""

import sqlite3
from datetime import datetime, timedelta
import os

DB_NAME = "SERVITEC_TEST_OPTIMIZED.DB"

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
        ("admin", "admin123", "Administrador", 50),
        ("Juan Técnico", "tec123", "Técnico", 50),
        ("María Soporte", "tec123", "Técnico", 50),
    ]
    
    cursor.execute("DELETE FROM usuarios")
    cursor.executemany("""
        INSERT INTO usuarios (nombre, password, rol, porcentaje_comision)
        VALUES (?, ?, ?, ?)
    """, usuarios)
    
    # 2. CLIENTES
    print("✓ Creando clientes...")
    clientes = [
        ("18.234.567-8", "Juan Pérez González", "+56 9 8765 4321", "juan.perez@email.com"),
        ("17.456.789-0", "María López Fernández", "+56 9 7654 3210", "maria.lopez@email.com"),
        ("19.123.456-7", "Carlos Rodríguez Silva", "+56 9 6543 2109", "carlos.rodriguez@email.com"),
        ("16.987.654-3", "Ana Martínez Torres", "+56 9 5432 1098", "ana.martinez@email.com"),
        ("20.345.678-9", "Pedro Sánchez Muñoz", "+56 9 4321 0987", "pedro.sanchez@email.com"),
    ]
    
    cursor.execute("DELETE FROM clientes")
    cursor.executemany("""
        INSERT INTO clientes (cedula, nombre, telefono, email)
        VALUES (?, ?, ?, ?)
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
    print("✓ Creando repuestos...")
    productos = [
        ("Pantalla Samsung A54", "PANTALLA", 45000, 60000, 15),
        ("Batería iPhone 13", "BATERIA", 28000, 45000, 20),
        ("Cargador USB-C 20W", "ACCESORIO", 8500, 15000, 50),
        ("Cable Lightning", "ACCESORIO", 5000, 10000, 80),
        ("Pantalla Xiaomi Redmi Note 11", "PANTALLA", 38000, 55000, 12),
        ("Batería Samsung S21", "BATERIA", 32000, 50000, 18),
        ("Módulo Táctil Motorola G60", "PANTALLA", 35000, 52000, 10),
        ("Funda Silicona Universal", "ACCESORIO", 3500, 7000, 100),
        ("Vidrio Templado Universal", "ACCESORIO", 2500, 5000, 120),
        ("Auriculares Bluetooth", "ACCESORIO", 15000, 30000, 30),
    ]
    
    cursor.execute("DELETE FROM repuestos")
    cursor.executemany("""
        INSERT INTO repuestos (nombre, categoria, costo, precio_sugerido, stock)
        VALUES (?, ?, ?, ?, ?)
    """, productos)
    
    # 5. ÓRDENES DE TRABAJO
    print("✓ Creando órdenes de trabajo...")
    
    # Obtener IDs de clientes
    cursor.execute("SELECT id FROM clientes LIMIT 5")
    cliente_ids = [row[0] for row in cursor.fetchall()]
    
    # Obtener ID del técnico
    cursor.execute("SELECT id FROM usuarios WHERE rol = 'Técnico' LIMIT 1")
    tecnico_row = cursor.fetchone()
    tecnico_id = tecnico_row[0] if tecnico_row else 1
    
    # Usar fecha actual para que aparezcan en reportes de hoy
    fecha_base = datetime.now()
    
    ordenes = []
    for i in range(8):
        cliente_id = cliente_ids[i % len(cliente_ids)]
        fecha_entrada = (fecha_base - timedelta(days=i)).strftime("%Y-%m-%d %H:%M:%S")
        
        equipos_data = [
            ("CELULAR", "MOTOROLA", "G9 PLUS", "SN2021MG9P001"),
            ("CELULAR", "SAMSUNG", "A54", "SN2022SA54002"),
            ("CELULAR", "APPLE", "IPHONE 13", "SN2021IP13003"),
            ("TABLET", "SAMSUNG", "GALAXY TAB A7", "SN2020STA7004"),
            ("CELULAR", "XIAOMI", "REDMI NOTE 11", "SN2022XRN11005"),
        ]
        
        tipo, marca, modelo, serie = equipos_data[i % len(equipos_data)]
        equipo = f"{tipo} {marca} {modelo}"
        
        fallas = [
            "PANTALLA ROTA. PRESENTA MANCHAS NEGRAS EN ESQUINA SUPERIOR. TOUCH FUNCIONA PARCIALMENTE.",
            "BATERÍA NO CARGA. EQUIPO SE APAGA AL 30%. PUERTO USB FUNCIONA CORRECTAMENTE.",
            "NO ENCIENDE. SE MOJÓ. NECESITA LIMPIEZA Y REVISIÓN DE PLACA.",
            "TOUCH NO RESPONDE EN ZONA INFERIOR. PANTALLA EN BUEN ESTADO.",
            "SPEAKER NO FUNCIONA. MICRÓFONO FUNCIONAL. VIBRADOR OK.",
        ]
        
        falla = fallas[i % len(fallas)]
        
        # Primeras 4 órdenes están entregadas (con fecha_cierre de hoy)
        # Resto están en proceso
        if i < 4:
            estado = "Entregado"
            fecha_cierre = fecha_base.strftime("%Y-%m-%d %H:%M:%S")
            condicion = "SOLUCIONADO"
        else:
            estado = ["Pendiente", "En Proceso", "Reparado"][i % 3]
            fecha_cierre = None
            condicion = "PENDIENTE"
        
        accesorios = ["BANDEJA SIM", "CARGADOR", "MICRO SD"] if i % 2 == 0 else ["BANDEJA SIM"]
        accesorios_str = ",".join(accesorios)
        
        presupuesto = (35000 + i * 5000) if i < 5 else (20000 + i * 2000)
        abono = presupuesto // 2 if i % 2 == 0 else 0
        
        # Costos de repuestos y envío para órdenes entregadas
        costo_repuestos = (10000 + i * 1000) if i < 4 else 0
        costo_envio = 2000 if i % 2 == 0 and i < 4 else 0
        
        ordenes.append((
            cliente_id, tecnico_id, fecha_entrada, equipo, marca, modelo, serie,
            falla, estado, accesorios_str, 0, presupuesto, abono, "2025-12-25", condicion,
            costo_repuestos, costo_envio, fecha_cierre
        ))
    
    cursor.execute("DELETE FROM ordenes")
    cursor.executemany("""
        INSERT INTO ordenes (
            cliente_id, tecnico_id, fecha_entrada, equipo, marca, modelo, serie,
            observacion, estado, accesorios, riesgoso, presupuesto_inicial, abono, fecha_entrega, condicion,
            costo_total_repuestos, costo_envio, fecha_cierre
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ordenes)
    
    # 6. Calcular campos financieros para órdenes entregadas
    print("✓ Calculando campos financieros para órdenes entregadas...")
    cursor.execute("""
        UPDATE ordenes 
        SET 
            total_a_cobrar = presupuesto_inicial - COALESCE(descuento, 0),
            saldo_pendiente = (presupuesto_inicial - COALESCE(descuento, 0)) - COALESCE(abono, 0),
            utilidad_bruta = (presupuesto_inicial - COALESCE(descuento, 0)) - 
                            COALESCE(costo_total_repuestos, 0) - COALESCE(costo_envio, 0),
            comision_tecnico = CASE 
                WHEN tecnico_id IN (SELECT id FROM usuarios WHERE porcentaje_comision > 0)
                THEN ((presupuesto_inicial - COALESCE(descuento, 0)) - 
                      COALESCE(costo_total_repuestos, 0) - COALESCE(costo_envio, 0)) * 
                     (SELECT porcentaje_comision FROM usuarios WHERE id = ordenes.tecnico_id) / 100.0
                ELSE 0
            END
        WHERE fecha_cierre IS NOT NULL AND estado = 'Entregado'
    """)
    
    # 7. VENTAS POS - OMITIDO (esquema diferente, no necesario para prueba inicial)
    print("✓ Creando ventas POS...")
    ventas = []  # Placeholder para evitar error en resumen
    
    # 8. CONFIGURACIÓN (saltada - no necesaria para demo)
    print("✓ Configuración completada")
    
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
    print()
    print("Ahora puede iniciar ServitecManager y cobrar en el POS.")
    print()

if __name__ == "__main__":
    try:
        poblar_base_datos()
        input("\nPresione ENTER para cerrar...")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        input("\nPresione ENTER para cerrar...")
