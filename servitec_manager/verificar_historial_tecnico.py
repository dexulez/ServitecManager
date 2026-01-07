#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de verificación: Órdenes cerradas para Historial por Técnico
"""
import sqlite3
from datetime import datetime

DB_PATH = "SERVITEC_TEST_OPTIMIZED.DB"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("VERIFICACIÓN: ÓRDENES CERRADAS PARA HISTORIAL POR TÉCNICO")
    print("="*80)
    
    # Verificar técnicos
    cursor.execute("SELECT id, nombre, porcentaje_comision FROM usuarios WHERE rol = 'Técnico'")
    tecnicos = cursor.fetchall()
    
    print(f"\n📋 TÉCNICOS REGISTRADOS: {len(tecnicos)}")
    for tec in tecnicos:
        print(f"  • ID: {tec[0]} | Nombre: {tec[1]} | Comisión: {tec[2]}%")
    
    # Verificar órdenes cerradas (las que deben aparecer en historial)
    cursor.execute("""
        SELECT 
            o.id, o.equipo, o.estado, o.fecha_entrada, o.fecha_cierre,
            o.presupuesto_inicial, o.total_a_cobrar, o.costo_total_repuestos,
            o.costo_envio, o.comision_tecnico, u.nombre
        FROM ordenes o
        LEFT JOIN usuarios u ON o.tecnico_id = u.id
        WHERE o.fecha_cierre IS NOT NULL AND o.estado = 'Entregado'
        ORDER BY o.id
    """)
    
    ordenes_cerradas = cursor.fetchall()
    
    print(f"\n✅ ÓRDENES CERRADAS (APARECEN EN HISTORIAL): {len(ordenes_cerradas)}")
    if ordenes_cerradas:
        print("\n" + "-"*80)
        for orden in ordenes_cerradas:
            print(f"\n  Orden #{orden[0]}: {orden[1]}")
            print(f"    Técnico: {orden[10]}")
            print(f"    Estado: {orden[2]}")
            print(f"    Fecha Entrada: {orden[3]}")
            print(f"    Fecha Cierre: {orden[4]}")
            print(f"    Presupuesto: ${orden[5]:,.0f}")
            print(f"    Total a Cobrar: ${orden[6]:,.0f}")
            print(f"    Costos (Rep+Env): ${orden[7] + orden[8]:,.0f}")
            print(f"    Comisión Técnico: ${orden[9]:,.0f}")
    else:
        print("  ⚠️  No hay órdenes cerradas. Ejecute cargar_datos_prueba.py")
    
    # Verificar órdenes pendientes
    cursor.execute("""
        SELECT COUNT(*) 
        FROM ordenes 
        WHERE fecha_cierre IS NULL OR estado != 'Entregado'
    """)
    pendientes = cursor.fetchone()[0]
    
    print(f"\n📌 ÓRDENES PENDIENTES/EN PROCESO: {pendientes}")
    
    # Rango de fechas para prueba
    hoy = datetime.now().strftime("%Y-%m-%d")
    print(f"\n📅 FECHA ACTUAL: {hoy}")
    print(f"\n💡 CONSEJO: En el módulo de reportes, selecciona:")
    print(f"   - Técnico: {tecnicos[0][1] if tecnicos else 'N/A'}")
    print(f"   - Desde: {hoy}")
    print(f"   - Hasta: {hoy}")
    
    print("\n" + "="*80)
    
    conn.close()

if __name__ == "__main__":
    main()
