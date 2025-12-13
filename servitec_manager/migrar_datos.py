"""
Script para migrar datos desde una base de datos existente a la nueva instalación
"""

import sqlite3
import os
from datetime import datetime

DB_ORIGEN = "SERVITEC_ORIGEN.DB"
DB_DESTINO = "SERVITEC.DB"

def analizar_db_origen():
    """Analizar la estructura de la base de datos de origen"""
    print("="*70)
    print("  ANALIZANDO BASE DE DATOS DE ORIGEN")
    print("="*70)
    
    if not os.path.exists(DB_ORIGEN):
        print(f"\n❌ ERROR: No se encuentra {DB_ORIGEN}")
        return None
    
    conn = sqlite3.connect(DB_ORIGEN)
    cursor = conn.cursor()
    
    # Obtener lista de tablas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tablas = [row[0] for row in cursor.fetchall()]
    
    print(f"\n📊 Tablas encontradas: {len(tablas)}\n")
    
    datos = {}
    for tabla in tablas:
        cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
        count = cursor.fetchone()[0]
        print(f"  • {tabla}: {count} registros")
        
        # Obtener estructura de columnas
        cursor.execute(f"PRAGMA table_info({tabla})")
        columnas = [col[1] for col in cursor.fetchall()]
        
        # Obtener todos los datos
        cursor.execute(f"SELECT * FROM {tabla}")
        registros = cursor.fetchall()
        
        datos[tabla] = {
            'columnas': columnas,
            'registros': registros,
            'count': count
        }
    
    conn.close()
    return datos

def migrar_datos(datos_origen):
    """Migrar datos de la base de origen a la destino"""
    
    print("\n" + "="*70)
    print("  INICIANDO MIGRACIÓN DE DATOS")
    print("="*70 + "\n")
    
    # Crear nueva base de datos
    if os.path.exists(DB_DESTINO):
        print(f"⚠️  {DB_DESTINO} ya existe. Se sobrescribirá.")
        os.remove(DB_DESTINO)
    
    conn_destino = sqlite3.connect(DB_DESTINO)
    cursor_destino = conn_destino.cursor()
    
    # Primero crear las tablas usando la estructura existente
    conn_origen = sqlite3.connect(DB_ORIGEN)
    cursor_origen = conn_origen.cursor()
    
    # Obtener los CREATE TABLE statements
    cursor_origen.execute("SELECT sql FROM sqlite_master WHERE type='table'")
    creates = cursor_origen.fetchall()
    
    print("📝 Creando estructura de base de datos...")
    for create in creates:
        if create[0]:
            try:
                cursor_destino.execute(create[0])
            except Exception as e:
                print(f"  ⚠️  Error creando tabla: {e}")
    
    conn_destino.commit()
    
    # Ahora insertar los datos
    total_migrado = 0
    
    for tabla, info in datos_origen.items():
        if info['count'] > 0:
            columnas = info['columnas']
            registros = info['registros']
            
            placeholders = ','.join(['?' for _ in columnas])
            cols_str = ','.join(columnas)
            
            try:
                cursor_destino.executemany(
                    f"INSERT INTO {tabla} ({cols_str}) VALUES ({placeholders})",
                    registros
                )
                print(f"✓ {tabla}: {info['count']} registros migrados")
                total_migrado += info['count']
            except Exception as e:
                print(f"❌ Error migrando {tabla}: {e}")
    
    conn_destino.commit()
    conn_origen.close()
    conn_destino.close()
    
    print(f"\n{'='*70}")
    print(f"  ✓ MIGRACIÓN COMPLETADA - {total_migrado} REGISTROS TOTALES")
    print(f"{'='*70}\n")
    
    return total_migrado

def generar_reporte(datos_origen):
    """Generar reporte de la migración"""
    
    print("\n📋 RESUMEN DE DATOS MIGRADOS:\n")
    
    tablas_principales = ['usuarios', 'clientes', 'ordenes', 'productos', 
                          'proveedores', 'finanzas', 'ventas']
    
    for tabla in tablas_principales:
        if tabla in datos_origen:
            count = datos_origen[tabla]['count']
            if count > 0:
                print(f"  • {tabla.upper()}: {count}")
    
    print()

def main():
    """Proceso principal de migración"""
    
    print("\n" + "="*70)
    print("  MIGRADOR DE DATOS - SERVITECMANAGER")
    print("  Versión 1.0")
    print("="*70 + "\n")
    
    # 1. Analizar base de datos de origen
    datos = analizar_db_origen()
    
    if datos is None:
        return
    
    # 2. Confirmar migración
    print("\n" + "-"*70)
    respuesta = input("¿Desea continuar con la migración? (S/N): ").strip().upper()
    
    if respuesta != 'S':
        print("\n❌ Migración cancelada por el usuario.\n")
        return
    
    # 3. Migrar datos
    total = migrar_datos(datos)
    
    # 4. Generar reporte
    generar_reporte(datos)
    
    print(f"📁 Base de datos creada: {DB_DESTINO}")
    print(f"📊 Total de registros: {total}")
    print(f"✅ La base de datos está lista para usarse con ServitecManager.exe\n")

if __name__ == "__main__":
    try:
        main()
        input("\nPresione ENTER para cerrar...")
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        input("\nPresione ENTER para cerrar...")
