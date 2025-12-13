"""
Script de Migración: Agregar proveedor_id a productos y repuestos existentes
Fecha: 2025
Descripción: Actualiza la base de datos para el nuevo sistema de pedidos con proveedores obligatorios
"""

import sqlite3
import os
from pathlib import Path

def migrar_proveedores():
    """Migra productos y repuestos existentes agregando proveedor_id=0 (sin proveedor)"""
    
    # Buscar la base de datos en posibles ubicaciones
    posibles_rutas = [
        Path(__file__).parent / "servitec_manager.db",
        Path(__file__).parent.parent / "servitec_manager.db",
        Path.cwd() / "servitec_manager.db",
    ]
    
    db_path = None
    for ruta in posibles_rutas:
        if ruta.exists():
            db_path = ruta
            break
    
    if not db_path:
        print("❌ Error: No se encontró la base de datos servitec_manager.db")
        print(f"   Buscado en:")
        for ruta in posibles_rutas:
            print(f"   - {ruta}")
        print("\n💡 Ejecute el programa principal primero para crear la base de datos")
        return False
    
    print(f"📊 Conectando a: {db_path}")
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Verificar si ya existe la columna proveedor_id
        cursor.execute("PRAGMA table_info(inventario)")
        columnas_inv = [col[1] for col in cursor.fetchall()]
        
        cursor.execute("PRAGMA table_info(repuestos)")
        columnas_rep = [col[1] for col in cursor.fetchall()]
        
        migracion_necesaria = False
        
        # MIGRACIÓN DE INVENTARIO
        if 'proveedor_id' not in columnas_inv:
            print("\n🔧 Migrando tabla INVENTARIO...")
            print("   ➤ Agregando columna proveedor_id...")
            
            # SQLite no permite ALTER TABLE ADD COLUMN con NOT NULL y sin DEFAULT
            # Por eso creamos la columna sin NOT NULL primero
            cursor.execute("ALTER TABLE inventario ADD COLUMN proveedor_id INTEGER DEFAULT 0")
            
            # Crear índice para mejor rendimiento
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_inventario_proveedor ON inventario(proveedor_id)")
            
            # Contar productos actualizados
            cursor.execute("SELECT COUNT(*) FROM inventario")
            total_productos = cursor.fetchone()[0]
            
            print(f"   ✅ {total_productos} productos actualizados con proveedor_id=0")
            migracion_necesaria = True
        else:
            print("\n✓ Tabla INVENTARIO ya tiene proveedor_id")
        
        # MIGRACIÓN DE REPUESTOS
        if 'proveedor_id' not in columnas_rep:
            print("\n🔧 Migrando tabla REPUESTOS...")
            print("   ➤ Agregando columna proveedor_id...")
            
            cursor.execute("ALTER TABLE repuestos ADD COLUMN proveedor_id INTEGER DEFAULT 0")
            
            # Crear índice
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_repuestos_proveedor ON repuestos(proveedor_id)")
            
            cursor.execute("SELECT COUNT(*) FROM repuestos")
            total_repuestos = cursor.fetchone()[0]
            
            print(f"   ✅ {total_repuestos} repuestos actualizados con proveedor_id=0")
            migracion_necesaria = True
        else:
            print("\n✓ Tabla REPUESTOS ya tiene proveedor_id")
        
        # Verificar si existe la tabla pedidos
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pedidos'")
        tabla_pedidos_existe = cursor.fetchone() is not None
        
        if not tabla_pedidos_existe:
            print("\n🔧 Creando tabla PEDIDOS...")
            cursor.execute("""
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
            """)
            
            # Índices para pedidos
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_pedidos_proveedor ON pedidos(proveedor_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_pedidos_estado ON pedidos(estado)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_pedidos_orden ON pedidos(orden_id)")
            
            print("   ✅ Tabla PEDIDOS creada correctamente")
            migracion_necesaria = True
        else:
            print("\n✓ Tabla PEDIDOS ya existe")
        
        # Commit de cambios
        if migracion_necesaria:
            conn.commit()
            print("\n" + "="*60)
            print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
            print("="*60)
            print("\n📋 PRÓXIMOS PASOS:")
            print("   1. Al crear productos/repuestos ahora DEBE seleccionar un proveedor")
            print("   2. Registros existentes tienen proveedor_id=0 (SIN PROVEEDOR)")
            print("   3. Edite cada producto/repuesto para asignar un proveedor válido")
            print("   4. Sistema de pedidos disponible en el módulo correspondiente")
        else:
            print("\n✓ No se requirieron cambios - Base de datos ya actualizada")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"\n❌ Error en la migración: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        return False


if __name__ == "__main__":
    print("="*60)
    print("🔄 MIGRACIÓN: Sistema de Pedidos con Proveedores")
    print("="*60)
    print("\nEste script:")
    print("  • Agrega proveedor_id a tablas inventario y repuestos")
    print("  • Crea tabla pedidos si no existe")
    print("  • Configura índices para mejor rendimiento")
    print("\n⚠️  IMPORTANTE: Se recomienda hacer backup de la BD antes de continuar")
    print("="*60)
    
    respuesta = input("\n¿Desea continuar con la migración? (s/n): ").lower()
    
    if respuesta == 's':
        print("\n🚀 Iniciando migración...\n")
        exito = migrar_proveedores()
        if exito:
            print("\n✅ Proceso finalizado correctamente")
        else:
            print("\n❌ La migración falló - revise los errores anteriores")
    else:
        print("\n❌ Migración cancelada por el usuario")
