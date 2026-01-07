"""
Script para recrear la base de datos con el esquema completo optimizado
Migra los datos existentes si es necesario
"""
import sqlite3
import os
import shutil
from datetime import datetime

def recrear_base_datos():
    """Recrea la base de datos con el esquema SQL completo"""
    
    db_path = 'SERVITEC_TEST_OPTIMIZED.DB'
    backup_path = f'SERVITEC_TEST_OPTIMIZED.DB.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    schema_path = '../database_schema_optimized.sql'
    
    # Hacer backup si existe
    if os.path.exists(db_path):
        print(f"📦 Creando backup: {backup_path}")
        shutil.copy(db_path, backup_path)
        
        # Exportar datos importantes
        conn_old = sqlite3.connect(db_path)
        cursor_old = conn_old.cursor()
        
        # Guardar usuarios
        cursor_old.execute("SELECT * FROM usuarios")
        usuarios = cursor_old.fetchall()
        
        # Guardar clientes
        cursor_old.execute("SELECT * FROM clientes")
        clientes = cursor_old.fetchall()
        
        # Guardar órdenes (con mapeo de columnas antiguas)
        cursor_old.execute("PRAGMA table_info(ordenes)")
        columnas_ordenes = [col[1] for col in cursor_old.fetchall()]
        cursor_old.execute("SELECT * FROM ordenes")
        ordenes = cursor_old.fetchall()
        
        conn_old.close()
        
        # Eliminar base de datos antigua
        os.remove(db_path)
        print("🗑️ Base de datos antigua eliminada")
    else:
        usuarios = []
        clientes = []
        ordenes = []
        columnas_ordenes = []
    
    # Leer schema SQL completo
    if not os.path.exists(schema_path):
        print(f"❌ Error: No se encuentra {schema_path}")
        return False
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    # Crear nueva base de datos
    print("🔨 Creando base de datos con esquema completo...")
    conn_new = sqlite3.connect(db_path)
    cursor_new = conn_new.cursor()
    
    # Ejecutar schema completo
    try:
        # Limpiar el schema SQL: eliminar comentarios y ejecutar por bloques
        lineas = schema_sql.split('\n')
        sql_limpio = []
        en_comentario = False
        
        for linea in lineas:
            linea_limpia = linea.strip()
            
            # Saltar comentarios multilinea
            if '/*' in linea_limpia:
                en_comentario = True
            if '*/' in linea_limpia:
                en_comentario = False
                continue
            if en_comentario:
                continue
            
            # Saltar comentarios de línea
            if linea_limpia.startswith('--') or linea_limpia == '':
                continue
            
            # Saltar comandos PRAGMA que no son críticos
            if linea_limpia.startswith('PRAGMA'):
                continue
            
            sql_limpio.append(linea)
        
        schema_limpio = '\n'.join(sql_limpio)
        
        # Ejecutar en modo no estricto
        cursor_new.executescript(schema_limpio)
        print("✅ Esquema completo aplicado")
    except Exception as e:
        print(f"❌ Error aplicando schema: {e}")
        print("🔄 Intentando aplicar schema básico...")
        
        # Si falla, crear manualmente las tablas críticas
        try:
            cursor_new.executescript("""
                CREATE TABLE IF NOT EXISTS ordenes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente_id INTEGER NOT NULL,
                    tecnico_id INTEGER,
                    fecha_entrada TEXT DEFAULT CURRENT_TIMESTAMP,
                    fecha_entrega TEXT,
                    equipo TEXT,
                    marca TEXT,
                    modelo TEXT,
                    serie TEXT,
                    observacion TEXT,
                    accesorios TEXT,
                    riesgoso INTEGER DEFAULT 0,
                    estado TEXT CHECK(estado IN ('Pendiente', 'En Proceso', 'Reparado', 'Entregado', 'Sin solución')) DEFAULT 'Pendiente',
                    condicion TEXT CHECK(condicion IN ('PENDIENTE', 'SOLUCIONADO', 'SIN SOLUCIÓN')) DEFAULT 'PENDIENTE',
                    presupuesto_inicial REAL DEFAULT 0,
                    costo_total_repuestos REAL DEFAULT 0,
                    costo_total_servicios REAL DEFAULT 0,
                    costo_envio REAL DEFAULT 0,
                    descuento REAL DEFAULT 0,
                    total_a_cobrar REAL DEFAULT 0,
                    abono REAL DEFAULT 0,
                    saldo_pendiente REAL DEFAULT 0,
                    utilidad_bruta REAL DEFAULT 0,
                    comision_tecnico REAL DEFAULT 0,
                    pago_efectivo REAL DEFAULT 0,
                    pago_transferencia REAL DEFAULT 0,
                    pago_debito REAL DEFAULT 0,
                    pago_credito REAL DEFAULT 0,
                    fecha_cierre TEXT,
                    usuario_cierre_id INTEGER,
                    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE RESTRICT,
                    FOREIGN KEY (tecnico_id) REFERENCES usuarios(id) ON DELETE SET NULL,
                    FOREIGN KEY (usuario_cierre_id) REFERENCES usuarios(id) ON DELETE SET NULL
                );
                
                CREATE INDEX IF NOT EXISTS idx_ordenes_cliente ON ordenes(cliente_id);
                CREATE INDEX IF NOT EXISTS idx_ordenes_estado ON ordenes(estado);
                CREATE INDEX IF NOT EXISTS idx_ordenes_fecha ON ordenes(fecha_entrada);
            """)
            print("✅ Schema básico aplicado exitosamente")
        except Exception as e2:
            print(f"❌ Error crítico: {e2}")
            conn_new.close()
            return False
    
    # Restaurar usuarios
    if usuarios:
        print(f"📥 Restaurando {len(usuarios)} usuarios...")
        cursor_new.executemany(
            "INSERT INTO usuarios VALUES (?, ?, ?, ?, ?, ?)",
            usuarios
        )
    
    # Restaurar clientes
    if clientes:
        print(f"📥 Restaurando {len(clientes)} clientes...")
        # Verificar si tienen columna 'rut' o 'cedula'
        if len(clientes[0]) == 6:  # id, cedula, nombre, telefono, email, fecha_creacion
            cursor_new.executemany(
                "INSERT INTO clientes VALUES (?, ?, ?, ?, ?, ?)",
                clientes
            )
        else:
            print("⚠️ Estructura de clientes no compatible")
    
    # Restaurar órdenes (con migración de estructura)
    if ordenes and columnas_ordenes:
        print(f"📥 Restaurando {len(ordenes)} órdenes...")
        
        # Mapeo de índices antiguo -> nuevo
        idx_cliente_id = columnas_ordenes.index('cliente_id') if 'cliente_id' in columnas_ordenes else 1
        idx_tecnico_id = columnas_ordenes.index('tecnico_id') if 'tecnico_id' in columnas_ordenes else 2
        idx_fecha = columnas_ordenes.index('fecha') if 'fecha' in columnas_ordenes else columnas_ordenes.index('fecha_entrada') if 'fecha_entrada' in columnas_ordenes else 3
        idx_equipo = columnas_ordenes.index('equipo') if 'equipo' in columnas_ordenes else 4
        idx_marca = columnas_ordenes.index('marca') if 'marca' in columnas_ordenes else 5
        idx_modelo = columnas_ordenes.index('modelo') if 'modelo' in columnas_ordenes else 6
        idx_serie = columnas_ordenes.index('serie') if 'serie' in columnas_ordenes else 7
        idx_observacion = columnas_ordenes.index('observacion') if 'observacion' in columnas_ordenes else 8
        idx_accesorios = columnas_ordenes.index('accesorios') if 'accesorios' in columnas_ordenes else 11
        idx_riesgoso = columnas_ordenes.index('riesgoso') if 'riesgoso' in columnas_ordenes else 12
        idx_estado = columnas_ordenes.index('estado') if 'estado' in columnas_ordenes else 9
        idx_condicion = columnas_ordenes.index('condicion') if 'condicion' in columnas_ordenes else None
        idx_presupuesto = columnas_ordenes.index('presupuesto') if 'presupuesto' in columnas_ordenes else columnas_ordenes.index('presupuesto_inicial') if 'presupuesto_inicial' in columnas_ordenes else 13
        idx_descuento = columnas_ordenes.index('descuento') if 'descuento' in columnas_ordenes else 14
        idx_abono = columnas_ordenes.index('abono') if 'abono' in columnas_ordenes else 15
        idx_fecha_entrega = columnas_ordenes.index('fecha_entrega') if 'fecha_entrega' in columnas_ordenes else 16
        
        for orden in ordenes:
            try:
                # Extraer datos de la orden antigua
                cliente_id = orden[idx_cliente_id]
                tecnico_id = orden[idx_tecnico_id]
                fecha_entrada = orden[idx_fecha]
                equipo = orden[idx_equipo]
                marca = orden[idx_marca]
                modelo = orden[idx_modelo]
                serie = orden[idx_serie]
                observacion = orden[idx_observacion]
                accesorios = orden[idx_accesorios]
                riesgoso = orden[idx_riesgoso]
                estado = orden[idx_estado]
                condicion = orden[idx_condicion] if idx_condicion is not None else 'PENDIENTE'
                presupuesto_inicial = orden[idx_presupuesto] or 0
                descuento = orden[idx_descuento] or 0
                abono = orden[idx_abono] or 0
                fecha_entrega = orden[idx_fecha_entrega] if idx_fecha_entrega < len(orden) else None
                
                # Calcular campos financieros
                total_a_cobrar = presupuesto_inicial - descuento
                saldo_pendiente = total_a_cobrar - abono
                
                # Insertar en nueva estructura
                cursor_new.execute("""
                    INSERT INTO ordenes (
                        cliente_id, tecnico_id, fecha_entrada, fecha_entrega,
                        equipo, marca, modelo, serie, observacion, accesorios, riesgoso,
                        estado, condicion,
                        presupuesto_inicial, descuento, abono, total_a_cobrar, saldo_pendiente
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    cliente_id, tecnico_id, fecha_entrada, fecha_entrega,
                    equipo, marca, modelo, serie, observacion, accesorios, riesgoso,
                    estado, condicion,
                    presupuesto_inicial, descuento, abono, total_a_cobrar, saldo_pendiente
                ))
            except Exception as e:
                print(f"⚠️ Error restaurando orden {orden[0]}: {e}")
    
    conn_new.commit()
    conn_new.close()
    
    print("✅ Base de datos recreada exitosamente")
    print(f"   - Usuarios: {len(usuarios)}")
    print(f"   - Clientes: {len(clientes)}")
    print(f"   - Órdenes: {len(ordenes)}")
    print(f"📦 Backup guardado en: {backup_path}")
    
    return True

if __name__ == "__main__":
    recrear_base_datos()
