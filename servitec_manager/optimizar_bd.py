"""
Script para optimizar la base de datos SERVITEC.DB
Ejecuta mantenimiento y optimizaciones para mejorar el rendimiento
"""
import sqlite3
import os

def optimizar_base_datos(ruta_bd="SERVITEC.DB"):
    """Optimiza la base de datos existente"""
    if not os.path.exists(ruta_bd):
        print(f"❌ No se encontró la base de datos: {ruta_bd}")
        return
    
    print(f"🔧 Optimizando base de datos: {ruta_bd}")
    
    try:
        conn = sqlite3.connect(ruta_bd)
        cursor = conn.cursor()
        
        print("📊 Aplicando configuraciones de rendimiento...")
        # Configuraciones de rendimiento
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=-64000")
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.execute("PRAGMA mmap_size=268435456")
        
        print("📈 Creando índices optimizados...")
        # Crear índices si no existen
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
            "CREATE INDEX IF NOT EXISTS idx_modelos_lookup ON modelos(tipo_dispositivo, marca)"
        ]
        
        for indice in indices:
            cursor.execute(indice)
        
        print("🔍 Analizando estadísticas...")
        cursor.execute("ANALYZE")
        
        print("🧹 Compactando base de datos...")
        cursor.execute("VACUUM")
        
        conn.commit()
        conn.close()
        
        # Mostrar tamaño de la BD
        tamaño = os.path.getsize(ruta_bd) / (1024 * 1024)
        print(f"✅ Optimización completada!")
        print(f"📦 Tamaño de la base de datos: {tamaño:.2f} MB")
        
    except Exception as e:
        print(f"❌ Error durante la optimización: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("OPTIMIZADOR DE BASE DE DATOS SERVITEC")
    print("=" * 60)
    optimizar_base_datos()
    print("=" * 60)
    input("Presiona ENTER para salir...")
