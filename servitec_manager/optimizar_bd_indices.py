"""
Script para optimizar la base de datos aplicando índices y configuraciones
Ejecutar este script después de actualizar el código para mejorar el rendimiento
"""

import sqlite3
import os

def optimizar_base_datos(ruta_bd="SERVITEC.DB"):
    """Aplica índices y optimizaciones a la base de datos existente"""
    
    if not os.path.exists(ruta_bd):
        print(f"❌ Base de datos no encontrada: {ruta_bd}")
        return False
    
    print(f"🔧 Optimizando base de datos: {ruta_bd}")
    
    # Índices críticos para mejorar el rendimiento
    indices = [
        "CREATE INDEX IF NOT EXISTS idx_clientes_rut ON clientes(rut)",
        "CREATE INDEX IF NOT EXISTS idx_clientes_nombre ON clientes(nombre)",
        "CREATE INDEX IF NOT EXISTS idx_ordenes_cliente ON ordenes(cliente_id)",
        "CREATE INDEX IF NOT EXISTS idx_ordenes_estado ON ordenes(estado)",
        "CREATE INDEX IF NOT EXISTS idx_ordenes_fecha ON ordenes(fecha)",
        "CREATE INDEX IF NOT EXISTS idx_ordenes_tecnico ON ordenes(tecnico_id)",
        "CREATE INDEX IF NOT EXISTS idx_finanzas_orden ON finanzas(orden_id)",
        "CREATE INDEX IF NOT EXISTS idx_ventas_usuario ON ventas(usuario_id)",
        "CREATE INDEX IF NOT EXISTS idx_ventas_fecha ON ventas(fecha)",
        "CREATE INDEX IF NOT EXISTS idx_detalle_ventas_venta ON detalle_ventas(venta_id)",
        "CREATE INDEX IF NOT EXISTS idx_precios_proveedor_repuesto ON precios_proveedor(repuesto_id)",
        "CREATE INDEX IF NOT EXISTS idx_precios_proveedor_proveedor ON precios_proveedor(proveedor_id)",
        "CREATE INDEX IF NOT EXISTS idx_compras_proveedor ON compras(proveedor_id)",
        "CREATE INDEX IF NOT EXISTS idx_compras_fecha ON compras(fecha)",
        "CREATE INDEX IF NOT EXISTS idx_detalle_compras_compra ON detalle_compras(compra_id)",
        "CREATE INDEX IF NOT EXISTS idx_pagos_proveedor_proveedor ON pagos_proveedor(proveedor_id)",
        "CREATE INDEX IF NOT EXISTS idx_gastos_sesion ON gastos(sesion_id)",
        "CREATE INDEX IF NOT EXISTS idx_caja_sesiones_usuario ON caja_sesiones(usuario_id)",
        "CREATE INDEX IF NOT EXISTS idx_modelos_lookup ON modelos(tipo_dispositivo, marca)",
        # ÍNDICES CRÍTICOS PARA INVENTARIO Y REPUESTOS (SOLUCIONA EL CONGELAMIENTO)
        "CREATE INDEX IF NOT EXISTS idx_inventario_nombre ON inventario(nombre)",
        "CREATE INDEX IF NOT EXISTS idx_inventario_categoria ON inventario(categoria)",
        "CREATE INDEX IF NOT EXISTS idx_repuestos_nombre ON repuestos(nombre)",
        "CREATE INDEX IF NOT EXISTS idx_repuestos_categoria ON repuestos(categoria)",
        "CREATE INDEX IF NOT EXISTS idx_servicios_nombre ON servicios_predefinidos(nombre_servicio)"
    ]
    
    try:
        with sqlite3.connect(ruta_bd) as conexion:
            cursor = conexion.cursor()
            
            print("📊 Aplicando configuraciones de optimización...")
            
            # Configuraciones de optimización
            cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
            cursor.execute("PRAGMA synchronous=NORMAL")  # Balance velocidad/seguridad
            cursor.execute("PRAGMA cache_size=-64000")  # Cache de 64MB
            cursor.execute("PRAGMA temp_store=MEMORY")  # Tablas temporales en memoria
            cursor.execute("PRAGMA mmap_size=268435456")  # Memory-mapped I/O de 256MB
            
            print("📇 Creando índices...")
            indices_creados = 0
            for idx, indice in enumerate(indices, 1):
                try:
                    cursor.execute(indice)
                    indices_creados += 1
                    print(f"  ✓ [{idx}/{len(indices)}] Índice creado")
                except sqlite3.Error as e:
                    print(f"  ⚠ [{idx}/{len(indices)}] Error: {e}")
            
            print("🔍 Actualizando estadísticas del optimizador...")
            cursor.execute("ANALYZE")
            
            print("🧹 Limpiando y compactando base de datos...")
            cursor.execute("VACUUM")
            
            conexion.commit()
            
            print(f"\n✅ Optimización completada!")
            print(f"   - {indices_creados}/{len(indices)} índices aplicados")
            print(f"   - Base de datos optimizada y compactada")
            
            # Mostrar estadísticas
            cursor.execute("SELECT COUNT(*) FROM inventario")
            total_inv = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM repuestos")
            total_rep = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM ordenes")
            total_ord = cursor.fetchone()[0]
            
            print(f"\n📈 Estadísticas:")
            print(f"   - Productos en inventario: {total_inv}")
            print(f"   - Repuestos: {total_rep}")
            print(f"   - Órdenes: {total_ord}")
            
            return True
            
    except sqlite3.Error as e:
        print(f"❌ Error al optimizar la base de datos: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("  OPTIMIZADOR DE BASE DE DATOS - SERVITEC MANAGER")
    print("="*60)
    print()
    
    success = optimizar_base_datos()
    
    if success:
        print("\n🎉 La base de datos ha sido optimizada correctamente.")
        print("   El inventario y las búsquedas ahora serán mucho más rápidas.")
    else:
        print("\n⚠ No se pudo completar la optimización.")
    
    print("\nPresione ENTER para salir...")
    input()
